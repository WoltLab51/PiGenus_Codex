from __future__ import annotations

from typing import Any

from pigenus.schemas.context import Context
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import GovernanceDecision
from pigenus.storage.repositories import DecisionRepository


ROOM_ID_TO_CONTEXT_NAME: dict[str, str] = {
    "room_developer": "developer/default",
    "room_private": "private/default",
    "room_family": "family/default",
    "room_trading": "trading/default",
}


class GovernanceDecisionLogger:
    """Persists Systemform governance decisions through the existing decision log."""

    def __init__(self, repository: DecisionRepository) -> None:
        self.repository = repository

    def add(
        self,
        decision: GovernanceDecision,
        *,
        context: Context | dict[str, Any] | None = None,
        source: str = "guard_pipeline",
    ) -> DecisionRecord:
        record = governance_decision_to_record(decision, context=context, source=source)
        self.repository.add(record)
        return record


def governance_decision_to_record(
    decision: GovernanceDecision,
    *,
    context: Context | dict[str, Any] | None = None,
    source: str = "guard_pipeline",
) -> DecisionRecord:
    """Convert a Systemform governance decision to a durable prototype decision record."""

    decision_data = decision.model_dump(mode="json")
    return DecisionRecord(
        decision_type="governance_decision",
        context=_decision_context(decision, context),
        subject_id=decision.event_id or decision.rule_id or f"{decision.actor_id}:{decision.room_id}",
        actor=decision.actor_id,
        reason=decision.reason,
        source=source,
        created_at=decision.created_at,
        details={
            "governance_decision": decision_data,
            "decision": decision_data["decision"],
            "room_id": decision.room_id,
            "requires_human": decision.requires_human,
            "trace": list(decision_data.get("details", {}).get("trace", [])),
        },
    )


def _decision_context(
    decision: GovernanceDecision,
    context: Context | dict[str, Any] | None,
) -> dict[str, Any]:
    if context is not None:
        return Context.model_validate(context).as_event_context()
    context_name = ROOM_ID_TO_CONTEXT_NAME.get(decision.room_id, "developer/default")
    return Context.model_validate({"name": context_name}).as_event_context()
