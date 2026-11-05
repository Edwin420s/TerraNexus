import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_reporting_endpoints():
    # Farm report
    r_farm = client.get("/api/v1/reports/farm")
    assert r_farm.status_code == 200
    data = r_farm.json()
    assert "summary_metrics" in data
    assert "trends" in data

    # Irrigation report
    r_irr = client.get("/api/v1/reports/irrigation")
    assert r_irr.status_code == 200
    data_irr = r_irr.json()
    assert "summary_metrics" in data_irr

def test_admin_and_developer_endpoints():
    # Admin system status
    r_status = client.get("/api/v1/admin/system-status")
    assert r_status.status_code == 200
    assert r_status.json()["status"] == "healthy"

    # Admin audit logs
    r_audit = client.get("/api/v1/admin/audit")
    assert r_audit.status_code == 200
    assert len(r_audit.json()) > 0

    # Developer applications
    r_apps = client.get("/api/v1/developer/applications")
    assert r_apps.status_code == 200
    assert len(r_apps.json()) > 0

    # Developer webhooks
    r_wh = client.get("/api/v1/developer/webhooks")
    assert r_wh.status_code == 200
    assert len(r_wh.json()) > 0
