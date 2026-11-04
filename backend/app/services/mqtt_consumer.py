import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import Device, Measurement, DeviceCommand

logger = logging.getLogger("terranexus.mqtt_consumer")

def process_telemetry_message(topic: str, payload_str: str) -> bool:
    """Parse, validate, and persist device telemetry message received via MQTT."""
    try:
        data = json.loads(payload_str)
        # Topic format: tnx/{org_id}/farm/{farm_id}/device/{device_uid}/telemetry
        parts = topic.split('/')
        device_uid = None
        if len(parts) >= 6 and parts[0] == "tnx" and parts[4] == "device":
            device_uid = parts[5]
        
        db = SessionLocal()
        try:
            device = None
            if device_uid:
                device = db.query(Device).filter(Device.device_uid == device_uid).first()
            
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

                rec = Measurement(
                    organisation_id=device.organisation_id if device else "a0000000-0000-0000-0000-000000000001",
                    farm_id=device.farm_id if device else "c0000000-0000-0000-0000-000000000001",
                    field_id=device.field_id if device else None,
                    device_id=device.id if device else (device_uid or str(uuid.uuid4())),
                    measurement_type=m_type,
                    value=m_val,
                    unit=m_unit,
                    depth_cm=m_depth,
                    observed_at=observed_at,
                    received_at=datetime.now(timezone.utc),
                    quality_score=1.0,
                    is_valid=True
                )
                db.add(rec)
            
            if device:
                device.last_telemetry_at = datetime.now(timezone.utc)
                device.connection_status = "online"
                if "battery" in data:
                    device.battery_level_pct = float(data["battery"])

            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error processing telemetry message: {e}")
        return False

def process_command_ack_message(topic: str, payload_str: str) -> bool:
    """Process command acknowledgements from devices via MQTT."""
    try:
        data = json.loads(payload_str)
        command_id = data.get("command_id")
        if not command_id:
            return False
        
        db = SessionLocal()
        try:
            cmd = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
            if cmd:
                cmd.status = data.get("status", "acknowledged")
                if cmd.status == "acknowledged":
                    cmd.acknowledged_at = datetime.now(timezone.utc)
                elif cmd.status in ("completed", "failed"):
                    cmd.completed_at = datetime.now(timezone.utc)
                db.commit()
                return True
            return False
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error processing command ack: {e}")
        return False
