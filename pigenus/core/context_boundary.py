from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import Context
from pigenus.schemas.base import utc_now
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform_adapters import context_to_room
from pigenus.storage.repositories import DecisionRepository


@dataclass(frozen=True)
class ContextBoundaryDecision:
    """Decision returned by the minimal context boundary engine."""

    cell_id: str
    context: str
    room_id: str
    protection_level: str
    allowed: bool
    reason: str


class ContextBoundaryEngine:
    """Checks whether a cell may process an event in a given context."""

    def check(self, *, cell: CellSpec, context: dict[str, Any]) -> ContextBoundaryDecision:
        validated = Context.model_validate(context)
        room = context_to_room(validated)
        allowed_contexts = set(cell.allowed_contexts)
        allowed = "*" in allowed_contexts or validated.name in allowed_contexts
        return ContextBoundaryDecision(
            cell_id=cell.cell_id,
            context=validated.name,
            room_id=room.id,
            protection_level=room.protection_level.value,
            allowed=allowed,
            reason="context_allowed" if allowed else "context_not_allowed",
        )

    def require_allowed(self, *, cell: CellSpec, context: dict[str, Any]) -> None:
        decision = self.check(cell=cell, context=context)
        if not decision.allowed:
            raise PermissionError(
                f"{decision.cell_id} cannot process context {decision.context}: {decision.reason}"
            )


class ContextBoundaryDecisionLogger:
    """Persists context boundary decisions through the durable decision log."""

    def __init__(self, repository: DecisionRepository) -> None:
        self.repository = repository

    def add(self, decision: ContextBoundaryDecision) -> DecisionRecord:
        record = context_boundary_decision_to_record(decision)
        self.repository.add(record)
        return record


def context_boundary_decision_to_record(decision: ContextBoundaryDecision) -> DecisionRecord:
    """Convert a context boundary decision to a durable prototype decision record."""

    data = asdict(decision)
    return DecisionRecord(
        decision_type="context_boundary",
        context={"name": decision.context},
        subject_id=f"{decision.cell_id}:{decision.context}",
        actor=decision.cell_id,
        reason=decision.reason,
        source="context_boundary_preview",
        created_at=utc_now(),
        details={
            "context_boundary": data,
            "allowed": decision.allowed,
            "room_id": decision.room_id,
            "protection_level": decision.protection_level,
        },
    )
