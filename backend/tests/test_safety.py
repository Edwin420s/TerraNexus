from datetime import datetime, timedelta, timezone
import pytest
from app.modules.irrigation.safety import ActuationContext, validate_actuation
from app.core.errors import SafetyInterlockError

def valid_context(**overrides):
    values = dict(actor_authorized=True, device_trusted=True, device_online=True,
        local_interlock_ready=True, emergency_stop_active=False, water_available=True,
        pump_fault=False, command_expires_at=datetime.now(timezone.utc)+timedelta(minutes=1),
        max_runtime_seconds=300, requested_runtime_seconds=60)
    values.update(overrides)
    return ActuationContext(**values)

def test_valid_preflight_passes():
    validate_actuation(valid_context())

def test_emergency_stop_blocks():
    with pytest.raises(SafetyInterlockError):
        validate_actuation(valid_context(emergency_stop_active=True))

def test_expired_command_blocks():
    with pytest.raises(SafetyInterlockError):
        validate_actuation(valid_context(command_expires_at=datetime.now(timezone.utc)-timedelta(seconds=1)))
