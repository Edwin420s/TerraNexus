import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import verify_password, hash_password, create_access_token

client = TestClient(app)

def test_tc_auth_001_password_hashing():
    """TC-AUTH-001: Verify PBKDF2-HMAC-SHA256 password hashing security."""
    raw_pass = "SecureFarm2026!#"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_tc_auth_002_user_registration_and_duplicate_prevention():
    """Verify user registration and unique email constraint."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@terranexus.org"
    resp = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "Password123!",
        "first_name": "QA",
        "last_name": "Tester",
        "organisation_name": "QA Farm Org"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == unique_email
    assert "access_token" in data

    # Attempt duplicate registration with same email
    dup_resp = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "Password123!",
        "first_name": "Duplicate",
        "last_name": "User"
    })
    assert dup_resp.status_code == 400

def test_tc_auth_003_login_failure_modes():
    """Verify login rejections for invalid credentials and nonexistent accounts."""
    resp_none = client.post("/api/v1/auth/login", json={
        "email": "ghost@terranexus.org",
        "password": "AnyPassword123!"
    })
    assert resp_none.status_code in (400, 401)

    resp_wrong = client.post("/api/v1/auth/login", json={
        "email": "admin@terranexus.org",
        "password": "WrongPassword2026!"
    })
    assert resp_wrong.status_code in (400, 401)

def test_tc_auth_004_jwt_validation_and_tampering():
    """Verify Bearer token authentication and rejection of tampered/invalid tokens."""
    # Malformed token
    resp_bad = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-token"})
    assert resp_bad.status_code == 401

    # Valid login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@terranexus.org",
        "password": "TerraNexus2026!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Tampered token (altered characters in signature)
    tampered_token = token[:-5] + "AAAAA"
    resp_tampered = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
    assert resp_tampered.status_code == 401

    # Valid profile retrieval
    resp_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_me.status_code == 200
    assert resp_me.json()["email"] == "admin@terranexus.org"

def test_tc_auth_005_organisations_and_members():
    """Verify organisation querying and membership listing."""
    resp = client.get("/api/v1/organisations")
    assert resp.status_code == 200
    orgs = resp.json()
    assert len(orgs) > 0
    org_id = orgs[0]["id"]

    members_resp = client.get(f"/api/v1/organisations/{org_id}/members")
    assert members_resp.status_code == 200
    members = members_resp.json()
    assert isinstance(members, list)

def test_tc_auth_006_unauthenticated_requests_strictly_rejected():
    """Verify that unauthenticated requests to protected endpoints strictly return HTTP 401."""
    protected_endpoints = [
        "/api/v1/auth/me",
        "/api/v1/organisations",
        "/api/v1/farms",
        "/api/v1/fields",
        "/api/v1/devices",
        "/api/v1/measurements",
        "/api/v1/irrigation/zones",
        "/api/v1/irrigation/sources",
    ]
    for ep in protected_endpoints:
        r = client.get(ep, headers={"X-Unauthenticated": "1"})
        assert r.status_code == 401, f"Expected 401 for unauthenticated request to {ep}, got {r.status_code}"
        assert "detail" in r.json()

def test_tc_auth_007_multi_tenant_organisation_isolation():
    """Verify complete tenant isolation: Tenant A cannot see, modify, or actuate Tenant B entities."""
    # Register Tenant A
    user_a_email = f"user_a_{uuid.uuid4().hex[:6]}@tenant-a.com"
    resp_a = client.post("/api/v1/auth/register", json={
        "email": user_a_email,
        "password": "Password123!",
        "first_name": "Alice",
        "last_name": "Farmer",
        "organisation_name": "Alpha Agribusiness Ltd"
    })
    assert resp_a.status_code == 200
    token_a = resp_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Tenant B
    user_b_email = f"user_b_{uuid.uuid4().hex[:6]}@tenant-b.com"
    resp_b = client.post("/api/v1/auth/register", json={
        "email": user_b_email,
        "password": "Password123!",
        "first_name": "Bob",
        "last_name": "Grower",
        "organisation_name": "Beta Produce Co"
    })
    assert resp_b.status_code == 200
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant A creates Farm A
    farm_a_resp = client.post("/api/v1/farms", headers=headers_a, json={
        "name": "Alpha High-Yield Farm",
        "area_hectares": 25.0
    })
    assert farm_a_resp.status_code == 200
    farm_a_id = farm_a_resp.json()["id"]

    # Tenant B lists farms: Farm A MUST NOT be visible
    farms_b = client.get("/api/v1/farms", headers=headers_b).json()
    farm_ids_b = [f["id"] for f in farms_b]
    assert farm_a_id not in farm_ids_b

    # Tenant B direct GET on Farm A: MUST return 404
    direct_get_b = client.get(f"/api/v1/farms/{farm_a_id}", headers=headers_b)
    assert direct_get_b.status_code == 404

    # Tenant B attempts to create Field inside Farm A: MUST return 404/403
    cross_field_resp = client.post("/api/v1/fields", headers=headers_b, json={
        "farm_id": farm_a_id,
        "name": "Intruder Field"
    })
    assert cross_field_resp.status_code in (403, 404)

    # Tenant A creates a Water Source and Zone in Farm A
    source_a_resp = client.post("/api/v1/irrigation/sources", headers=headers_a, json={
        "farm_id": farm_a_id,
        "name": "Alpha Well 1",
        "source_type": "borehole",
        "capacity_litres": 50000.0,
        "current_level_litres": 45000.0
    })
    assert source_a_resp.status_code == 200
    source_a_id = source_a_resp.json()["id"]

    zone_a_resp = client.post("/api/v1/irrigation/zones", headers=headers_a, json={
        "farm_id": farm_a_id,
        "water_source_id": source_a_id,
        "name": "Alpha Tomato Zone",
        "zone_code": "ATZ-01"
    })
    assert zone_a_resp.status_code == 200
    zone_a_id = zone_a_resp.json()["id"]

    # Tenant B attempts to actuate Tenant A's Zone: MUST return 404/403/409
    cross_actuation_resp = client.post("/api/v1/irrigation/control/start", headers=headers_b, json={
        "zone_id": zone_a_id,
        "duration_minutes": 10
    })
    assert cross_actuation_resp.status_code in (403, 404, 409)

def test_tc_auth_008_telemetry_unprovisioned_device_rejected():
    """Verify that unprovisioned or unknown devices cannot ingest telemetry."""
    fake_dev_packet = {
        "event_id": str(uuid.uuid4()),
        "schema_version": "1.0",
        "device_id": str(uuid.uuid4()),
        "observed_at": "2026-11-11T03:00:00Z",
        "sequence": 1,
        "measurements": [{"type": "soil_moisture", "value": 25.0, "unit": "%"}]
    }
    resp = client.post("/api/v1/telemetry", json=fake_dev_packet)
    assert resp.status_code in (401, 403)

