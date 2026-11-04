from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.entities import User, Farm, Field, FieldObservation

router = APIRouter(prefix="", tags=["farms"])

# Schemas
class FarmCreateRequest(BaseModel):
    name: str
    farm_code: Optional[str] = None
    area_hectares: Optional[float] = None
    country_code: Optional[str] = "KE"
    timezone: Optional[str] = "Africa/Nairobi"
    boundary_geojson: Optional[Dict[str, Any]] = None

class FarmResponse(BaseModel):
    id: str
    organisation_id: str
    name: str
    farm_code: Optional[str]
    area_hectares: Optional[float]
    country_code: Optional[str]
    timezone: str
    status: str
    boundary_geojson: Optional[Dict[str, Any]] = None

class FieldCreateRequest(BaseModel):
    farm_id: str
    name: str
    field_code: Optional[str] = None
    area_hectares: Optional[float] = None
    boundary_geojson: Optional[Dict[str, Any]] = None

class FieldResponse(BaseModel):
    id: str
    organisation_id: str
    farm_id: str
    name: str
    field_code: Optional[str]
    area_hectares: Optional[float]
    status: str
    boundary_geojson: Optional[Dict[str, Any]] = None

class ObservationCreateRequest(BaseModel):
    observation_type: str
    description: str
    severity: Optional[str] = "medium"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[str]] = []

class ObservationResponse(BaseModel):
    id: str
    field_id: str
    observation_type: str
    description: str
    severity: Optional[str]
    observed_at: str
    photos: Optional[List[str]] = []

@router.get("/farms", response_model=List[FarmResponse])
def list_farms(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).all()
    return [
        FarmResponse(
            id=f.id,
            organisation_id=f.organisation_id,
            name=f.name,
            farm_code=f.farm_code,
            area_hectares=float(f.area_hectares) if f.area_hectares is not None else None,
            country_code=f.country_code,
            timezone=f.timezone,
            status=f.status,
            boundary_geojson=f.boundary_geojson
        ) for f in farms
    ]

@router.post("/farms", response_model=FarmResponse)
def create_farm(req: FarmCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Find user's organisation
    membership = user.memberships[0] if user.memberships else None
    org_id = membership.organisation_id if membership else "a0000000-0000-0000-0000-000000000001"
    
    farm = Farm(
        organisation_id=org_id,
        name=req.name,
        farm_code=req.farm_code or req.name[:6].upper().replace(" ", "-"),
        area_hectares=req.area_hectares,
        country_code=req.country_code,
        timezone=req.timezone,
        boundary_geojson=req.boundary_geojson,
        status="active"
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return FarmResponse(
        id=farm.id,
        organisation_id=farm.organisation_id,
        name=farm.name,
        farm_code=farm.farm_code,
        area_hectares=float(farm.area_hectares) if farm.area_hectares is not None else None,
        country_code=farm.country_code,
        timezone=farm.timezone,
        status=farm.status,
        boundary_geojson=farm.boundary_geojson
    )

@router.get("/farms/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return FarmResponse(
        id=farm.id,
        organisation_id=farm.organisation_id,
        name=farm.name,
        farm_code=farm.farm_code,
        area_hectares=float(farm.area_hectares) if farm.area_hectares is not None else None,
        country_code=farm.country_code,
        timezone=farm.timezone,
        status=farm.status,
        boundary_geojson=farm.boundary_geojson
    )

@router.get("/fields", response_model=List[FieldResponse])
def list_fields(farm_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    query = db.query(Field)
    if farm_id:
        query = query.filter(Field.farm_id == farm_id)
    fields = query.all()
    return [
        FieldResponse(
            id=f.id,
            organisation_id=f.organisation_id,
            farm_id=f.farm_id,
            name=f.name,
            field_code=f.field_code,
            area_hectares=float(f.area_hectares) if f.area_hectares is not None else None,
            status=f.status,
            boundary_geojson=f.boundary_geojson
        ) for f in fields
    ]

@router.post("/fields", response_model=FieldResponse)
def create_field(req: FieldCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Parent farm not found")
    
    field = Field(
        organisation_id=farm.organisation_id,
        farm_id=farm.id,
        name=req.name,
        field_code=req.field_code or req.name[:6].upper().replace(" ", "-"),
        area_hectares=req.area_hectares,
        boundary_geojson=req.boundary_geojson,
        status="active"
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return FieldResponse(
        id=field.id,
        organisation_id=field.organisation_id,
        farm_id=field.farm_id,
        name=field.name,
        field_code=field.field_code,
        area_hectares=float(field.area_hectares) if field.area_hectares is not None else None,
        status=field.status,
        boundary_geojson=field.boundary_geojson
    )

@router.get("/fields/{field_id}", response_model=FieldResponse)
def get_field(field_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return FieldResponse(
        id=field.id,
        organisation_id=field.organisation_id,
        farm_id=field.farm_id,
        name=field.name,
        field_code=field.field_code,
        area_hectares=float(field.area_hectares) if field.area_hectares is not None else None,
        status=field.status,
        boundary_geojson=field.boundary_geojson
    )

@router.get("/fields/{field_id}/observations", response_model=List[ObservationResponse])
def get_field_observations(field_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    obs = db.query(FieldObservation).filter(FieldObservation.field_id == field_id).order_by(FieldObservation.observed_at.desc()).all()
    return [
        ObservationResponse(
            id=o.id,
            field_id=o.field_id,
            observation_type=o.observation_type,
            description=o.description,
            severity=o.severity,
            observed_at=o.observed_at.isoformat() if o.observed_at else "",
            photos=o.photos or []
        ) for o in obs
    ]

@router.post("/fields/{field_id}/observations", response_model=ObservationResponse)
def create_field_observation(field_id: str, req: ObservationCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    obs = FieldObservation(
        organisation_id=field.organisation_id,
        field_id=field.id,
        observed_by=user.id,
        observation_type=req.observation_type,
        description=req.description,
        severity=req.severity,
        latitude=req.latitude,
        longitude=req.longitude,
        photos=req.photos or []
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return ObservationResponse(
        id=obs.id,
        field_id=obs.field_id,
        observation_type=obs.observation_type,
        description=obs.description,
        severity=obs.severity,
        observed_at=obs.observed_at.isoformat(),
        photos=obs.photos or []
    )
