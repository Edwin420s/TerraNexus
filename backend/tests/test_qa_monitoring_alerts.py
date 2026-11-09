import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_alert_001_alert_rules_lifecycle():
    """Verify alert rule creation with condition operators and thresholds."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]
    rule_name = f"Crit Low Moisture {uuid.uuid4().hex[:4]}"

    rule_resp = client.post("/api/v1/alert-rules", json={
        "farm_id": farm_id,
        "name": rule_name,
        "rule_type": "threshold",
        "measurement_type": "soil_moisture",
        "conditions": {"operator": "<", "threshold": 15.0},
        "severity": "critical"
    })
    assert rule_resp.status_code == 200
    assert rule_resp.json()["name"] == rule_name

    # List alert rules
    rules = client.get("/api/v1/alert-rules").json()
    assert len(rules) > 0

def test_tc_alert_002_alerts_acknowledgement_and_resolution():
    """Verify alert querying, state transition from active to acknowledged and resolved."""
    alerts = client.get("/api/v1/alerts").json()
    assert len(alerts) > 0
    alert_id = alerts[0]["id"]

    # Acknowledge alert (no request body)
    ack_resp = client.post(f"/api/v1/alerts/{alert_id}/ack")
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ok"

    # Resolve alert
    res_resp = client.post(f"/api/v1/alerts/{alert_id}/resolve?notes=Resolved+by+irrigation")
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "ok"

def test_tc_alert_003_notifications_listing():
    """Verify in-app notification querying."""
    notif_resp = client.get("/api/v1/notifications")
    assert notif_resp.status_code == 200
    assert isinstance(notif_resp.json(), list)
