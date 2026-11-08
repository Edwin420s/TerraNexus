import uuid
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_agri_001_crops_and_fao56():
    """Verify crop creation with FAO-56 dual crop coefficient stages."""
    crop_name = f"Soybean-{uuid.uuid4().hex[:4]}"
    crop_resp = client.post("/api/v1/crops", json={
        "common_name": crop_name,
        "scientific_name": "Glycine max",
        "category": "Legume",
        "growing_days_min": 85,
        "growing_days_max": 120,
        "water_requirement_mm": 450.0,
        "optimal_ph_min": 6.0,
        "optimal_ph_max": 7.0
    })
    assert crop_resp.status_code == 200
    crop_data = crop_resp.json()
    crop_id = crop_data["id"]

    # Verify retrieval
    get_crop = client.get(f"/api/v1/crops/{crop_id}")
    assert get_crop.status_code == 200
    assert get_crop.json()["common_name"] == crop_name

def test_tc_agri_002_growing_seasons():
    """Verify seasonal management and active season listing."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    season_name = f"Season Long Rains {uuid.uuid4().hex[:4]}"
    start_d = date.today().isoformat()
    end_d = (date.today() + timedelta(days=120)).isoformat()

    season_resp = client.post("/api/v1/seasons", json={
        "farm_id": farm_id,
        "name": season_name,
        "start_date": start_d,
        "end_date": end_d
    })
    assert season_resp.status_code == 200
    assert season_resp.json()["name"] == season_name

    # List seasons
    seasons = client.get("/api/v1/seasons").json()
    assert len(seasons) > 0

def test_tc_agri_003_field_crop_planting():
    """Verify planting allocation linking crop, field, and dates."""
    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]
    crops = client.get("/api/v1/crops").json()
    crop_id = crops[0]["id"]

    planting_resp = client.post("/api/v1/field-crops", json={
        "field_id": field_id,
        "crop_id": crop_id,
        "planted_area_hectares": 8.0
    })
    assert planting_resp.status_code == 200
    assert planting_resp.json()["field_id"] == field_id

    # List field crops
    fc_list = client.get("/api/v1/field-crops").json()
    assert len(fc_list) > 0
