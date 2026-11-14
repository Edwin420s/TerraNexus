from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids
from app.core.security import decode_access_token
from sqlalchemy.orm.attributes import flag_modified
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
async def ingest_telemetry(
    payload: TelemetryEnvelope,
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Durable ingestion, strict device authentication, sequence monotonic validation, and quality evaluation."""
    dev_id_str = str(payload.device_id)
    device = db.query(Device).filter((Device.id == dev_id_str) | (Device.device_uid == dev_id_str)).first()
    
    # 1. Device lookup & Authentication MUST happen BEFORE deduplication or audit logging
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

    cfg = dict(device.config) if isinstance(device.config, dict) else {}
    expected_token = cfg.get("device_token")
    raw_bearer = authorization[7:] if authorization and authorization.startswith("Bearer ") else authorization
    provided_token = x_device_token or raw_bearer

    is_authenticated = False
    if expected_token and (provided_token == expected_token):
        is_authenticated = True
    elif raw_bearer:
        token_payload = decode_access_token(raw_bearer)
        if token_payload and (token_payload.get("org") == device.organisation_id or token_payload.get("sub")):
            is_authenticated = True

    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing device authentication token"
        )

    # 2. Deduplication on event_id for authenticated device
    event_id_str = str(payload.event_id) if payload.event_id else None
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

    # 3. Sequence validation & Anti-Replay (must be strictly monotonic when sequence > 0)
    if payload.sequence is not None and payload.sequence > 0:
        last_seq = cfg.get("last_telemetry_sequence", -1)
        if payload.sequence <= last_seq:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Replay detected: telemetry sequence {payload.sequence} <= last sequence {last_seq}"
            )
        cfg["last_telemetry_sequence"] = payload.sequence
        device.config = cfg
        flag_modified(device, "config")

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

    now_utc = datetime.now(timezone.utc)
    device.last_telemetry_at = now_utc
    device.connection_status = "online"
    device.config = cfg

    db.commit()

    return TelemetryAccepted(
        event_id=event_id_str,
        accepted=True,
        status="persisted_and_processed",
        received_at=datetime.now(timezone.utc)
    )

class HeartbeatRequest(BaseModel):
    device_id: str
    status: Optional[str] = "online"
    battery_level_pct: Optional[float] = None
    firmware_version: Optional[str] = None

@router.post("/telemetry/heartbeat")
def ingest_heartbeat(
    req: HeartbeatRequest,
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Dedicated authenticated device heartbeat endpoint."""
    device = db.query(Device).filter((Device.id == req.device_id) | (Device.device_uid == req.device_id)).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown device")
    
    cfg = dict(device.config) if isinstance(device.config, dict) else {}
    expected_token = cfg.get("device_token")
    raw_bearer = authorization[7:] if authorization and authorization.startswith("Bearer ") else authorization
    provided_token = x_device_token or raw_bearer

    is_authenticated = False
    if expected_token and (provided_token == expected_token):
        is_authenticated = True
    elif raw_bearer:
        token_payload = decode_access_token(raw_bearer)
        if token_payload and (token_payload.get("org") == device.organisation_id or token_payload.get("sub")):
            is_authenticated = True

    if not is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device credentials")

    now = datetime.now(timezone.utc)
    device.last_heartbeat_at = now
    device.connection_status = "online"
    if req.battery_level_pct is not None:
        device.battery_level_pct = req.battery_level_pct
    db.commit()
    return {"status": "heartbeat_acknowledged", "device_id": device.id, "last_heartbeat_at": now.isoformat()}

@router.post("/telemetry/batch", response_model=List[TelemetryAccepted], status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry_batch(
    payloads: List[TelemetryEnvelope],
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    results = []
    for p in payloads:
        res = await ingest_telemetry(p, x_device_token=x_device_token, authorization=authorization, db=db)
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
