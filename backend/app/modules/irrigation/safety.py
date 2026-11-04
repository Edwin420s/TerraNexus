from dataclasses import dataclass
from datetime import datetime, timezone
from app.core.errors import SafetyInterlockError

@dataclass(frozen=True)
class ActuationContext:
    actor_authorized: bool
    device_trusted: bool
    device_online: bool
    local_interlock_ready: bool
    emergency_stop_active: bool
    water_available: bool
    pump_fault: bool
    command_expires_at: datetime
    max_runtime_seconds: int
    requested_runtime_seconds: int


def validate_actuation(ctx: ActuationContext) -> None:
    """Server-side preflight only. Device-local interlocks remain authoritative."""
    checks = [
        (ctx.actor_authorized, "actor is not authorised"),
        (ctx.device_trusted, "device identity is not trusted"),
        (ctx.device_online, "device is offline"),
        (ctx.local_interlock_ready, "device safety interlock is not ready"),
        (not ctx.emergency_stop_active, "emergency stop is active"),
        (ctx.water_available, "water availability is not confirmed"),
        (not ctx.pump_fault, "pump fault is active"),
        (ctx.command_expires_at > datetime.now(timezone.utc), "command has expired"),
        (0 < ctx.requested_runtime_seconds <= ctx.max_runtime_seconds, "requested runtime exceeds configured limit"),
    ]
    for passed, reason in checks:
        if not passed:
            raise SafetyInterlockError(reason)
