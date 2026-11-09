import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_report_001_farm_operational_reports():
    """Verify aggregated farm operational report generation."""
    farms = client.get("/api/v1/farms").json()
    farm_id = farms[0]["id"]

    resp = client.get(f"/api/v1/reports/farm?farm_id={farm_id}")
    assert resp.status_code == 200
    report = resp.json()
    assert "summary_metrics" in report
    assert "trends" in report
    assert report["summary_metrics"]["total_farms"] >= 1

def test_tc_report_002_irrigation_efficiency_reports():
    """Verify irrigation water use efficiency report."""
    resp = client.get("/api/v1/reports/irrigation")
    assert resp.status_code == 200
    report = resp.json()
    assert "summary_metrics" in report
    assert "trends" in report

def test_tc_admin_001_audit_log_and_system_status():
    """Verify immutable audit log and super-admin system diagnostics."""
    # System status
    status_resp = client.get("/api/v1/admin/system-status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["status"] == "healthy"
    assert "components" in status_data
    assert "database" in status_data["components"]

    # Audit log
    audit_resp = client.get("/api/v1/admin/audit")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert isinstance(logs, list)

    # Admin users list
    users_resp = client.get("/api/v1/admin/users")
    assert users_resp.status_code == 200
    users = users_resp.json()
    assert len(users) > 0
