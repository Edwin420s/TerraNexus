from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class TelemetryEnvelope(BaseModel):
    event_id: UUID
    schema_version: str = "1.0"
    device_id: UUID
    observed_at: datetime
    sent_at: datetime | None = None
    sequence: int = Field(ge=0)
    measurements: list[dict[str, Any]] = Field(min_length=1, max_length=500)

    @field_validator("observed_at", "sent_at")
    @classmethod
    def require_timezone(cls, value):
        if value is not None and value.tzinfo is None:
            raise ValueError("timestamps must include a timezone")
        return value

class TelemetryAccepted(BaseModel):
    event_id: UUID
    accepted: bool
    status: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
