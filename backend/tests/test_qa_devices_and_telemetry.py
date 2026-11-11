import uuid
import time
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
    base_seq = int(time.time() * 10) % 10000000 + 1000
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "schema_version": "1.0",
        "device_id": dev_uuid,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": base_seq + 1,
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
            "sequence": base_seq + 2,
            "measurements": [
                {"type": "battery_voltage", "value": 3.92, "unit": "V"}
            ]
        },
        {
            "event_id": str(uuid.uuid4()),
            "schema_version": "1.0",
            "device_id": dev_uuid,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "sequence": base_seq + 3,
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

def test_tc_dev_004_telemetry_deduplication_range_validation_and_no_fabricated_data():
    """Verify event_id deduplication, physical sensor range validation, and strict absence of fake demo data."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    # Register new clean device
    uid = f"esp32-range-{uuid.uuid4().hex[:6]}"
    dev_resp = client.post("/api/v1/devices", json={
        "farm_id": farm_id,
        "device_uid": uid,
        "name": "Validation Probe",
        "device_type": "esp32_sensor_node",
        "hardware_version": "v1.0",
        "firmware_version": "1.0.0"
    })
    device_id = dev_resp.json()["id"]

    # 1. Verify empty measurements returns [] instead of fabricated demo points
    empty_resp = client.get(f"/api/v1/measurements?device_id={device_id}")
    assert empty_resp.status_code == 200
    assert empty_resp.json() == []

    # 2. Ingest telemetry with out-of-range moisture value (250%)
    event_id = str(uuid.uuid4())
    t_payload = {
        "event_id": event_id,
        "schema_version": "1.0",
        "device_id": device_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": 1,
        "measurements": [
            {"type": "soil_moisture", "value": 250.0, "unit": "%"} # Invalid physical value
        ]
    }
    first_resp = client.post("/api/v1/telemetry", json=t_payload)
    assert first_resp.status_code == 202
    assert first_resp.json()["status"] == "persisted_and_processed"

    # Verify invalid value was flagged with quality_score = 0.0
    m_resp = client.get(f"/api/v1/measurements?device_id={device_id}")
    assert m_resp.status_code == 200
    m_list = m_resp.json()
    assert len(m_list) == 1
    assert m_list[0]["quality_score"] == 0.0

    # 3. Duplicate event_id ingestion must be deduplicated
    dup_resp = client.post("/api/v1/telemetry", json=t_payload)
    assert dup_resp.status_code == 202
    assert dup_resp.json()["status"] == "already_ingested_duplicate"

    # Measurement count must still be 1 (no duplicate insertion)
    m_resp2 = client.get(f"/api/v1/measurements?device_id={device_id}")
    assert len(m_resp2.json()) == 1

def test_tc_dev_005_mqtt_consumer_unknown_device_rejection_and_live_safety_persistence():
    """Verify MQTT consumer rejects unknown/mismatched devices and persists live E-stop state."""
    from app.services.mqtt_consumer import process_telemetry_message
    from app.core.database import SessionLocal
    from app.models.entities import Device
    import json

    # 1. Unknown device UID must be rejected (return False)
    unknown_topic = "tnx/a0000000-0000-0000-0000-000000000001/farm/c0000000-0000-0000-0000-000000000001/device/unknown-uid-9999/telemetry"
    unknown_payload = json.dumps({"event_id": str(uuid.uuid4()), "measurements": [{"type": "soil_moisture", "value": 32.0}]})
    assert process_telemetry_message(unknown_topic, unknown_payload) is False

    # 2. Known provisioned device
    db = SessionLocal()
    try:
        dev = db.query(Device).filter(Device.device_uid == "esp32-node-001").first()
        assert dev is not None

        # Telemetry containing emergency_stop = True and pump_running = True
        telemetry_event_id = str(uuid.uuid4())
        valid_topic = f"tnx/{dev.organisation_id}/farm/{dev.farm_id}/device/{dev.device_uid}/telemetry"
        valid_payload = json.dumps({
            "event_id": telemetry_event_id,
            "emergency_stop": True,
            "pump_running": False,
            "battery": 88.5,
            "measurements": [{"type": "soil_moisture", "value": 45.2, "unit": "%"}]
        })
        success = process_telemetry_message(valid_topic, valid_payload)
        assert success is True

        db.refresh(dev)
        # Verify safety state was persisted in device.config
        assert dev.config.get("emergency_stop_active") is True
        assert dev.battery_level_pct == 88.5

        # Duplicate event_id should succeed gracefully without re-persisting
        assert process_telemetry_message(valid_topic, valid_payload) is True
    finally:
        db.close()

def test_tc_dev_006_device_provisioning_credential_lifecycle():
    """Verify device-specific token generation, rotation, and revocation lifecycle."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    reg_resp = client.post("/api/v1/devices", json={
        "farm_id": farm_id,
        "device_uid": f"esp32-cred-{uuid.uuid4().hex[:6]}",
        "name": "Secure Node",
        "device_type": "esp32_sensor_node",
        "hardware_version": "v1.0",
        "firmware_version": "1.0.0"
    })
    dev_id = reg_resp.json()["id"]

    # Provision device -> generates unique token and sets status to pending_first_connect
    prov_resp = client.post(f"/api/v1/devices/{dev_id}/provision")
    assert prov_resp.status_code == 200
    pdata = prov_resp.json()
    assert "device_token" in pdata
    assert pdata["device_token"].startswith("tnx_dev_")
    assert pdata["connection_status"] == "pending_first_connect"
    old_token = pdata["device_token"]

    # Rotate credentials
    rot_resp = client.post(f"/api/v1/devices/{dev_id}/rotate-credentials")
    assert rot_resp.status_code == 200
    rdata = rot_resp.json()
    assert rdata["device_token"] != old_token

    # Revoke device
    rev_resp = client.post(f"/api/v1/devices/{dev_id}/revoke")
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "revoked"

    # Cannot rotate on revoked device
    fail_rot = client.post(f"/api/v1/devices/{dev_id}/rotate-credentials")
    assert fail_rot.status_code == 400

def test_tc_dev_007_http_telemetry_token_auth_and_sequence_replay():
    """Verify HTTP telemetry ingestion enforces token authentication and detects sequence replay attacks."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    # Register and provision a new device with token
    reg_resp = client.post("/api/v1/devices", json={
        "farm_id": farm_id,
        "device_uid": f"esp32-auth-{uuid.uuid4().hex[:6]}",
        "name": "Auth Probe",
        "device_type": "esp32_sensor_node"
    })
    dev_id = reg_resp.json()["id"]
    prov_resp = client.post(f"/api/v1/devices/{dev_id}/provision")
    token = prov_resp.json()["device_token"]

    t_payload = {
        "event_id": str(uuid.uuid4()),
        "device_id": dev_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": 100,
        "measurements": [{"type": "soil_moisture", "value": 38.5, "unit": "%"}]
    }

    # 1. Missing token -> 401 Unauthorized
    resp_no_token = client.post("/api/v1/telemetry", json=t_payload)
    assert resp_no_token.status_code == 401

    # 2. Invalid token -> 401 Unauthorized
    resp_bad_token = client.post("/api/v1/telemetry", json=t_payload, headers={"X-Device-Token": "bad-token"})
    assert resp_bad_token.status_code == 401

    # 3. Valid token -> 202 Accepted
    resp_good = client.post("/api/v1/telemetry", json=t_payload, headers={"X-Device-Token": token})
    assert resp_good.status_code == 202
    assert resp_good.json()["status"] == "persisted_and_processed"

    # 4. Replay sequence attack (sequence 100 <= 100) -> 400 Bad Request
    t_replay = {
        "event_id": str(uuid.uuid4()),
        "device_id": dev_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": 100,
        "measurements": [{"type": "soil_moisture", "value": 39.0, "unit": "%"}]
    }
    resp_replay = client.post("/api/v1/telemetry", json=t_replay, headers={"X-Device-Token": token})
    assert resp_replay.status_code == 400
    assert "Replay detected" in resp_replay.json()["detail"]

    # 5. Higher sequence (sequence 101 > 100) -> 202 Accepted
    t_next = {
        "event_id": str(uuid.uuid4()),
        "device_id": dev_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "sequence": 101,
        "measurements": [{"type": "soil_moisture", "value": 39.5, "unit": "%"}]
    }
    resp_next = client.post("/api/v1/telemetry", json=t_next, headers={"X-Device-Token": token})
    assert resp_next.status_code == 202




