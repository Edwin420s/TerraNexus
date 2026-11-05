import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_device_lifecycle_and_telemetry():
    # 1. Fetch devices
    dev_resp = client.get("/api/v1/devices")
    assert dev_resp.status_code == 200
    devices = dev_resp.json()
    assert len(devices) > 0
    device_id = devices[0]["id"]

    # 2. Ingest valid telemetry packet
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "schema_version": "1.0",
        "device_id": device_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": 101,
        "measurements": [
            {"type": "soil_moisture", "value": 31.4, "unit": "%", "depth_cm": 10.0},
            {"type": "ambient_temp", "value": 24.2, "unit": "°C"}
        ]
    }
    telem_resp = client.post("/api/v1/telemetry", json=payload)
    assert telem_resp.status_code == 202
    assert telem_resp.json()["status"] == "persisted_and_processed"

    # 3. Query persisted measurements
    m_resp = client.get(f"/api/v1/measurements?device_id={device_id}")
    assert m_resp.status_code == 200
    measurements = m_resp.json()
    assert len(measurements) > 0

    # 4. Dispatch device command
    cmd_resp = client.post(f"/api/v1/devices/{device_id}/commands", json={
        "command_type": "turn_on",
        "payload": {"relay_index": 1, "duration_sec": 300},
        "priority": 1
    })
    assert cmd_resp.status_code == 200
    cmd_data = cmd_resp.json()
    assert cmd_data["status"] == "dispatched"
    cmd_id = cmd_data["id"]

    # 5. Device acknowledges command
    ack_resp = client.post(f"/api/v1/devices/commands/{cmd_id}/ack", json={
        "status": "acknowledged"
    })
    assert ack_resp.status_code == 200
    assert ack_resp.json()["new_status"] == "acknowledged"
