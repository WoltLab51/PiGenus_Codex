from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import Context


@dataclass(frozen=True)
class ContextBoundaryDecision:
    """Decision returned by the minimal context boundary engine."""

    cell_id: str
    context: str
    allowed: bool
    reason: str


class ContextBoundaryEngine:
    """Checks whether a cell may process an event in a given context."""

    def check(self, *, cell: CellSpec, context: dict[str, Any]) -> ContextBoundaryDecision:
        validated = Context.model_validate(context)
        allowed_contexts = set(cell.allowed_contexts)
        allowed = "*" in allowed_contexts or validated.name in allowed_contexts
        return ContextBoundaryDecision(
            cell_id=cell.cell_id,
            context=validated.name,
            allowed=allowed,
            reason="context_allowed" if allowed else "context_not_allowed",
        )

    def require_allowed(self, *, cell: CellSpec, context: dict[str, Any]) -> None:
        decision = self.check(cell=cell, context=context)
        if not decision.allowed:
            raise PermissionError(
                f"{decision.cell_id} cannot process context {decision.context}: {decision.reason}"
            )
