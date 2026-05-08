from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from pigenus.schemas.base import utc_now

CellStatus = Literal["draft", "active", "watch", "disabled", "fossil"]


class CellSpec(BaseModel):
    """Versioned metadata that describes a PiGenus cell."""

    name: str
    version: str
    input_event_types: list[str] = Field(default_factory=list)
    output_event_types: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    allowed_contexts: list[str] = Field(default_factory=lambda: ["developer/default"])
    status: CellStatus = "active"
    fitness: float = 0.0
    created_at: datetime = Field(default_factory=utc_now)
    last_used_at: datetime | None = None
    description: str = ""

    @property
    def cell_id(self) -> str:
        return f"{self.name}@{self.version}"


class CellState(BaseModel):
    """Operational state owned by a cell, separate from core memory."""

    cell_id: str
    state: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=utc_now)
