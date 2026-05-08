from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ContextName = Literal[
    "developer/default",
    "private/default",
    "family/default",
    "trading/default",
]

DEFAULT_CONTEXT_NAME: ContextName = "developer/default"
KNOWN_CONTEXTS: set[str] = {
    "developer/default",
    "private/default",
    "family/default",
    "trading/default",
}


class Context(BaseModel):
    """Execution boundary for events, cells, and memory."""

    name: ContextName = DEFAULT_CONTEXT_NAME
    metadata: dict[str, Any] = Field(default_factory=dict)

    def as_event_context(self) -> dict[str, Any]:
        return {"name": self.name, **self.metadata}
