from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids
from app.models.entities import User, Device, Sensor, Measurement, AuditLog
from app.modules.telemetry.schemas import TelemetryEnvelope, TelemetryAccepted

router = APIRouter(tags=["telemetry"])

class MeasurementResponse(BaseModel):
    id: str
    device_id: str
    field_id: Optional[str]
    measurement_type: str
    value: float
    unit: str
    depth_cm: Optional[float]
    observed_at: str
    quality_score: float

def validate_sensor_range(measurement_type: str, value: float) -> tuple[bool, float]:
    """
    Validates physical plausibility of agronomic measurements.
    Returns (is_valid, quality_score).
    """
    m = measurement_type.lower()
    if "soil_moisture" in m or "moisture" in m:
        if 0.0 <= value <= 100.0:
            return True, 1.0
        return False, 0.0
    elif "temp" in m:
        if -30.0 <= value <= 70.0:
            return True, 1.0
        return False, 0.0
    elif "humidity" in m:
        if 0.0 <= value <= 100.0:
            return True, 1.0
        return False, 0.0
    elif "battery" in m:
        if 0.0 <= value <= 100.0 or 0.0 <= value <= 12.0:
            return True, 1.0
        return False, 0.0
    elif "ph" in m:
        if 0.0 <= value <= 14.0:
            return True, 1.0
        return False, 0.0
    elif "flow" in m:
        if 0.0 <= value <= 2000.0:
            return True, 1.0
        return False, 0.0
    elif "conductivity" in m or "ec" in m:
        if 0.0 <= value <= 20.0:
            return True, 1.0
        return False, 0.0
    return True, 1.0

@router.post("/telemetry", response_model=TelemetryAccepted, status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry(payload: TelemetryEnvelope, db: Session = Depends(get_db)):
    """Durable ingestion and quality evaluation for canonical telemetry packets."""
    event_id_str = str(payload.event_id) if payload.event_id else None

    # Deduplicate incoming telemetry on event_id
    if event_id_str:
        existing_log = db.query(AuditLog).filter(
            AuditLog.action == "telemetry_ingest",
            AuditLog.resource_id == event_id_str
        ).first()
        if existing_log:
            return TelemetryAccepted(
                event_id=event_id_str,
                accepted=True,
                status="already_ingested_duplicate",
                received_at=existing_log.created_at
            )

    dev_id_str = str(payload.device_id)
    device = db.query(Device).filter((Device.id == dev_id_str) | (Device.device_uid == dev_id_str)).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown or unprovisioned device"
        )
    if device.provisioning_status not in ("active", "provisioned"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device is inactive or revoked"
        )

    org_id = device.organisation_id
    farm_id = device.farm_id
    field_id = device.field_id
    
    # Persist measurements with range validation
    for m in payload.measurements:
        m_type = m.get("type") or m.get("measurement_type") or "soil_moisture"
        m_val = float(m.get("value", 0.0))
        m_unit = m.get("unit", "%")
        m_depth = float(m.get("depth_cm")) if m.get("depth_cm") is not None else None
        
        is_valid, quality_score = validate_sensor_range(m_type, m_val)

        # Check battery update if reported
        if m_type in ("battery_voltage", "battery_level_pct") and device:
            device.battery_level_pct = m_val

        measurement_record = Measurement(
            organisation_id=org_id,
            farm_id=farm_id,
            field_id=field_id,
            device_id=device.id if device else dev_id_str,
            measurement_type=m_type,
            value=m_val,
            unit=m_unit,
            depth_cm=m_depth,
            observed_at=payload.observed_at,
            received_at=datetime.now(timezone.utc),
            quality_score=quality_score,
            is_valid=is_valid
        )
        db.add(measurement_record)

    # Persist AuditLog record for idempotency deduplication
    if event_id_str:
        audit = AuditLog(
            organisation_id=org_id,
            action="telemetry_ingest",
            resource_type="event",
            resource_id=event_id_str,
            status="success"
        )
        db.add(audit)

    if device:
        device.last_telemetry_at = datetime.now(timezone.utc)
        device.connection_status = "online"

    db.commit()

    return TelemetryAccepted(
        event_id=event_id_str,
        accepted=True,
        status="persisted_and_processed",
        received_at=datetime.now(timezone.utc)
    )

@router.post("/telemetry/batch", response_model=List[TelemetryAccepted], status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry_batch(payloads: List[TelemetryEnvelope], db: Session = Depends(get_db)):
    results = []
    for p in payloads:
        res = await ingest_telemetry(p, db)
        results.append(res)
    return results

@router.get("/measurements", response_model=List[MeasurementResponse])
def list_measurements(
    field_id: Optional[str] = None,
    device_id: Optional[str] = None,
    measurement_type: Optional[str] = None,
    limit: int = Query(100, le=500),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(Measurement).filter(Measurement.organisation_id.in_(user_org_ids))
    if field_id:
        query = query.filter(Measurement.field_id == field_id)
    if device_id:
        query = query.filter(Measurement.device_id == device_id)
    if measurement_type:
        query = query.filter(Measurement.measurement_type == measurement_type)
    
    records = query.order_by(Measurement.observed_at.desc()).limit(limit).all()

    return [
        MeasurementResponse(
            id=m.id,
            device_id=m.device_id,
            field_id=m.field_id,
            measurement_type=m.measurement_type,
            value=float(m.value),
            unit=m.unit,
            depth_cm=float(m.depth_cm) if m.depth_cm is not None else None,
            observed_at=m.observed_at.isoformat() if m.observed_at else "",
            quality_score=float(m.quality_score) if m.quality_score is not None else 1.0
        ) for m in records
    ]
