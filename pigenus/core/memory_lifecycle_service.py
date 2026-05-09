from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pigenus.core.audit import AuditLogger
from pigenus.core.memory_lifecycle import MemoryLifecycleDecision, MemoryLifecycleEngine
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.memory import MemoryObject, MemoryStatus
from pigenus.storage.repositories import DecisionRepository, MemoryRepository


@dataclass(frozen=True)
class MemoryReviewResult:
    """Summary returned by deterministic memory review."""

    checked: int
    changed: int
    decisions: list[MemoryLifecycleDecision]


class MemoryLifecycleService:
    """Applies lifecycle decisions to storage and audit logs."""

    actor = "memory_lifecycle@0.1.0"

    def __init__(
        self,
        *,
        repository: MemoryRepository,
        audit_logger: AuditLogger,
        decision_repository: DecisionRepository | None = None,
        engine: MemoryLifecycleEngine | None = None,
    ) -> None:
        self.repository = repository
        self.audit_logger = audit_logger
        self.decision_repository = decision_repository
        self.engine = engine or MemoryLifecycleEngine()

    def review(self, *, now: datetime) -> MemoryReviewResult:
        memories = self.repository.list()
        decisions: list[MemoryLifecycleDecision] = []
        changed = 0

        for memory in memories:
            decision = self.engine.apply_automatic_rules(memory, now=now)
            decisions.append(decision)
            if decision.changed:
                self._apply_decision(memory, decision)
                changed += 1

        return MemoryReviewResult(checked=len(memories), changed=changed, decisions=decisions)

    def manual_transition(
        self,
        memory: MemoryObject,
        *,
        new_status: MemoryStatus,
        now: datetime,
    ) -> MemoryObject:
        decision = self.engine.manual_transition(memory, new_status=new_status, now=now)
        if decision.changed:
            return self._apply_decision(memory, decision)
        return memory

    def _apply_decision(
        self,
        memory: MemoryObject,
        decision: MemoryLifecycleDecision,
    ) -> MemoryObject:
        last_validated_at = (
            decision.decided_at.isoformat()
            if decision.source == "manual" and decision.new_status == "active"
            else None
        )
        updated = self.repository.update_lifecycle(
            memory,
            status=decision.new_status,
            last_validated_at=last_validated_at,
        )
        self.audit_logger.log(
            actor=self.actor,
            action=self._audit_action(decision),
            context=memory.context,
            details={
                "memory_id": decision.memory_id,
                "old_status": decision.old_status,
                "new_status": decision.new_status,
                "reason": decision.reason,
                "source": decision.source,
            },
        )
        if self.decision_repository is not None:
            self.decision_repository.add(
                DecisionRecord(
                    decision_type="memory_lifecycle_status_change",
                    context=memory.context,
                    subject_id=decision.memory_id,
                    actor=self.actor,
                    reason=decision.reason,
                    source=decision.source,
                    created_at=decision.decided_at,
                    details={
                        "old_status": decision.old_status,
                        "new_status": decision.new_status,
                    },
                )
            )
        return updated

    @staticmethod
    def _audit_action(decision: MemoryLifecycleDecision) -> str:
        if decision.source == "manual":
            return "memory_lifecycle_manual_transition"
        if decision.reason == "expired":
            return "memory_lifecycle_expire"
        return "memory_lifecycle_review"
