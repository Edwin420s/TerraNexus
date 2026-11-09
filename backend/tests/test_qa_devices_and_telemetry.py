import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_dev_001_device_registry_and_provisioning():
    """Verify device registration and provisioning handshake."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    mac = f"A4:CF:12:{uuid.uuid4().hex[:2].upper()}:{uuid.uuid4().hex[:2].upper()}:{uuid.uuid4().hex[:2].upper()}"

    dev_resp = client.post("/api/v1/devices", json={
        "farm_id": farm_id,
        "device_uid": mac,
        "name": "QA Edge Node 42",
        "device_type": "esp32_sensor_node",
        "hardware_version": "ESP32-WROOM-32D",
        "firmware_version": "1.2.0"
    })
    assert dev_resp.status_code == 200
    device_data = dev_resp.json()
    device_id = device_data["id"]
    assert device_data["device_uid"] == mac

    # Provision device (no request body required)
    prov_resp = client.post(f"/api/v1/devices/{device_id}/provision")
    assert prov_resp.status_code == 200
    assert prov_resp.json()["status"] == "provisioned"

def test_tc_dev_002_sensor_channel_configuration():
    """Verify attaching calibrated sensor channel to edge node."""
    devices = client.get("/api/v1/devices").json()
    device_id = devices[0]["id"]

    sensor_resp = client.post("/api/v1/sensors", json={
        "device_id": device_id,
        "sensor_index": 1,
        "sensor_code": f"SOIL_{uuid.uuid4().hex[:4].upper()}",
        "measurement_type_code": "soil_moisture",
        "depth_cm": 15.0,
        "unit": "%"
    })
    assert sensor_resp.status_code == 200
    assert sensor_resp.json()["device_id"] == device_id

    # List sensors
    sensors = client.get("/api/v1/sensors").json()
    assert len(sensors) > 0

def test_tc_telem_001_canonical_telemetry_and_batch_ingestion():
    """Verify single and batch canonical telemetry envelope processing."""
    devices = client.get("/api/v1/devices").json()
    device_id = devices[0]["id"]
    dev_uuid = str(uuid.UUID(device_id)) if "-" in device_id else str(uuid.uuid4())

    # 1. Single ingestion
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "schema_version": "1.0",
        "device_id": dev_uuid,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": 501,
        "measurements": [
            {"type": "soil_moisture", "value": 29.8, "unit": "%", "depth_cm": 15.0},
            {"type": "ambient_temp", "value": 22.4, "unit": "°C"},
            {"type": "ambient_humidity", "value": 68.0, "unit": "%"}
        ]
    }
    resp = client.post("/api/v1/telemetry", json=payload)
    assert resp.status_code == 202
    assert resp.json()["status"] == "persisted_and_processed"

    # 2. Batch ingestion (list of envelopes)
    batch_payload = [
        {
            "event_id": str(uuid.uuid4()),
            "schema_version": "1.0",
            "device_id": dev_uuid,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "sequence": 502,
            "measurements": [
                {"type": "battery_voltage", "value": 3.92, "unit": "V"}
            ]
        },
        {
            "event_id": str(uuid.uuid4()),
            "schema_version": "1.0",
            "device_id": dev_uuid,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "sequence": 503,
            "measurements": [
                {"type": "soil_moisture", "value": 30.1, "unit": "%", "depth_cm": 30.0}
            ]
        }
    ]
    batch_resp = client.post("/api/v1/telemetry/batch", json=batch_payload)
    assert batch_resp.status_code == 202
    assert len(batch_resp.json()) == 2

    # 3. Query persisted measurements
    m_resp = client.get(f"/api/v1/measurements?device_id={device_id}&limit=10")
    assert m_resp.status_code == 200
    measurements = m_resp.json()
    assert len(measurements) > 0

def test_tc_dev_003_device_command_dispatch_and_ack():
    """Verify device command queueing, state transitions, and execution acknowledgement."""
    devices = client.get("/api/v1/devices").json()
    device_id = devices[0]["id"]

    cmd_resp = client.post(f"/api/v1/devices/{device_id}/commands", json={
        "command_type": "turn_on",
        "payload": {"channels": ["GPIO34", "GPIO35"]},
        "priority": 2
    })
    assert cmd_resp.status_code == 200
    cmd_data = cmd_resp.json()
    assert cmd_data["status"] == "dispatched"
    cmd_id = cmd_data["id"]

    # Acknowledge command execution from edge device
    ack_resp = client.post(f"/api/v1/devices/commands/{cmd_id}/ack", json={
        "status": "acknowledged",
        "error_message": None
    })
    assert ack_resp.status_code == 200
    assert ack_resp.json()["new_status"] == "acknowledged"
