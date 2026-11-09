import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_safe_001_safety_capabilities_and_sources():
    """Verify safety capabilities reporting and water source registration."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    cap_resp = client.get("/api/v1/irrigation/safety-capabilities")
    assert cap_resp.status_code == 200
    caps = cap_resp.json()
    assert caps["device_local_interlock_required"] is True
    assert caps["status"] == "active_hardware_enforced"

    # Register water source
    source_name = f"Reservoir {uuid.uuid4().hex[:4]}"
    src_resp = client.post("/api/v1/irrigation/sources", json={
        "farm_id": farm_id,
        "name": source_name,
        "source_type": "surface_reservoir",
        "capacity_litres": 150000.0,
        "current_level_litres": 120000.0
    })
    assert src_resp.status_code == 200
    source_id = src_resp.json()["id"]

    # Verify list
    sources = client.get("/api/v1/irrigation/sources").json()
    assert any(s["id"] == source_id for s in sources)

def test_tc_safe_002_irrigation_zones_and_actuation_lifecycle():
    """Verify zone creation, safe start actuation, and stop actuation."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    sources = client.get("/api/v1/irrigation/sources").json()
    source_id = sources[0]["id"]
    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]

    # Create irrigation zone
    zone_code = f"Z_{uuid.uuid4().hex[:4].upper()}"
    zone_resp = client.post("/api/v1/irrigation/zones", json={
        "farm_id": farm_id,
        "field_id": field_id,
        "water_source_id": source_id,
        "name": f"Drip Line Block {uuid.uuid4().hex[:4]}",
        "zone_code": zone_code,
        "irrigation_method": "drip",
        "flow_rate_lpm": 45.0
    })
    assert zone_resp.status_code == 200
    zone_id = zone_resp.json()["id"]

    # Safe actuation start (10 minutes <= 30 minutes watchdog limit)
    start_resp = client.post("/api/v1/irrigation/control/start", json={
        "zone_id": zone_id,
        "duration_minutes": 10,
        "triggered_by": "manual_user"
    })
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    assert start_data["status"] == "running"

    # Safe actuation stop
    stop_resp = client.post("/api/v1/irrigation/control/stop", json={
        "zone_id": zone_id,
        "reason": "Target moisture threshold reached"
    })
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "completed"

def test_tc_safe_003_watchdog_duration_cap_enforcement():
    """Verify that requests exceeding 30 minutes (1800s) are rejected by safety preflights."""
    zones = client.get("/api/v1/irrigation/zones").json()
    zone_id = zones[0]["id"]

    resp = client.post("/api/v1/irrigation/control/start", json={
        "zone_id": zone_id,
        "duration_minutes": 120, # 120 mins = 7200s, exceeds 1800s safety limit
        "triggered_by": "manual_user"
    })
    # Preflight interlock rejects with 409 or 400
    assert resp.status_code in (400, 409, 422)

def test_tc_safe_004_nonexistent_zone_rejected():
    """Verify preflight rejects invalid zone IDs."""
    fake_zone = str(uuid.uuid4())
    resp = client.post("/api/v1/irrigation/control/start", json={
        "zone_id": fake_zone,
        "duration_minutes": 10
    })
    assert resp.status_code in (400, 404)

def test_tc_safe_005_irrigation_history_retrieval():
    """Verify audit history of irrigation actuation runs."""
    hist_resp = client.get("/api/v1/irrigation/history")
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert isinstance(history, list)
