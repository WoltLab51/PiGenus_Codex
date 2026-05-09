from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from pigenus.schemas.base import new_id, utc_now
from pigenus.schemas.context import Context


class DecisionRecord(BaseModel):
    """A durable record of an important system decision."""

    decision_id: str = Field(default_factory=lambda: new_id("dec"))
    decision_type: str
    context: dict[str, Any] = Field(default_factory=dict)
    subject_id: str
    actor: str
    reason: str
    source: str
    created_at: datetime = Field(default_factory=utc_now)
    details: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_context_contract(self) -> DecisionRecord:
        Context.model_validate(self.context)
        return self
