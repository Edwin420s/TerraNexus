import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.init_db import init_database

@pytest.fixture(autouse=True)
def setup_db():
    init_database()

client = TestClient(app)

def test_health_endpoints():
    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "ok"

    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] in ("ready", "degraded")

def test_login_and_me():
    # Login with seed admin user
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@terranexus.org",
        "password": "TerraNexus2026!"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # Verify profile
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "admin@terranexus.org"

def test_farms_and_fields():
    # List farms
    farms_resp = client.get("/api/v1/farms")
    assert farms_resp.status_code == 200
    farms = farms_resp.json()
    assert len(farms) > 0
    farm_id = farms[0]["id"]

    # Create new field
    field_resp = client.post("/api/v1/fields", json={
        "farm_id": farm_id,
        "name": "East Terrace - Wheat",
        "area_hectares": 5.0
    })
    assert field_resp.status_code == 200
    field_data = field_resp.json()
    assert field_data["name"] == "East Terrace - Wheat"

    # List fields
    fields_list = client.get(f"/api/v1/fields?farm_id={farm_id}")
    assert fields_list.status_code == 200
    assert any(f["name"] == "East Terrace - Wheat" for f in fields_list.json())
