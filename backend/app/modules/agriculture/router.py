from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, get_user_organisation_ids, get_current_user_organisation_id, require_admin
from app.models.entities import User, Crop, CropVariety, GrowingSeason, FieldCrop, Farm, Field

router = APIRouter(prefix="", tags=["agriculture"])

class CropResponse(BaseModel):
    id: str
    common_name: str
    scientific_name: Optional[str]
    category: str
    growing_days_min: Optional[int]
    growing_days_max: Optional[int]
    water_requirement_mm: Optional[float]
    optimal_ph_min: Optional[float]
    optimal_ph_max: Optional[float]

class CropCreateRequest(BaseModel):
    common_name: str
    scientific_name: Optional[str] = None
    category: str
    growing_days_min: Optional[int] = None
    growing_days_max: Optional[int] = None
    water_requirement_mm: Optional[float] = None
    optimal_ph_min: Optional[float] = None
    optimal_ph_max: Optional[float] = None

class SeasonResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    start_date: str
    end_date: Optional[str]
    status: str

class SeasonCreateRequest(BaseModel):
    farm_id: str
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class FieldCropResponse(BaseModel):
    id: str
    field_id: str
    crop_id: str
    crop_name: str
    planting_date: str
    planted_area_hectares: Optional[float]
    status: str

class FieldCropCreateRequest(BaseModel):
    field_id: str
    crop_id: str
    variety_id: Optional[str] = None
    season_id: Optional[str] = None
    planted_area_hectares: Optional[float] = None
    planting_date: Optional[str] = None

@router.get("/crops", response_model=List[CropResponse])
def list_crops(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    crops = db.query(Crop).filter(Crop.is_archived == False).all()
    return [
        CropResponse(
            id=c.id,
            common_name=c.common_name,
            scientific_name=c.scientific_name,
            category=c.category,
            growing_days_min=c.growing_days_min,
            growing_days_max=c.growing_days_max,
            water_requirement_mm=float(c.water_requirement_mm) if c.water_requirement_mm is not None else None,
            optimal_ph_min=float(c.optimal_ph_min) if c.optimal_ph_min is not None else None,
            optimal_ph_max=float(c.optimal_ph_max) if c.optimal_ph_max is not None else None
        ) for c in crops
    ]

@router.post("/crops", response_model=CropResponse)
def create_crop(req: CropCreateRequest, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    crop = Crop(
        common_name=req.common_name,
        scientific_name=req.scientific_name,
        category=req.category,
        growing_days_min=req.growing_days_min,
        growing_days_max=req.growing_days_max,
        water_requirement_mm=req.water_requirement_mm,
        optimal_ph_min=req.optimal_ph_min,
        optimal_ph_max=req.optimal_ph_max
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return CropResponse(
        id=crop.id,
        common_name=crop.common_name,
        scientific_name=crop.scientific_name,
        category=crop.category,
        growing_days_min=crop.growing_days_min,
        growing_days_max=crop.growing_days_max,
        water_requirement_mm=float(crop.water_requirement_mm) if crop.water_requirement_mm is not None else None,
        optimal_ph_min=float(crop.optimal_ph_min) if crop.optimal_ph_min is not None else None,
        optimal_ph_max=float(crop.optimal_ph_max) if crop.optimal_ph_max is not None else None
    )

@router.get("/crops/{crop_id}", response_model=CropResponse)
def get_crop(crop_id: str, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return CropResponse(
        id=crop.id,
        common_name=crop.common_name,
        scientific_name=crop.scientific_name,
        category=crop.category,
        growing_days_min=crop.growing_days_min,
        growing_days_max=crop.growing_days_max,
        water_requirement_mm=float(crop.water_requirement_mm) if crop.water_requirement_mm is not None else None,
        optimal_ph_min=float(crop.optimal_ph_min) if crop.optimal_ph_min is not None else None,
        optimal_ph_max=float(crop.optimal_ph_max) if crop.optimal_ph_max is not None else None
    )

@router.get("/seasons", response_model=List[SeasonResponse])
def list_seasons(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    seasons = db.query(GrowingSeason).filter(GrowingSeason.organisation_id.in_(user_org_ids)).all()
    return [
        SeasonResponse(
            id=s.id,
            farm_id=s.farm_id,
            name=s.name,
            start_date=s.start_date.isoformat() if s.start_date else "",
            end_date=s.end_date.isoformat() if s.end_date else None,
            status=s.status
        ) for s in seasons
    ]

@router.post("/seasons", response_model=SeasonResponse)
def create_season(req: SeasonCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    farm = db.query(Farm).filter(Farm.id == req.farm_id, Farm.organisation_id.in_(user_org_ids)).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")

    start_dt = datetime.fromisoformat(req.start_date) if req.start_date else datetime.now(timezone.utc)
    end_dt = datetime.fromisoformat(req.end_date) if req.end_date else None
    season = GrowingSeason(
        organisation_id=farm.organisation_id,
        farm_id=req.farm_id,
        name=req.name,
        start_date=start_dt,
        end_date=end_dt,
        status="active"
    )
    db.add(season)
    db.commit()
    db.refresh(season)
    return SeasonResponse(
        id=season.id,
        farm_id=season.farm_id,
        name=season.name,
        start_date=season.start_date.isoformat(),
        end_date=season.end_date.isoformat() if season.end_date else None,
        status=season.status
    )

@router.get("/field-crops", response_model=List[FieldCropResponse])
def list_field_crops(field_id: Optional[str] = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    query = db.query(FieldCrop).filter(FieldCrop.organisation_id.in_(user_org_ids))
    if field_id:
        query = query.filter(FieldCrop.field_id == field_id)
    records = query.all()
    results = []
    for fc in records:
        crop = db.query(Crop).filter(Crop.id == fc.crop_id).first()
        crop_name = crop.common_name if crop else "Unknown"
        results.append(FieldCropResponse(
            id=fc.id,
            field_id=fc.field_id,
            crop_id=fc.crop_id,
            crop_name=crop_name,
            planting_date=fc.planting_date.isoformat() if fc.planting_date else "",
            planted_area_hectares=float(fc.planted_area_hectares) if fc.planted_area_hectares is not None else None,
            status=fc.status
        ))
    return results

@router.post("/field-crops", response_model=FieldCropResponse)
def assign_field_crop(req: FieldCropCreateRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_org_ids = get_user_organisation_ids(user, db)
    field = db.query(Field).filter(Field.id == req.field_id, Field.organisation_id.in_(user_org_ids)).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found or unauthorized")

    plant_dt = datetime.fromisoformat(req.planting_date) if req.planting_date else datetime.now(timezone.utc)
    fc = FieldCrop(
        organisation_id=field.organisation_id,
        field_id=req.field_id,
        crop_id=req.crop_id,
        variety_id=req.variety_id,
        season_id=req.season_id,
        planted_area_hectares=req.planted_area_hectares,
        planting_date=plant_dt,
        status="growing"
    )
    db.add(fc)
    db.commit()
    db.refresh(fc)
    crop = db.query(Crop).filter(Crop.id == fc.crop_id).first()
    return FieldCropResponse(
        id=fc.id,
        field_id=fc.field_id,
        crop_id=fc.crop_id,
        crop_name=crop.common_name if crop else "Unknown",
        planting_date=fc.planting_date.isoformat(),
        planted_area_hectares=float(fc.planted_area_hectares) if fc.planted_area_hectares is not None else None,
        status=fc.status
    )
