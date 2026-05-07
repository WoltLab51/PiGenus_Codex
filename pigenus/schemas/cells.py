from __future__ import annotations

from pydantic import BaseModel, Field


class CellSpec(BaseModel):
    """Versioned metadata that describes a PiGenus cell."""

    name: str
    version: str
    input_event_types: list[str] = Field(default_factory=list)
    output_event_types: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    description: str = ""

    @property
    def cell_id(self) -> str:
        return f"{self.name}@{self.version}"
