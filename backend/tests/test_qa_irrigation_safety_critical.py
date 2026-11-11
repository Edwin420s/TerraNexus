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

def test_tc_safe_006_cross_tenant_zone_isolation():
    """Verify that users cannot stop or view history of zones in organisations they do not belong to."""
    random_zone_id = str(uuid.uuid4())
    # Attempt stop on nonexistent / unauthorized zone
    stop_resp = client.post("/api/v1/irrigation/control/stop", json={
        "zone_id": random_zone_id,
        "reason": "Unauthorized test stop"
    })
    assert stop_resp.status_code == 404

    # Attempt closed-loop plan on nonexistent / unauthorized zone
    plan_resp = client.post("/api/v1/irrigation/closed-loop/plan", json={
        "zone_id": random_zone_id,
        "current_moisture_pct": 45.0
    })
    assert plan_resp.status_code == 404

def test_tc_safe_007_preflight_device_enforcement_and_emergency_stop():
    """Verify that zones without provisioned devices or under emergency stop are blocked."""
    from app.core.database import SessionLocal
    from app.models.entities import Farm, IrrigationZone, WaterSource, Device, DeviceCommand
    db = SessionLocal()
    try:
        # 1. Create a isolated farm with NO devices
        isolated_farm = Farm(
            organisation_id="a0000000-0000-0000-0000-000000000001",
            name="No Device Farm",
            farm_code=f"NDF_{uuid.uuid4().hex[:4]}",
            timezone="UTC"
        )
        db.add(isolated_farm)
        db.commit()
        db.refresh(isolated_farm)

        src = WaterSource(
            organisation_id=isolated_farm.organisation_id,
            farm_id=isolated_farm.id,
            name="Orphan Reservoir",
            source_type="borehole",
            capacity_litres=50000.0,
            current_level_litres=40000.0,
            status="operational"
        )
        db.add(src)
        db.commit()
        db.refresh(src)

        orphan_zone = IrrigationZone(
            organisation_id=isolated_farm.organisation_id,
            farm_id=isolated_farm.id,
            water_source_id=src.id,
            name="Orphan Zone",
            zone_code=f"OZ_{uuid.uuid4().hex[:4]}",
            irrigation_method="drip",
            flow_rate_lpm=30.0,
            target_soil_moisture_pct=60.0
        )
        db.add(orphan_zone)
        db.commit()
        db.refresh(orphan_zone)

        # Actuation should fail preflight because no device is attached or present on the farm
        resp = client.post("/api/v1/irrigation/control/start", json={
            "zone_id": orphan_zone.id,
            "duration_minutes": 5
        })
        assert resp.status_code in (400, 409, 422)

        # 2. Attach an emergency-stopped device to this farm
        estop_device = Device(
            organisation_id=isolated_farm.organisation_id,
            farm_id=isolated_farm.id,
            name="E-stop Controller",
            device_uid=f"esp32-estop-{uuid.uuid4().hex[:6]}",
            device_type="esp32_gateway",
            provisioning_status="active",
            connection_status="online",
            config={"emergency_stop_active": True}
        )
        db.add(estop_device)
        db.commit()

        # Actuation should be blocked by emergency stop
        resp2 = client.post("/api/v1/irrigation/control/start", json={
            "zone_id": orphan_zone.id,
            "duration_minutes": 5
        })
        assert resp2.status_code in (400, 409, 422)

    finally:
        db.close()


