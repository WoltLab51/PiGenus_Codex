from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from pigenus.schemas.base import new_id, utc_now


class Event(BaseModel):
    """Structured meaning event passed between cells."""

    event_id: str = Field(default_factory=lambda: new_id("evt"))
    object_type: str
    schema_version: str = "1.0"
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    created_by_cell: str
    payload: dict[str, Any] = Field(default_factory=dict)
