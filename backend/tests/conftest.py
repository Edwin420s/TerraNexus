import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.core.database import SessionLocal
from app.core.init_db import init_database
from app.models.entities import User, Membership, Device
from datetime import datetime, timezone

@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Ensure database tables and initial seed fixtures exist for clean CI environments."""
    init_database()

@pytest.fixture(autouse=True)
def refresh_online_devices():
    """Ensure online test devices have fresh heartbeats within the 120s safety window and pristine state."""
    db = SessionLocal()
    try:
        from sqlalchemy.orm.attributes import flag_modified
        now = datetime.now(timezone.utc)
        devices = db.query(Device).filter(
            Device.connection_status == "online",
            Device.provisioning_status.in_(("active", "provisioned"))
        ).all()
        for dev in devices:
            dev.last_heartbeat_at = now
            if isinstance(dev.config, dict):
                dev.config.pop("last_telemetry_sequence", None)
                dev.config.pop("emergency_stop_active", None)
                dev.config["device_token"] = "tnx_secret_device_token_2026"
                dev.config["local_interlock_ready"] = True
                flag_modified(dev, "config")
        db.commit()
    except Exception:
        pass
    finally:
        db.close()

@pytest.fixture(scope="session")
def admin_auth_token():
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@terranexus.org").first()
    mem = db.query(Membership).filter(Membership.user_id == admin.id).first() if admin else None
    org_id = mem.organisation_id if mem else "a0000000-0000-0000-0000-000000000001"
    token = create_access_token({"sub": admin.id, "email": admin.email, "org": org_id}) if admin else ""
    db.close()
    return token

@pytest.fixture(autouse=True)
def auto_authenticate_test_client(admin_auth_token, monkeypatch):
    """
    Ensure TestClient requests have the admin Bearer token injected by default
    across integration test suites, unless:
    - Target is a public route (/health/*, /api/v1/auth/login, /api/v1/auth/register)
    - Request explicitly specifies an Authorization header (including empty or invalid)
    - Request explicitly specifies X-Unauthenticated header
    """
    original_request = TestClient.request

    def patched_request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers")
        if headers is None:
            headers = {}
            kwargs["headers"] = headers

        # Allow tests to explicitly test unauthenticated access
        if "X-Unauthenticated" in headers:
            headers.pop("X-Unauthenticated", None)
            headers.pop("Authorization", None)
            headers.pop("authorization", None)
            return original_request(self, method, url, *args, **kwargs)

        has_auth = "Authorization" in headers or "authorization" in headers
        is_public = (
            url.startswith("/health")
            or url.startswith("/api/v1/auth/login")
            or url.startswith("/api/v1/auth/register")
            or url.startswith("/api/v1/auth/forgot-password")
            or url.startswith("/api/v1/auth/verify-email")
            or url.startswith("/docs")
            or url.startswith("/openapi.json")
            or url.startswith("/api/v1/telemetry")
        )

        if url.startswith("/api/v1/telemetry") and "X-Device-Token" not in headers and not has_auth:
            headers["X-Device-Token"] = "tnx_secret_device_token_2026"

        if not has_auth and not is_public and admin_auth_token:
            headers["Authorization"] = f"Bearer {admin_auth_token}"

        return original_request(self, method, url, *args, **kwargs)

    monkeypatch.setattr(TestClient, "request", patched_request)
