import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_sec_001_sql_injection_defense():
    """Verify parameterized queries withstand aggressive SQL injection payloads."""
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1 UNION SELECT null, null, null--",
        "admin'--",
        "' OR 1=1#"
    ]

    for payload in sql_payloads:
        # Probe query parameters
        resp = client.get(f"/api/v1/measurements?device_id={payload}")
        assert resp.status_code in (200, 400, 422)
        if resp.status_code == 200:
            assert isinstance(resp.json(), list)

        # Probe login
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "injected@example.com",
            "password": payload
        })
        assert login_resp.status_code in (400, 401, 422)

def test_tc_sec_002_xss_payload_neutralization():
    """Verify Cross-Site Scripting (XSS) payloads are stored safely as text without execution risk."""
    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]

    xss_payload = "<script>alert('XSS_ATTACK_VECTOR');</script>"
    resp = client.post(f"/api/v1/fields/{field_id}/observations", json={
        "observation_type": "scouting_xss_test",
        "description": xss_payload,
        "severity": "low"
    })
    assert resp.status_code == 200
    obs_id = resp.json()["id"]

    # Verify query returns safe JSON serialization
    obs_list = client.get(f"/api/v1/fields/{field_id}/observations").json()
    matched = [o for o in obs_list if o["id"] == obs_id]
    assert len(matched) == 1
    assert xss_payload in matched[0]["description"]

def test_tc_sec_003_malformed_json_fuzzing():
    """Verify resilience against malformed and corrupted JSON payloads."""
    headers = {"Content-Type": "application/json"}
    bad_payloads = [
        b"{",
        b'{"device_id": }',
        b'{"measurements": [1, 2, "broken"',
        b""
    ]
    for bad in bad_payloads:
        resp = client.post("/api/v1/telemetry", content=bad, headers=headers)
        assert resp.status_code in (400, 422)
