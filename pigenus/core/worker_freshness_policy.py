from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    WorkerAssignment,
    WorkerHeartbeat,
    WorkerStatus,
)


class FreshnessLabel(str, Enum):
    """Stable freshness labels for worker scheduling-readiness inputs."""

    FRESH = "fresh"
    REVIEW_STALE = "review_stale"
    HARD_STALE = "hard_stale"
    MISSING = "missing"
    CLOCK_INVALID = "clock_invalid"


class WorkerFreshnessRecommendation(str, Enum):
    """Derived recommendation from freshness-only checks."""

    CONTINUE = "continue"
    REQUIRE_REVIEW = "require_review"
    DENY_FRESHNESS = "deny_freshness"
    NOT_CONSIDERED = "not_considered"


@dataclass(frozen=True)
class WorkerFreshnessPolicy:
    """Thresholds for storage-free worker freshness evaluation."""

    heartbeat_fresh_for: timedelta = timedelta(seconds=120)
    heartbeat_review_for: timedelta = timedelta(seconds=600)
    evidence_fresh_for: timedelta = timedelta(minutes=15)
    evidence_review_for: timedelta = timedelta(minutes=60)
    assignment_fresh_for: timedelta = timedelta(minutes=30)
    assignment_review_for: timedelta = timedelta(minutes=120)
    max_future_skew: timedelta = timedelta(seconds=5)
    evaluate_assignment_age: bool = False


@dataclass(frozen=True)
class WorkerFreshnessPolicyResult:
    """Read-only result of applying worker freshness policy."""

    assignment_id: str
    recommendation: WorkerFreshnessRecommendation
    heartbeat_label: FreshnessLabel
    evidence_label: FreshnessLabel
    assignment_age_label: FreshnessLabel | None
    reasons: tuple[str, ...]
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def can_continue(self) -> bool:
        return self.recommendation == WorkerFreshnessRecommendation.CONTINUE


class WorkerFreshnessPolicyValidator:
    """Classify heartbeat and evidence freshness without side effects."""

    def __init__(self, policy: WorkerFreshnessPolicy | None = None) -> None:
        self.policy = policy or WorkerFreshnessPolicy()

    def validate(
        self,
        *,
        assignment: WorkerAssignment,
        heartbeat: WorkerHeartbeat | None,
        evidence: DecisionRecord | None,
        now: datetime,
    ) -> WorkerFreshnessPolicyResult:
        heartbeat_label = self._label_timestamp(
            timestamp=heartbeat.seen_at if heartbeat is not None else None,
            now=now,
            fresh_for=self.policy.heartbeat_fresh_for,
            review_for=self.policy.heartbeat_review_for,
        )
        evidence_label = self._label_timestamp(
            timestamp=evidence.created_at if evidence is not None else None,
            now=now,
            fresh_for=self.policy.evidence_fresh_for,
            review_for=self.policy.evidence_review_for,
        )
        assignment_age_label = (
            self._label_timestamp(
                timestamp=assignment.updated_at,
                now=now,
                fresh_for=self.policy.assignment_fresh_for,
                review_for=self.policy.assignment_review_for,
            )
            if self.policy.evaluate_assignment_age
            else None
        )

        reasons = self._reasons(
            heartbeat=heartbeat,
            heartbeat_label=heartbeat_label,
            evidence_label=evidence_label,
            assignment_age_label=assignment_age_label,
        )
        recommendation = self._recommendation(
            heartbeat=heartbeat,
            heartbeat_label=heartbeat_label,
            evidence_label=evidence_label,
            assignment_age_label=assignment_age_label,
        )

        details: dict[str, Any] = {
            "assignment_id": assignment.id,
            "worker_id": assignment.worker_id,
            "governance_decision_id": assignment.governance_decision_id,
            "now": now.isoformat(),
            "heartbeat_label": heartbeat_label.value,
            "evidence_label": evidence_label.value,
            "heartbeat_seen_at": heartbeat.seen_at.isoformat()
            if heartbeat is not None
            else None,
            "heartbeat_status": heartbeat.status.value if heartbeat is not None else None,
            "evidence_created_at": evidence.created_at.isoformat()
            if evidence is not None
            else None,
            "thresholds": {
                "heartbeat_fresh_for_seconds": self.policy.heartbeat_fresh_for.total_seconds(),
                "heartbeat_review_for_seconds": self.policy.heartbeat_review_for.total_seconds(),
                "evidence_fresh_for_seconds": self.policy.evidence_fresh_for.total_seconds(),
                "evidence_review_for_seconds": self.policy.evidence_review_for.total_seconds(),
                "max_future_skew_seconds": self.policy.max_future_skew.total_seconds(),
            },
        }
        if assignment_age_label is not None:
            details["assignment_age_label"] = assignment_age_label.value
            details["assignment_updated_at"] = assignment.updated_at.isoformat()

        return WorkerFreshnessPolicyResult(
            assignment_id=assignment.id,
            recommendation=recommendation,
            heartbeat_label=heartbeat_label,
            evidence_label=evidence_label,
            assignment_age_label=assignment_age_label,
            reasons=tuple(reasons),
            details=details,
        )

    def _label_timestamp(
        self,
        *,
        timestamp: datetime | None,
        now: datetime,
        fresh_for: timedelta,
        review_for: timedelta,
    ) -> FreshnessLabel:
        if timestamp is None:
            return FreshnessLabel.MISSING
        if timestamp.tzinfo is None or now.tzinfo is None:
            return FreshnessLabel.CLOCK_INVALID
        if timestamp > now + self.policy.max_future_skew:
            return FreshnessLabel.CLOCK_INVALID

        age = max(now - timestamp, timedelta())
        if age <= fresh_for:
            return FreshnessLabel.FRESH
        if age <= review_for:
            return FreshnessLabel.REVIEW_STALE
        return FreshnessLabel.HARD_STALE

    def _reasons(
        self,
        *,
        heartbeat: WorkerHeartbeat | None,
        heartbeat_label: FreshnessLabel,
        evidence_label: FreshnessLabel,
        assignment_age_label: FreshnessLabel | None,
    ) -> list[str]:
        reasons: list[str] = []
        self._append_label_reason(reasons, "heartbeat", heartbeat_label)
        self._append_label_reason(reasons, "evidence", evidence_label)
        if assignment_age_label is not None:
            self._append_label_reason(reasons, "assignment_age", assignment_age_label)

        if heartbeat is not None:
            if heartbeat.status == WorkerStatus.DEGRADED:
                _append_reason(reasons, "worker_degraded")
            elif heartbeat.status != WorkerStatus.ACTIVE:
                _append_reason(reasons, "worker_not_considerable")

        if not reasons:
            reasons.append("freshness_policy_passed")
        return reasons

    def _append_label_reason(
        self,
        reasons: list[str],
        prefix: str,
        label: FreshnessLabel,
    ) -> None:
        if label == FreshnessLabel.FRESH:
            return
        _append_reason(reasons, f"{prefix}_{label.value}")

    def _recommendation(
        self,
        *,
        heartbeat: WorkerHeartbeat | None,
        heartbeat_label: FreshnessLabel,
        evidence_label: FreshnessLabel,
        assignment_age_label: FreshnessLabel | None,
    ) -> WorkerFreshnessRecommendation:
        labels = [heartbeat_label, evidence_label]
        if assignment_age_label is not None:
            labels.append(assignment_age_label)

        if FreshnessLabel.MISSING in labels:
            return WorkerFreshnessRecommendation.NOT_CONSIDERED
        if FreshnessLabel.HARD_STALE in labels:
            return WorkerFreshnessRecommendation.DENY_FRESHNESS
        if heartbeat is not None and heartbeat.status not in {
            WorkerStatus.ACTIVE,
            WorkerStatus.DEGRADED,
        }:
            return WorkerFreshnessRecommendation.DENY_FRESHNESS
        if (
            FreshnessLabel.REVIEW_STALE in labels
            or FreshnessLabel.CLOCK_INVALID in labels
            or (heartbeat is not None and heartbeat.status == WorkerStatus.DEGRADED)
        ):
            return WorkerFreshnessRecommendation.REQUIRE_REVIEW
        return WorkerFreshnessRecommendation.CONTINUE


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)
