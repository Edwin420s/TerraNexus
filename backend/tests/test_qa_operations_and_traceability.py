import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_ops_001_task_lifecycle():
    """Verify task creation, status mutation, and completion."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    task_title = f"Clean Drip Filters {uuid.uuid4().hex[:4]}"

    create_resp = client.post("/api/v1/tasks", json={
        "farm_id": farm_id,
        "title": task_title,
        "description": "Inspect and backwash secondary sand filter mesh.",
        "task_type": "maintenance",
        "priority": "high",
        "due_date": date.today().isoformat()
    })
    assert create_resp.status_code == 200
    task_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "todo"

    # Mutate to in_progress
    patch_resp = client.patch(f"/api/v1/tasks/{task_id}", json={
        "status": "in_progress"
    })
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "in_progress"

    # Mutate to completed
    done_resp = client.patch(f"/api/v1/tasks/{task_id}", json={
        "status": "completed"
    })
    assert done_resp.status_code == 200
    assert done_resp.json()["status"] == "completed"

def test_tc_ops_002_equipment_registry():
    """Verify equipment asset creation and listing."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    eq_name = f"Solar Booster Pump {uuid.uuid4().hex[:4]}"

    eq_resp = client.post("/api/v1/equipment", json={
        "farm_id": farm_id,
        "name": eq_name,
        "equipment_type": "pump",
        "status": "operational",
        "operating_hours": 120.5
    })
    assert eq_resp.status_code == 200
    assert eq_resp.json()["name"] == eq_name

    # List equipment
    eq_list = client.get("/api/v1/equipment").json()
    assert len(eq_list) > 0

def test_tc_ops_003_inventory_tracking():
    """Verify warehouse input inventory creation and querying."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    item_name = f"Drip Tape 16mm {uuid.uuid4().hex[:4]}"

    inv_resp = client.post("/api/v1/inventory", json={
        "farm_id": farm_id,
        "item_name": item_name,
        "category": "irrigation_supplies",
        "quantity_on_hand": 12.0,
        "unit_of_measure": "rolls",
        "reorder_level": 3.0
    })
    assert inv_resp.status_code == 200
    assert inv_resp.json()["item_name"] == item_name

    # List inventory
    inv_list = client.get("/api/v1/inventory").json()
    assert len(inv_list) > 0

def test_tc_ops_004_harvest_traceability():
    """Verify harvest batch logging linking yield to field and crop."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]
    lot_no = f"LOT-{uuid.uuid4().hex[:6].upper()}"

    harvest_resp = client.post("/api/v1/harvest", json={
        "farm_id": farm_id,
        "field_id": field_id,
        "quantity_harvested_kg": 4500.0,
        "grade_quality": "Grade A",
        "batch_number": lot_no,
        "harvest_date": date.today().isoformat()
    })
    assert harvest_resp.status_code == 200
    assert harvest_resp.json()["batch_number"] == lot_no

    # Query harvest records
    h_list = client.get("/api/v1/harvest").json()
    assert any(h["batch_number"] == lot_no for h in h_list)
