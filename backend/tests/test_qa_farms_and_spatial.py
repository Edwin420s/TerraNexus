import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_farm_001_farm_lifecycle():
    """Verify farm creation, spatial metadata, and retrieval."""
    unique_name = f"QA Test Farm {uuid.uuid4().hex[:6]}"
    create_resp = client.post("/api/v1/farms", json={
        "name": unique_name,
        "area_hectares": 45.0,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[36.0, -0.3], [36.1, -0.3], [36.1, -0.2], [36.0, -0.2], [36.0, -0.3]]]
        }
    })
    assert create_resp.status_code == 200
    farm_data = create_resp.json()
    farm_id = farm_data["id"]
    assert farm_data["name"] == unique_name

    # Fetch farm by ID
    get_resp = client.get(f"/api/v1/farms/{farm_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == farm_id

    # Nonexistent farm
    fake_id = str(uuid.uuid4())
    bad_resp = client.get(f"/api/v1/farms/{fake_id}")
    assert bad_resp.status_code == 404

def test_tc_farm_002_field_creation():
    """Verify field plot attachment to farm."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    field_name = f"Plot {uuid.uuid4().hex[:4]} - Maize"
    field_resp = client.post("/api/v1/fields", json={
        "farm_id": farm_id,
        "name": field_name,
        "area_hectares": 12.5,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[36.01, -0.28], [36.05, -0.28], [36.05, -0.25], [36.01, -0.25], [36.01, -0.28]]]
        }
    })
    assert field_resp.status_code == 200
    field_data = field_resp.json()
    field_id = field_data["id"]
    assert field_data["farm_id"] == farm_id

    # Query field by ID
    get_field = client.get(f"/api/v1/fields/{field_id}")
    assert get_field.status_code == 200
    assert get_field.json()["name"] == field_name

def test_tc_farm_003_field_observations():
    """Verify creating and retrieving scouting observations with photo metadata."""
    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]

    obs_resp = client.post(f"/api/v1/fields/{field_id}/observations", json={
        "observation_type": "pest_scouting",
        "description": "Fall armyworm detected on juvenile maize foliage.",
        "severity": "medium",
        "latitude": -0.275,
        "longitude": 36.023,
        "photos": ["https://storage.terranexus.org/photos/obs-101.jpg"]
    })
    assert obs_resp.status_code == 200
    obs_data = obs_resp.json()
    assert obs_data["field_id"] == field_id
    assert obs_data["severity"] == "medium"

    # Query observations for this field
    obs_list = client.get(f"/api/v1/fields/{field_id}/observations")
    assert obs_list.status_code == 200
    assert len(obs_list.json()) > 0
