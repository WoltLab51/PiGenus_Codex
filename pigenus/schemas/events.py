from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from pigenus.schemas.base import new_id, utc_now
from pigenus.schemas.context import Context

EventType = Literal[
    "UserInput",
    "TaskRequest",
    "MemoryProposal",
    "GuardDecision",
    "MemoryStored",
    "HumanResponse",
]

REQUIRED_PAYLOAD_KEYS: dict[str, set[str]] = {
    "TaskRequest": {"raw_text", "action"},
    "MemoryProposal": {"action", "memory_type", "content", "human_summary", "source_event_id"},
    "GuardDecision": {"action", "allowed", "reason", "blocking_cell", "source_event_id"},
    "MemoryStored": {"memory_id", "source_event_id", "proposal_event_id", "human_summary"},
    "HumanResponse": {"response", "memory_id"},
}


class Event(BaseModel):
    """Structured meaning event passed between cells."""

    event_id: str = Field(default_factory=lambda: new_id("evt"))
    object_type: EventType
    schema_version: str = "1.0"
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    created_by_cell: str
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_contract_payload(self) -> Event:
        Context.model_validate(self.context)
        required_keys = REQUIRED_PAYLOAD_KEYS.get(self.object_type, set())
        missing_keys = sorted(required_keys.difference(self.payload))
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise ValueError(f"{self.object_type} payload missing required keys: {missing}")
        return self
