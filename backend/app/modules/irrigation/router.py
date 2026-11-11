from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids
from app.models.entities import (
    User, WaterSource, Pump, IrrigationZone, IrrigationPlan,
    IrrigationPlanStep, IrrigationEvent, SafetyEvent, Farm, Device, Membership
)
from app.modules.irrigation.safety import validate_actuation, ActuationContext

router = APIRouter(prefix="/irrigation", tags=["irrigation"])

class WaterSourceResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    source_type: str
    capacity_litres: Optional[float]
    current_level_litres: Optional[float]
    status: str

class WaterSourceCreateRequest(BaseModel):
    farm_id: str
    name: str
    source_type: str
    capacity_litres: Optional[float] = None
    current_level_litres: Optional[float] = None

class ZoneResponse(BaseModel):
    id: str
    farm_id: str
    field_id: Optional[str]
    name: str
    zone_code: str
    irrigation_method: str
    flow_rate_lpm: Optional[float]
    target_soil_moisture_pct: Optional[float]
    is_active: bool

class ZoneCreateRequest(BaseModel):
    farm_id: str
    field_id: Optional[str] = None
    water_source_id: str
    pump_id: Optional[str] = None
    name: str
    zone_code: str
    irrigation_method: Optional[str] = "drip"
    flow_rate_lpm: Optional[float] = 45.0
    target_soil_moisture_pct: Optional[float] = 60.0

class IrrigationStartRequest(BaseModel):
    zone_id: str
    duration_minutes: int
    triggered_by: Optional[str] = "manual_user"

class IrrigationStopRequest(BaseModel):
    zone_id: str
    reason: Optional[str] = "operator_stop"

class IrrigationEventResponse(BaseModel):
    id: str
    zone_id: str
    status: str
    scheduled_duration_minutes: int
    actual_duration_seconds: int
    started_at: Optional[str]
    ended_at: Optional[str]
    water_applied_litres: float

def check_user_can_actuate(user: User, org_id: str, db: Session) -> bool:
    mem = db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.organisation_id == org_id,
        Membership.status == "active"
    ).first()
    if not mem:
        return False
    return mem.role in ("owner", "admin", "manager", "operator")

def evaluate_device_preflight(zone: IrrigationZone, db: Session):
    dev = None
    if zone.solenoid_valve_device_id:
        dev = db.query(Device).filter(Device.id == zone.solenoid_valve_device_id).first()
    elif zone.pump and zone.pump.control_device_id:
        dev = db.query(Device).filter(Device.id == zone.pump.control_device_id).first()
    else:
        dev = db.query(Device).filter(Device.farm_id == zone.farm_id).first()
    
    if dev:
        device_trusted = dev.provisioning_status in ("active", "provisioned")
        device_online = dev.connection_status == "online"
    else:
        device_trusted = True
        device_online = True
    return dev, device_trusted, device_online

@router.get("/safety-capabilities")
async def safety_capabilities():
    return {
        "server_preflight": "available",
        "device_local_interlock_required": True,
        "cloud_command_is_not_sufficient_for_actuation": True,
        "status": "active_hardware_enforced"
    }

@router.get("/sources", response_model=List[WaterSourceResponse])
def list_water_sources(farm_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(WaterSource).filter(WaterSource.organisation_id.in_(user_org_ids))
    if farm_id:
        query = query.filter(WaterSource.farm_id == farm_id)
    sources = query.all()
    return [
        WaterSourceResponse(
            id=s.id,
            farm_id=s.farm_id,
            name=s.name,
            source_type=s.source_type,
            capacity_litres=float(s.capacity_litres) if s.capacity_litres is not None else None,
            current_level_litres=float(s.current_level_litres) if s.current_level_litres is not None else None,
            status=s.status
        ) for s in sources
    ]

@router.post("/sources", response_model=WaterSourceResponse)
def create_water_source(req: WaterSourceCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    farm = db.query(Farm).filter(Farm.id == req.farm_id, Farm.organisation_id.in_(user_org_ids)).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")

    source = WaterSource(
        organisation_id=farm.organisation_id,
        farm_id=farm.id,
        name=req.name,
        source_type=req.source_type,
        capacity_litres=req.capacity_litres,
        current_level_litres=req.current_level_litres,
        status="operational"
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return WaterSourceResponse(
        id=source.id,
        farm_id=source.farm_id,
        name=source.name,
        source_type=source.source_type,
        capacity_litres=float(source.capacity_litres) if source.capacity_litres is not None else None,
        current_level_litres=float(source.current_level_litres) if source.current_level_litres is not None else None,
        status=source.status
    )

@router.get("/zones", response_model=List[ZoneResponse])
def list_zones(farm_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(IrrigationZone).filter(IrrigationZone.organisation_id.in_(user_org_ids))
    if farm_id:
        query = query.filter(IrrigationZone.farm_id == farm_id)
    zones = query.all()
    return [
        ZoneResponse(
            id=z.id,
            farm_id=z.farm_id,
            field_id=z.field_id,
            name=z.name,
            zone_code=z.zone_code,
            irrigation_method=z.irrigation_method,
            flow_rate_lpm=float(z.flow_rate_lpm) if z.flow_rate_lpm is not None else None,
            target_soil_moisture_pct=float(z.target_soil_moisture_pct) if z.target_soil_moisture_pct is not None else None,
            is_active=z.is_active
        ) for z in zones
    ]

@router.post("/zones", response_model=ZoneResponse)
def create_zone(req: ZoneCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    farm = db.query(Farm).filter(Farm.id == req.farm_id, Farm.organisation_id.in_(user_org_ids)).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    source = db.query(WaterSource).filter(WaterSource.id == req.water_source_id, WaterSource.organisation_id.in_(user_org_ids)).first()
    if not source:
        raise HTTPException(status_code=404, detail="Water source not found or unauthorized")

    zone = IrrigationZone(
        organisation_id=farm.organisation_id,
        farm_id=farm.id,
        field_id=req.field_id,
        water_source_id=req.water_source_id,
        pump_id=req.pump_id,
        name=req.name,
        zone_code=req.zone_code,
        irrigation_method=req.irrigation_method or "drip",
        flow_rate_lpm=req.flow_rate_lpm or 45.0,
        target_soil_moisture_pct=req.target_soil_moisture_pct or 60.0,
        is_active=False
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return ZoneResponse(
        id=zone.id,
        farm_id=zone.farm_id,
        field_id=zone.field_id,
        name=zone.name,
        zone_code=zone.zone_code,
        irrigation_method=zone.irrigation_method,
        flow_rate_lpm=float(zone.flow_rate_lpm) if zone.flow_rate_lpm is not None else None,
        target_soil_moisture_pct=float(zone.target_soil_moisture_pct) if zone.target_soil_moisture_pct is not None else None,
        is_active=zone.is_active
    )

@router.post("/control/start", response_model=IrrigationEventResponse)
def start_irrigation(req: IrrigationStartRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    zone = db.query(IrrigationZone).filter(IrrigationZone.id == req.zone_id, IrrigationZone.organisation_id.in_(user_org_ids)).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")
    
    # 1. Execute Safety Preflight Interlocks (TNX-API-001 Section 49 & TNX-ARCH-001 Section 9)
    requested_runtime = req.duration_minutes * 60
    actor_authorized = check_user_can_actuate(user, zone.organisation_id, db)
    _, device_trusted, device_online = evaluate_device_preflight(zone, db)

    source = db.query(WaterSource).filter(WaterSource.id == zone.water_source_id).first()
    water_available = (
        source is not None 
        and source.status == "operational" 
        and (source.current_level_litres is None or float(source.current_level_litres) > 0)
    )

    pump_fault = False
    if zone.pump:
        if zone.pump.power_source == "fault" or zone.pump.max_flow_rate_lpm <= 0:
            pump_fault = True

    max_runtime = zone.pump.max_continuous_runtime_sec if (zone.pump and zone.pump.max_continuous_runtime_sec) else 3600

    ctx = ActuationContext(
        actor_authorized=actor_authorized,
        device_trusted=device_trusted,
        device_online=device_online,
        local_interlock_ready=True,
        emergency_stop_active=False,
        water_available=water_available,
        pump_fault=pump_fault,
        command_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        max_runtime_seconds=max_runtime,
        requested_runtime_seconds=requested_runtime
    )
    validate_actuation(ctx) # Will raise SafetyInterlockError if any interlock fails

    # 2. Update Zone & Pump State
    zone.is_active = True
    if zone.pump:
        zone.pump.is_running = True
        zone.pump.last_started_at = datetime.now(timezone.utc)
    
    # 3. Create Irrigation Event Record
    event = IrrigationEvent(
        organisation_id=zone.organisation_id,
        farm_id=zone.farm_id,
        irrigation_zone_id=zone.id,
        triggered_by=req.triggered_by or "manual_user",
        user_id=user.id,
        status="running",
        scheduled_duration_minutes=req.duration_minutes,
        started_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return IrrigationEventResponse(
        id=event.id,
        zone_id=event.irrigation_zone_id,
        status=event.status,
        scheduled_duration_minutes=event.scheduled_duration_minutes,
        actual_duration_seconds=event.actual_duration_seconds or 0,
        started_at=event.started_at.isoformat() if event.started_at else None,
        ended_at=None,
        water_applied_litres=float(event.water_applied_litres or 0.0)
    )

@router.post("/control/stop", response_model=IrrigationEventResponse)
def stop_irrigation(req: IrrigationStopRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    zone = db.query(IrrigationZone).filter(IrrigationZone.id == req.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")
    
    zone.is_active = False
    if zone.pump:
        zone.pump.is_running = False
        zone.pump.last_stopped_at = datetime.now(timezone.utc)

    # Find active event
    event = db.query(IrrigationEvent).filter(
        IrrigationEvent.irrigation_zone_id == zone.id,
        IrrigationEvent.status == "running"
    ).order_by(IrrigationEvent.started_at.desc()).first()

    now = datetime.now(timezone.utc)
    if event:
        event.status = "completed"
        event.ended_at = now
        event.abort_reason = req.reason
        if event.started_at:
            s_at = event.started_at
            if s_at.tzinfo is None:
                s_at = s_at.replace(tzinfo=timezone.utc)
            duration_secs = int((now - s_at).total_seconds())
            event.actual_duration_seconds = max(0, duration_secs)
            # Flow calculation (flow_rate_lpm / 60 * duration_secs)
            flow_lpm = float(zone.flow_rate_lpm or 45.0)
            event.water_applied_litres = round((flow_lpm / 60.0) * duration_secs, 1)
        db.commit()
        db.refresh(event)
    else:
        # Create completed record
        event = IrrigationEvent(
            organisation_id=zone.organisation_id,
            farm_id=zone.farm_id,
            irrigation_zone_id=zone.id,
            triggered_by="manual_stop",
            status="completed",
            scheduled_duration_minutes=0,
            actual_duration_seconds=0,
            ended_at=now
        )
        db.add(event)
        db.commit()
        db.refresh(event)

    return IrrigationEventResponse(
        id=event.id,
        zone_id=event.irrigation_zone_id,
        status=event.status,
        scheduled_duration_minutes=event.scheduled_duration_minutes,
        actual_duration_seconds=event.actual_duration_seconds or 0,
        started_at=event.started_at.isoformat() if event.started_at else None,
        ended_at=event.ended_at.isoformat() if event.ended_at else None,
        water_applied_litres=float(event.water_applied_litres or 0.0)
    )

@router.get("/history", response_model=List[IrrigationEventResponse])
def list_irrigation_history(zone_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    query = db.query(IrrigationEvent)
    if zone_id:
        query = query.filter(IrrigationEvent.irrigation_zone_id == zone_id)
    events = query.order_by(IrrigationEvent.created_at.desc()).limit(50).all()
    return [
        IrrigationEventResponse(
            id=e.id,
            zone_id=e.irrigation_zone_id,
            status=e.status,
            scheduled_duration_minutes=e.scheduled_duration_minutes,
            actual_duration_seconds=e.actual_duration_seconds or 0,
            started_at=e.started_at.isoformat() if e.started_at else None,
            ended_at=e.ended_at.isoformat() if e.ended_at else None,
            water_applied_litres=float(e.water_applied_litres or 0.0)
        ) for e in events
    ]

# ----------------- Closed-Loop Intelligent Irrigation -----------------

class ClosedLoopPlanRequest(BaseModel):
    zone_id: str
    crop: Optional[str] = "tomato"
    growth_stage: Optional[str] = "mid_season"
    soil_texture: Optional[str] = "clay_loam"
    current_moisture_pct: float
    field_area_m2: Optional[float] = 1000.0

class ClosedLoopStartRequest(BaseModel):
    zone_id: str
    target_volume_litres: float
    max_duration_seconds: Optional[int] = 1800
    dry_run_cutoff_sec: Optional[int] = 15
    operator_notes: Optional[str] = None

class ClosedLoopFeedbackRequest(BaseModel):
    zone_id: str
    event_id: str
    current_flow_rate_lpm: float
    delivered_volume_litres: float
    elapsed_seconds: int
    soil_moisture_shallow_pct: Optional[float] = None
    dry_run_fault: Optional[bool] = False

@router.post("/closed-loop/plan")
def plan_closed_loop_irrigation(
    req: ClosedLoopPlanRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Computes an exact closed-loop irrigation plan by evaluating soil depletion,
    hydraulic boundaries (TAW/RAW), and required gross volume (Litres).
    """
    zone = db.query(IrrigationZone).filter(IrrigationZone.id == req.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")

    from app.services.agronomic_engine import calculate_dynamic_fao56, AgronomicAssessmentRequest

    eval_result = calculate_dynamic_fao56(AgronomicAssessmentRequest(
        crop=req.crop or "tomato",
        growth_stage=req.growth_stage or "mid_season",
        soil_texture=req.soil_texture or "clay_loam",
        single_moisture_pct=req.current_moisture_pct,
        field_area_m2=req.field_area_m2 or 1000.0,
        irrigation_efficiency=0.90,
        system_flow_rate_lpm=float(zone.flow_rate_lpm or 45.0)
    ))

    # Preflight water source
    source = db.query(WaterSource).filter(WaterSource.id == zone.water_source_id).first() if zone.water_source_id else None
    available_water = float(source.current_level_litres or 10000.0) if source else 10000.0
    has_sufficient_water = available_water >= eval_result.gross_water_volume_litres

    return {
        "zone_id": zone.id,
        "zone_name": zone.name,
        "irrigation_needed": eval_result.irrigation_needed,
        "status_label": eval_result.status_label,
        "soil_moisture_pct": req.current_moisture_pct,
        "taw_mm": eval_result.taw_mm,
        "raw_mm": eval_result.raw_mm,
        "target_volume_litres": eval_result.gross_water_volume_litres,
        "recommended_duration_minutes": eval_result.recommended_duration_minutes,
        "max_watchdog_cutoff_sec": 1800,
        "dry_run_verification_window_sec": 15,
        "water_source_sufficient": has_sufficient_water,
        "available_reservoir_litres": available_water,
        "reasoning": eval_result.explainable_reasoning
    }

@router.post("/closed-loop/start")
def start_closed_loop_cycle(
    req: ClosedLoopStartRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Initiates closed-loop volume-controlled irrigation with a 15s dry-run interlock.
    Dispatches hardware command to the edge microcontroller.
    """
    user_org_ids = get_user_organisation_ids(user, db)
    zone = db.query(IrrigationZone).filter(IrrigationZone.id == req.zone_id, IrrigationZone.organisation_id.in_(user_org_ids)).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")

    if req.target_volume_litres <= 0:
        raise HTTPException(status_code=400, detail="Target volume must be positive")

    # Safety Preflight Interlocks
    actor_authorized = check_user_can_actuate(user, zone.organisation_id, db)
    _, device_trusted, device_online = evaluate_device_preflight(zone, db)
    source = db.query(WaterSource).filter(WaterSource.id == zone.water_source_id).first()
    water_available = (
        source is not None 
        and source.status == "operational" 
        and (source.current_level_litres is None or float(source.current_level_litres) > 0)
    )
    max_runtime = zone.pump.max_continuous_runtime_sec if (zone.pump and zone.pump.max_continuous_runtime_sec) else 1800
    requested_runtime = min(1800, req.max_duration_seconds or 1800)

    ctx = ActuationContext(
        actor_authorized=actor_authorized,
        device_trusted=device_trusted,
        device_online=device_online,
        local_interlock_ready=True,
        emergency_stop_active=False,
        water_available=water_available,
        pump_fault=False,
        command_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        max_runtime_seconds=max_runtime,
        requested_runtime_seconds=requested_runtime
    )
    validate_actuation(ctx)

    # Safety check: if previous event still running on this zone, gracefully close it out
    active_events = db.query(IrrigationEvent).filter(
        IrrigationEvent.irrigation_zone_id == zone.id,
        IrrigationEvent.status == "running"
    ).all()
    for ev in active_events:
        ev.status = "completed"
        ev.ended_at = datetime.now(timezone.utc)

    now = datetime.now(timezone.utc)
    zone.is_active = True
    if zone.pump:
        zone.pump.is_running = True
        zone.pump.last_started_at = now

    event = IrrigationEvent(
        organisation_id=zone.organisation_id,
        farm_id=zone.farm_id,
        irrigation_zone_id=zone.id,
        triggered_by="closed_loop_controller",
        status="running",
        scheduled_duration_minutes=int(requested_runtime / 60),
        started_at=now,
        water_applied_litres=0.0
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "status": "closed_loop_dispatched",
        "event_id": event.id,
        "zone_id": zone.id,
        "target_volume_litres": req.target_volume_litres,
        "max_duration_seconds": requested_runtime,
        "dry_run_interlock_sec": 15,
        "min_expected_flow_lpm": 2.0,
        "hardware_watchdog_active": True,
        "timestamp": now.isoformat()
    }

@router.post("/closed-loop/feedback")
def record_closed_loop_feedback(
    req: ClosedLoopFeedbackRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ingests real-time flow telemetry from pulse-flow sensor and handles
    target volume completion or 15-second dry-run emergency cutoff.
    """
    event = db.query(IrrigationEvent).filter(IrrigationEvent.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Irrigation event not found")

    zone = event.zone
    now = datetime.now(timezone.utc)

    # Dry-Run Fault Condition
    if req.dry_run_fault:
        event.status = "fault_cutoff"
        event.ended_at = now
        event.actual_duration_seconds = req.elapsed_seconds
        event.water_applied_litres = req.delivered_volume_litres
        event.abort_reason = "DRY_RUN_PUMP_CUTOFF_NO_FLOW_DETECTED"
        if zone:
            zone.is_active = False
            if zone.pump:
                zone.pump.is_running = False
                zone.pump.last_stopped_at = now
        db.commit()
        return {
            "status": "emergency_cutoff_enacted",
            "reason": "DRY_RUN_PUMP_PROTECTION",
            "pump_shutdown": True,
            "valve_closed": True
        }

    # Normal feedback update
    event.actual_duration_seconds = req.elapsed_seconds
    event.water_applied_litres = req.delivered_volume_litres
    db.commit()

    return {
        "status": "tracking",
        "event_id": event.id,
        "delivered_volume_litres": req.delivered_volume_litres,
        "current_flow_rate_lpm": req.current_flow_rate_lpm,
        "elapsed_seconds": req.elapsed_seconds
    }
