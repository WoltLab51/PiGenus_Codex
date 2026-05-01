from __future__ import annotations

from pydantic import BaseModel, Field


class WorkerCapabilitySet(BaseModel):
    capabilities: list[str] = Field(default_factory=list)

    def can_run(self, required: list[str]) -> bool:
        return set(required).issubset(set(self.capabilities))

