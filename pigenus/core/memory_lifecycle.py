from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pigenus.schemas.memory import MemoryObject, MemoryStatus

MANUAL_TRANSITIONS: set[tuple[MemoryStatus, MemoryStatus]] = {
    ("fresh", "active"),
    ("fresh", "stale"),
    ("active", "watch"),
    ("active", "stale"),
    ("active", "dormant"),
    ("watch", "active"),
    ("watch", "stale"),
    ("stale", "active"),
    ("stale", "dormant"),
    ("stale", "dead"),
    ("dormant", "active"),
    ("dormant", "fossil"),
    ("dead", "fossil"),
    ("fossil", "active"),
    ("canonical", "canonical"),
}

REVIEW_DUE_TRANSITIONS: dict[MemoryStatus, MemoryStatus] = {
    "fresh": "watch",
    "active": "watch",
    "watch": "watch",
}

EXPIRY_TRANSITIONS: dict[MemoryStatus, MemoryStatus] = {
    "fresh": "dead",
    "active": "dead",
    "watch": "dead",
    "stale": "dead",
    "dormant": "fossil",
    "dead": "dead",
    "fossil": "fossil",
    "canonical": "canonical",
}


@dataclass(frozen=True)
class MemoryLifecycleDecision:
    """Result of a lifecycle rule evaluation."""

    memory_id: str
    old_status: MemoryStatus
    new_status: MemoryStatus
    changed: bool
    reason: str
    source: str
    decided_at: datetime


class MemoryLifecycleEngine:
    """Deterministic memory lifecycle rules."""

    def validate_manual_transition(
        self,
        *,
        old_status: MemoryStatus,
        new_status: MemoryStatus,
    ) -> None:
        if (old_status, new_status) not in MANUAL_TRANSITIONS:
            raise ValueError(f"Invalid memory status transition: {old_status} -> {new_status}")

    def manual_transition(
        self,
        memory: MemoryObject,
        *,
        new_status: MemoryStatus,
        now: datetime,
    ) -> MemoryLifecycleDecision:
        self.validate_manual_transition(old_status=memory.status, new_status=new_status)
        return self._decision(
            memory,
            new_status=new_status,
            reason="manual_transition",
            source="manual",
            now=now,
        )

    def apply_automatic_rules(
        self,
        memory: MemoryObject,
        *,
        now: datetime,
    ) -> MemoryLifecycleDecision:
        if memory.status == "canonical":
            return self._decision(
                memory,
                new_status="canonical",
                reason="canonical_protected",
                source="automatic",
                now=now,
            )

        if memory.expires_at is not None and memory.expires_at <= now:
            return self._decision(
                memory,
                new_status=EXPIRY_TRANSITIONS[memory.status],
                reason="expired",
                source="automatic",
                now=now,
            )

        if memory.review_due_at is not None and memory.review_due_at <= now:
            return self._decision(
                memory,
                new_status=REVIEW_DUE_TRANSITIONS.get(memory.status, memory.status),
                reason="review_due",
                source="automatic",
                now=now,
            )

        return self._decision(
            memory,
            new_status=memory.status,
            reason="no_lifecycle_change",
            source="automatic",
            now=now,
        )

    @staticmethod
    def _decision(
        memory: MemoryObject,
        *,
        new_status: MemoryStatus,
        reason: str,
        source: str,
        now: datetime,
    ) -> MemoryLifecycleDecision:
        return MemoryLifecycleDecision(
            memory_id=memory.memory_id,
            old_status=memory.status,
            new_status=new_status,
            changed=memory.status != new_status,
            reason=reason,
            source=source,
            decided_at=now,
        )
