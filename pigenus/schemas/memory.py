from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from pigenus.schemas.base import new_id, utc_now
from pigenus.schemas.context import Context

MemoryStatus = Literal[
    "fresh",
    "active",
    "watch",
    "stale",
    "dormant",
    "dead",
    "fossil",
    "canonical",
]


class MemoryObject(BaseModel):
    """Structured memory object managed by the local PiGenus core."""

    memory_id: str = Field(default_factory=lambda: new_id("mem"))
    memory_type: str
    context: dict[str, Any] = Field(default_factory=dict)
    status: MemoryStatus = "fresh"
    content: dict[str, Any] = Field(default_factory=dict)
    human_summary: str
    importance: float = 0.5
    confidence: float = 0.5
    created_at: datetime = Field(default_factory=utc_now)
    last_used_at: datetime | None = None
    last_validated_at: datetime | None = None
    review_due_at: datetime | None = None
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_context_contract(self) -> MemoryObject:
        Context.model_validate(self.context)
        return self
