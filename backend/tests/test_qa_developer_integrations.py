import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_intg_001_developer_applications_and_api_keys():
    """Verify developer application registration and scoped API key issuance."""
    app_name = f"AgriAnalytics Integrator {uuid.uuid4().hex[:4]}"
    resp = client.post("/api/v1/developer/applications", json={
        "name": app_name,
        "description": "External satellite vegetation index connector"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == app_name
    assert "api_key_prefix" in data

    # List developer applications
    apps_list = client.get("/api/v1/developer/applications").json()
    assert len(apps_list) > 0

def test_tc_intg_002_webhooks_registration():
    """Verify webhook subscription registration and secret generation."""
    endpoint = f"https://api.externalag.com/hooks/tnx-{uuid.uuid4().hex[:4]}"
    hook_name = f"Field Alerts Hook {uuid.uuid4().hex[:4]}"
    hook_resp = client.post("/api/v1/developer/webhooks", json={
        "name": hook_name,
        "target_url": endpoint,
        "secret_token": "whsec_terranexus_test_key",
        "event_subscriptions": ["telemetry.anomaly", "alert.critical"]
    })
    assert hook_resp.status_code == 200
    hook_data = hook_resp.json()
    assert hook_data["target_url"] == endpoint
    assert hook_data["name"] == hook_name

    # List webhooks
    hooks_list = client.get("/api/v1/developer/webhooks").json()
    assert len(hooks_list) > 0
