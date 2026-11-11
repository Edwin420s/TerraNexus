import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import Device, Measurement, DeviceCommand, AuditLog, IrrigationEvent, IrrigationZone
from app.modules.telemetry.router import validate_sensor_range

logger = logging.getLogger("terranexus.mqtt_consumer")

def process_telemetry_message(topic: str, payload_str: str) -> bool:
    """Parse, validate, and persist device telemetry message received via MQTT."""
    try:
        data = json.loads(payload_str)
        # Topic format: tnx/{org_id}/farm/{farm_id}/device/{device_uid}/telemetry
        parts = topic.split('/')
        device_uid = None
        topic_org = None
        topic_farm = None
        if len(parts) >= 6 and parts[0] == "tnx" and parts[2] == "farm" and parts[4] == "device":
            topic_org = parts[1]
            topic_farm = parts[3]
            device_uid = parts[5]
        
        if not device_uid:
            logger.warning(f"Invalid telemetry topic structure: {topic}")
            return False

        db = SessionLocal()
        try:
            device = db.query(Device).filter(Device.device_uid == device_uid).first()
            if not device or device.provisioning_status not in ("active", "provisioned"):
                logger.warning(f"Rejecting telemetry from unprovisioned/unknown device: {device_uid}")
                return False

            # Verify tenant & farm isolation
            if topic_org and topic_farm:
                if str(device.organisation_id) != topic_org or str(device.farm_id) != topic_farm:
                    logger.warning(f"Telemetry topic mismatch: topic {topic_org}/{topic_farm} does not match device {device.organisation_id}/{device.farm_id}")
                    return False

            # Event-level deduplication
            event_id = data.get("event_id")
            if event_id:
                event_id_str = str(event_id)
                existing = db.query(AuditLog).filter(
                    AuditLog.action == "telemetry_ingest",
                    AuditLog.resource_id == event_id_str
                ).first()
                if existing:
                    logger.info(f"Duplicate MQTT telemetry event_id: {event_id_str}, skipping insertion")
                    return True
            
            observed_at_raw = data.get("observed_at")
            if observed_at_raw:
                try:
                    observed_at = datetime.fromisoformat(observed_at_raw)
                except Exception:
                    observed_at = datetime.now(timezone.utc)
            else:
                observed_at = datetime.now(timezone.utc)

            measurements = data.get("measurements", [])
            for m in measurements:
                m_type = m.get("type") or m.get("measurement_type") or "unknown"
                m_val = float(m.get("value", 0.0))
                m_unit = m.get("unit", "")
                m_depth = float(m.get("depth_cm")) if m.get("depth_cm") is not None else None

                is_valid, quality_score = validate_sensor_range(m_type, m_val)

                rec = Measurement(
                    organisation_id=device.organisation_id,
                    farm_id=device.farm_id,
                    field_id=device.field_id,
                    device_id=device.id,
                    measurement_type=m_type,
                    value=m_val,
                    unit=m_unit,
                    depth_cm=m_depth,
                    observed_at=observed_at,
                    received_at=datetime.now(timezone.utc),
                    quality_score=quality_score,
                    is_valid=is_valid
                )
                db.add(rec)
            
            # Persist live safety telemetry and heartbeat on the device record
            now_utc = datetime.now(timezone.utc)
            device.last_telemetry_at = now_utc
            device.last_heartbeat_at = now_utc
            device.connection_status = "online"
            
            cfg = dict(device.config) if isinstance(device.config, dict) else {}
            if "emergency_stop" in data:
                cfg["emergency_stop_active"] = bool(data["emergency_stop"])
            if "pump_running" in data:
                cfg["pump_running"] = bool(data["pump_running"])
            if "dry_run_fault" in data:
                cfg["dry_run_fault"] = bool(data["dry_run_fault"])
            device.config = cfg

            if "battery" in data:
                device.battery_level_pct = float(data["battery"])

            # Record event in AuditLog for idempotency deduplication
            if event_id:
                audit = AuditLog(
                    organisation_id=device.organisation_id,
                    action="telemetry_ingest",
                    resource_type="event",
                    resource_id=str(event_id),
                    status="success"
                )
                db.add(audit)

            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error processing telemetry message: {e}")
        return False

def process_command_ack_message(topic: str, payload_str: str) -> bool:
    """Process command acknowledgements from devices via MQTT and update actuation state machine."""
    try:
        data = json.loads(payload_str)
        command_id = data.get("command_id")
        if not command_id:
            return False
        
        db = SessionLocal()
        try:
            cmd = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
            if not cmd:
                return False

            raw_status = data.get("status", "acknowledged")
            cmd.status = raw_status
            now = datetime.now(timezone.utc)

            if raw_status in ("acknowledged", "closed_loop_executing", "executing"):
                cmd.acknowledged_at = now
            elif raw_status in ("completed", "failed"):
                cmd.completed_at = now

            if data.get("error"):
                cmd.error_message = data["error"]

            # Hardware feedback drives the actual irrigation event and pump state
            if cmd.payload and "zone_id" in cmd.payload:
                zone_id = cmd.payload["zone_id"]
                zone = db.query(IrrigationZone).filter(IrrigationZone.id == zone_id).first()

                if raw_status in ("executing", "closed_loop_executing"):
                    # Transition event to running upon confirmed hardware actuation
                    event = db.query(IrrigationEvent).filter(
                        IrrigationEvent.irrigation_zone_id == zone_id,
                        IrrigationEvent.status.in_(("dispatched", "requested"))
                    ).order_by(IrrigationEvent.created_at.desc()).first()
                    if event:
                        event.status = "running"
                        event.started_at = now
                    if zone:
                        zone.is_active = True
                        if zone.pump:
                            zone.pump.is_running = True
                            zone.pump.last_started_at = now

                elif raw_status in ("completed", "failed"):
                    # Transition event to completed/aborted upon confirmed hardware stop
                    event = db.query(IrrigationEvent).filter(
                        IrrigationEvent.irrigation_zone_id == zone_id,
                        IrrigationEvent.status.in_(("running", "stopping", "dispatched", "requested"))
                    ).order_by(IrrigationEvent.created_at.desc()).first()
                    if event:
                        event.status = "completed" if raw_status == "completed" else "failed"
                        event.ended_at = now
                        if data.get("error"):
                            event.abort_reason = data["error"]
                    if zone:
                        zone.is_active = False
                        if zone.pump:
                            zone.pump.is_running = False
                            zone.pump.last_stopped_at = now

            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error processing command ack: {e}")
        return False
