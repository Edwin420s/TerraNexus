from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids
from app.models.entities import User, Device, Sensor, DeviceCommand, Farm

router = APIRouter(prefix="", tags=["devices"])

class DeviceCreateRequest(BaseModel):
    farm_id: str
    field_id: Optional[str] = None
    device_uid: str
    name: str
    device_type: str
    hardware_version: Optional[str] = "esp32-devkit-v1"
    firmware_version: Optional[str] = "1.0.0"

class DeviceResponse(BaseModel):
    id: str
    organisation_id: str
    farm_id: str
    field_id: Optional[str]
    device_uid: str
    name: str
    device_type: str
    hardware_version: Optional[str]
    firmware_version: Optional[str]
    provisioning_status: str
    connection_status: str
    battery_level_pct: Optional[float]
    signal_strength_rssi: Optional[int]
    last_telemetry_at: Optional[str]

class SensorCreateRequest(BaseModel):
    device_id: str
    sensor_index: int
    sensor_code: str
    measurement_type_code: str
    depth_cm: Optional[float] = None
    unit: str

class SensorResponse(BaseModel):
    id: str
    device_id: str
    sensor_index: int
    sensor_code: str
    measurement_type_code: str
    depth_cm: Optional[float]
    unit: str
    status: str

class CommandCreateRequest(BaseModel):
    command_type: str # turn_on, turn_off, set_config, reboot
    payload: Optional[Dict[str, Any]] = {}
    priority: Optional[int] = 5
    max_execution_duration_sec: Optional[int] = 1800

class CommandResponse(BaseModel):
    id: str
    device_id: str
    command_type: str
    payload: Dict[str, Any]
    status: str
    priority: int
    dispatched_at: Optional[str]
    acknowledged_at: Optional[str]
    completed_at: Optional[str]

class CommandAckRequest(BaseModel):
    status: str # acknowledged, executing, completed, failed
    error_message: Optional[str] = None
    telemetry_snapshot: Optional[Dict[str, Any]] = None

@router.get("/devices", response_model=List[DeviceResponse])
def list_devices(farm_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(Device).filter(Device.organisation_id.in_(user_org_ids))
    if farm_id:
        query = query.filter(Device.farm_id == farm_id)
    devices = query.all()
    return [
        DeviceResponse(
            id=d.id,
            organisation_id=d.organisation_id,
            farm_id=d.farm_id,
            field_id=d.field_id,
            device_uid=d.device_uid,
            name=d.name,
            device_type=d.device_type,
            hardware_version=d.hardware_version,
            firmware_version=d.firmware_version,
            provisioning_status=d.provisioning_status,
            connection_status=d.connection_status,
            battery_level_pct=float(d.battery_level_pct) if d.battery_level_pct is not None else None,
            signal_strength_rssi=d.signal_strength_rssi,
            last_telemetry_at=d.last_telemetry_at.isoformat() if d.last_telemetry_at else None
        ) for d in devices
    ]

@router.post("/devices", response_model=DeviceResponse)
def register_device(req: DeviceCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    farm = db.query(Farm).filter(Farm.id == req.farm_id, Farm.organisation_id.in_(user_org_ids)).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    
    device = Device(
        organisation_id=farm.organisation_id,
        farm_id=farm.id,
        field_id=req.field_id,
        device_uid=req.device_uid,
        name=req.name,
        device_type=req.device_type,
        hardware_version=req.hardware_version,
        firmware_version=req.firmware_version,
        provisioning_status="active",
        connection_status="online"
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return DeviceResponse(
        id=device.id,
        organisation_id=device.organisation_id,
        farm_id=device.farm_id,
        field_id=device.field_id,
        device_uid=device.device_uid,
        name=device.name,
        device_type=device.device_type,
        hardware_version=device.hardware_version,
        firmware_version=device.firmware_version,
        provisioning_status=device.provisioning_status,
        connection_status=device.connection_status,
        battery_level_pct=float(device.battery_level_pct) if device.battery_level_pct is not None else None,
        signal_strength_rssi=device.signal_strength_rssi,
        last_telemetry_at=device.last_telemetry_at.isoformat() if device.last_telemetry_at else None
    )

@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return DeviceResponse(
        id=dev.id,
        organisation_id=dev.organisation_id,
        farm_id=dev.farm_id,
        field_id=dev.field_id,
        device_uid=dev.device_uid,
        name=dev.name,
        device_type=dev.device_type,
        hardware_version=dev.hardware_version,
        firmware_version=dev.firmware_version,
        provisioning_status=dev.provisioning_status,
        connection_status=dev.connection_status,
        battery_level_pct=float(dev.battery_level_pct) if dev.battery_level_pct is not None else None,
        signal_strength_rssi=dev.signal_strength_rssi,
        last_telemetry_at=dev.last_telemetry_at.isoformat() if dev.last_telemetry_at else None
    )

@router.post("/devices/{device_id}/provision")
def provision_device(device_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Generate unique cryptographic device access token & MQTT credentials
    import secrets
    device_token = f"tnx_dev_{secrets.token_urlsafe(32)}"
    mqtt_password = f"tnx_mqtt_{secrets.token_urlsafe(24)}"

    cfg = dict(dev.config) if isinstance(dev.config, dict) else {}
    cfg["device_token"] = device_token
    cfg["mqtt_username"] = dev.device_uid
    cfg["mqtt_password"] = mqtt_password
    dev.config = cfg

    dev.provisioning_status = "active"
    dev.connection_status = "pending_first_connect"
    db.commit()
    return {
        "status": "provisioned",
        "device_id": dev.id,
        "device_uid": dev.device_uid,
        "device_token": device_token,
        "mqtt_username": dev.device_uid,
        "mqtt_password": mqtt_password,
        "connection_status": dev.connection_status,
        "mqtt_topic_telemetry": f"tnx/{dev.organisation_id}/farm/{dev.farm_id}/device/{dev.device_uid}/telemetry",
        "mqtt_topic_commands": f"tnx/{dev.organisation_id}/farm/{dev.farm_id}/device/{dev.device_uid}/commands"
    }

@router.post("/devices/{device_id}/revoke")
def revoke_device(device_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    
    dev.provisioning_status = "revoked"
    dev.connection_status = "offline"
    cfg = dict(dev.config) if isinstance(dev.config, dict) else {}
    cfg.pop("device_token", None)
    cfg.pop("mqtt_password", None)
    dev.config = cfg
    db.commit()
    return {"status": "revoked", "device_id": dev.id}

@router.post("/devices/{device_id}/rotate-credentials")
def rotate_device_credentials(device_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    if dev.provisioning_status != "active":
        raise HTTPException(status_code=400, detail="Cannot rotate credentials for inactive or revoked device")

    import secrets
    device_token = f"tnx_dev_{secrets.token_urlsafe(32)}"
    mqtt_password = f"tnx_mqtt_{secrets.token_urlsafe(24)}"
    cfg = dict(dev.config) if isinstance(dev.config, dict) else {}
    cfg["device_token"] = device_token
    cfg["mqtt_password"] = mqtt_password
    dev.config = cfg
    db.commit()
    return {
        "status": "credentials_rotated",
        "device_id": dev.id,
        "device_token": device_token,
        "mqtt_username": dev.device_uid,
        "mqtt_password": mqtt_password
    }

@router.get("/sensors", response_model=List[SensorResponse])
def list_sensors(device_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(Sensor).join(Device).filter(Device.organisation_id.in_(user_org_ids))
    if device_id:
        query = query.filter(Sensor.device_id == device_id)
    sensors = query.all()
    return [
        SensorResponse(
            id=s.id,
            device_id=s.device_id,
            sensor_index=s.sensor_index,
            sensor_code=s.sensor_code,
            measurement_type_code=s.measurement_type_code,
            depth_cm=float(s.depth_cm) if s.depth_cm is not None else None,
            unit=s.unit,
            status=s.status
        ) for s in sensors
    ]

@router.post("/sensors", response_model=SensorResponse)
def register_sensor(req: SensorCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == req.device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Parent device not found or unauthorized")
    
    sensor = Sensor(
        device_id=dev.id,
        sensor_index=req.sensor_index,
        sensor_code=req.sensor_code,
        measurement_type_code=req.measurement_type_code,
        depth_cm=req.depth_cm,
        unit=req.unit,
        status="active"
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return SensorResponse(
        id=sensor.id,
        device_id=sensor.device_id,
        sensor_index=sensor.sensor_index,
        sensor_code=sensor.sensor_code,
        measurement_type_code=sensor.measurement_type_code,
        depth_cm=float(sensor.depth_cm) if sensor.depth_cm is not None else None,
        unit=sensor.unit,
        status=sensor.status
    )

@router.get("/devices/{device_id}/commands", response_model=List[CommandResponse])
def list_device_commands(device_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    cmds = db.query(DeviceCommand).filter(DeviceCommand.device_id == device_id).order_by(DeviceCommand.created_at.desc()).all()
    return [
        CommandResponse(
            id=c.id,
            device_id=c.device_id,
            command_type=c.command_type,
            payload=c.payload or {},
            status=c.status,
            priority=c.priority,
            dispatched_at=c.dispatched_at.isoformat() if c.dispatched_at else None,
            acknowledged_at=c.acknowledged_at.isoformat() if c.acknowledged_at else None,
            completed_at=c.completed_at.isoformat() if c.completed_at else None
        ) for c in cmds
    ]

@router.post("/devices/{device_id}/commands", response_model=CommandResponse)
def dispatch_command(device_id: str, req: CommandCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    dev = db.query(Device).filter(Device.id == device_id, Device.organisation_id.in_(user_org_ids)).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Preflight Safety Checks (TNX-API-001 Section 49)
    if dev.provisioning_status != "active":
        raise HTTPException(status_code=400, detail="Device is not active or provisioned")
    
    # Cap max execution duration
    max_duration = min(req.max_execution_duration_sec or 1800, 3600)

    cmd = DeviceCommand(
        organisation_id=dev.organisation_id,
        farm_id=dev.farm_id,
        device_id=dev.id,
        command_type=req.command_type,
        payload=req.payload or {},
        status="dispatched",
        priority=req.priority or 5,
        max_execution_duration_sec=max_duration,
        dispatched_at=datetime.now(timezone.utc),
        initiated_by=user.id
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return CommandResponse(
        id=cmd.id,
        device_id=cmd.device_id,
        command_type=cmd.command_type,
        payload=cmd.payload or {},
        status=cmd.status,
        priority=cmd.priority,
        dispatched_at=cmd.dispatched_at.isoformat() if cmd.dispatched_at else None,
        acknowledged_at=cmd.acknowledged_at.isoformat() if cmd.acknowledged_at else None,
        completed_at=cmd.completed_at.isoformat() if cmd.completed_at else None
    )

@router.post("/devices/commands/{command_id}/ack")
def acknowledge_command(command_id: str, req: CommandAckRequest, db: Session = Depends(get_db)):
    cmd = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")
    
    cmd.status = req.status
    if req.status == "acknowledged":
        cmd.acknowledged_at = datetime.now(timezone.utc)
    elif req.status in ("completed", "failed"):
        cmd.completed_at = datetime.now(timezone.utc)
    if req.error_message:
        cmd.error_message = req.error_message
    
    db.commit()
    return {"status": "ok", "command_id": cmd.id, "new_status": cmd.status}
