import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_irrigation_zones_and_safe_control():
    # 1. Fetch zones
    zones_resp = client.get("/api/v1/irrigation/zones")
    assert zones_resp.status_code == 200
    zones = zones_resp.json()
    assert len(zones) > 0
    zone_id = zones[0]["id"]

    # 2. Trigger safe irrigation start (returns dispatched awaiting hardware ACK)
    start_resp = client.post("/api/v1/irrigation/control/start", json={
        "zone_id": zone_id,
        "duration_minutes": 20
    })
    assert start_resp.status_code == 200
    event_data = start_resp.json()
    assert event_data["status"] == "dispatched"
    assert event_data["scheduled_duration_minutes"] == 20

    # 3. Stop irrigation (returns stopping awaiting hardware ACK)
    stop_resp = client.post("/api/v1/irrigation/control/stop", json={
        "zone_id": zone_id,
        "reason": "target_reached"
    })
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "stopping"

def test_operations_tasks():
    # List tasks
    tasks_resp = client.get("/api/v1/tasks")
    assert tasks_resp.status_code == 200
    tasks = tasks_resp.json()
    assert len(tasks) > 0
    task_id = tasks[0]["id"]

    # Update task
    upd_resp = client.patch(f"/api/v1/tasks/{task_id}", json={
        "status": "completed"
    })
    assert upd_resp.status_code == 200
    assert upd_resp.json()["status"] == "completed"
