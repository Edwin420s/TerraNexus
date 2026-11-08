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
