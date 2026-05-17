from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from pigenus.core.governance_decision_log import GovernanceDecisionLogger
from pigenus.core.worker_freshness_policy import (
    WorkerFreshnessPolicyValidator,
    WorkerFreshnessRecommendation,
)
from pigenus.core.worker_scheduling_preview import SENSITIVITY_RANK
from pigenus.schemas.base import utc_now
from pigenus.schemas.context import Context
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    GovernanceDecision,
    GuardDecisionType,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerHeartbeat,
    WorkerStatus,
)
from pigenus.storage.repositories import DecisionRepository, WorkerRepository
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


class WorkerAssignmentSchedulingEligibilityOutcome(str, Enum):
    """Read-only scheduling eligibility outcome for assigned worker intent."""

    ALLOW = "allow_scheduling"
    DENY = "deny_scheduling"
    REQUIRE_REVIEW = "require_review"
    NOT_CONSIDERED = "not_considered"


@dataclass(frozen=True)
class WorkerAssignmentSchedulingEligibilityResult:
    """Result of checking whether assignment intent may be considered."""

    assignment_id: str
    outcome: WorkerAssignmentSchedulingEligibilityOutcome
    reasons: tuple[str, ...]
    details: dict[str, Any]

    @property
    def eligible(self) -> bool:
        return self.outcome == WorkerAssignmentSchedulingEligibilityOutcome.ALLOW

    def to_governance_decision(
        self,
        *,
        actor_id: str,
        event_id: str | None = None,
        rule_id: str = "worker_assignment_scheduling_eligibility",
    ) -> GovernanceDecision | None:
        decision = _outcome_to_guard_decision(self.outcome)
        if decision is None:
            return None

        room_id = self.details.get("room_id")
        if not isinstance(room_id, str) or not room_id:
            return None

        reason = self.reasons[0] if self.reasons else self.outcome.value
        return GovernanceDecision(
            decision=decision,
            reason=reason,
            actor_id=actor_id,
            room_id=room_id,
            event_id=event_id,
            rule_id=rule_id,
            requires_human=decision == GuardDecisionType.ESCALATE,
            details={
                "family": "worker_assignment_scheduling_eligibility",
                "assignment_id": self.assignment_id,
                "outcome": self.outcome.value,
                "eligible": self.eligible,
                "reasons": list(self.reasons),
                **self.details,
                "trace": [
                    {
                        "name": "worker_assignment_scheduling_eligibility",
                        "family": "worker_assignment_scheduling_eligibility",
                        "decision": decision.value,
                        "reason": reason,
                        "details": {
                            "assignment_id": self.assignment_id,
                            "outcome": self.outcome.value,
                            "reasons": ",".join(self.reasons),
                        },
                    },
                ],
            },
        )


class WorkerAssignmentSchedulingEligibilityLogger:
    """Opt-in persistence for assignment scheduling eligibility decisions."""

    def __init__(self, repository: DecisionRepository) -> None:
        self.governance_logger = GovernanceDecisionLogger(repository)

    def add(
        self,
        result: WorkerAssignmentSchedulingEligibilityResult,
        *,
        actor_id: str,
        event_id: str | None = None,
        rule_id: str = "worker_assignment_scheduling_eligibility",
        context: Context | dict[str, Any] | None = None,
    ) -> DecisionRecord | None:
        decision = result.to_governance_decision(
            actor_id=actor_id,
            event_id=event_id,
            rule_id=rule_id,
        )
        if decision is None:
            return None
        return self.governance_logger.add(
            decision,
            context=context,
            source="worker_assignment_scheduling_eligibility",
            subject_id=result.assignment_id,
        )


class WorkerAssignmentSchedulingEligibilityValidator:
    """Read-only check before future scheduling can consider an assignment."""

    def __init__(
        self,
        *,
        assignments: WorkerAssignmentRepository,
        workers: WorkerRepository,
        decisions: DecisionRepository,
        freshness: WorkerFreshnessPolicyValidator | None = None,
        now_provider: Callable[[], datetime] = utc_now,
    ) -> None:
        self.assignments = assignments
        self.workers = workers
        self.decisions = decisions
        self.freshness = freshness or WorkerFreshnessPolicyValidator()
        self.now_provider = now_provider

    def validate(
        self,
        assignment_id: str,
        *,
        now: datetime | None = None,
    ) -> WorkerAssignmentSchedulingEligibilityResult:
        assignment = self.assignments.get(assignment_id)
        if assignment is None:
            return WorkerAssignmentSchedulingEligibilityResult(
                assignment_id=assignment_id,
                outcome=WorkerAssignmentSchedulingEligibilityOutcome.NOT_CONSIDERED,
                reasons=("assignment_unknown",),
                details={"assignment_id": assignment_id},
            )

        details: dict[str, Any] = {
            "assignment_id": assignment.id,
            "assignment_status": assignment.status.value,
            "worker_id": assignment.worker_id,
            "capability": assignment.capability,
            "room_id": assignment.room_id,
            "governance_decision_id": assignment.governance_decision_id,
        }

        if assignment.status != WorkerAssignmentStatus.ASSIGNED:
            reason = (
                "assignment_status_terminal"
                if assignment.status
                in {
                    WorkerAssignmentStatus.REJECTED,
                    WorkerAssignmentStatus.CANCELLED,
                    WorkerAssignmentStatus.EXPIRED,
                }
                else "assignment_status_not_assigned"
            )
            return WorkerAssignmentSchedulingEligibilityResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentSchedulingEligibilityOutcome.NOT_CONSIDERED,
                reasons=(reason,),
                details=details,
            )

        deny_reasons: list[str] = []
        review_reasons: list[str] = []

        heartbeat = self._check_worker_state(
            assignment,
            deny_reasons,
            review_reasons,
            details,
        )
        evidence = self._check_governance_evidence(assignment, deny_reasons, details)
        if evidence is not None and "worker_unknown" not in deny_reasons:
            self._check_freshness(
                assignment=assignment,
                heartbeat=heartbeat,
                evidence=evidence,
                deny_reasons=deny_reasons,
                review_reasons=review_reasons,
                details=details,
                now=now or self.now_provider(),
            )

        if deny_reasons:
            return WorkerAssignmentSchedulingEligibilityResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentSchedulingEligibilityOutcome.DENY,
                reasons=tuple(deny_reasons),
                details=details,
            )

        if review_reasons:
            return WorkerAssignmentSchedulingEligibilityResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentSchedulingEligibilityOutcome.REQUIRE_REVIEW,
                reasons=tuple(review_reasons),
                details=details,
            )

        return WorkerAssignmentSchedulingEligibilityResult(
            assignment_id=assignment.id,
            outcome=WorkerAssignmentSchedulingEligibilityOutcome.ALLOW,
            reasons=("assignment_scheduling_eligible",),
            details=details,
        )

    def _check_worker_state(
        self,
        assignment: WorkerAssignment,
        deny_reasons: list[str],
        review_reasons: list[str],
        details: dict[str, Any],
    ) -> WorkerHeartbeat | None:
        profile = self.workers.get_profile(assignment.worker_id)
        if profile is None:
            deny_reasons.append("worker_unknown")
            return None

        heartbeat = self.workers.get_heartbeat(assignment.worker_id)
        details["worker_status"] = profile.status.value
        details["heartbeat_status"] = heartbeat.status.value if heartbeat is not None else None

        if profile.status == WorkerStatus.DEGRADED:
            _append_reason(review_reasons, "worker_degraded")
        elif profile.status != WorkerStatus.ACTIVE:
            _append_reason(deny_reasons, "worker_not_considerable")

        if heartbeat is None:
            _append_reason(deny_reasons, "heartbeat_missing")
        elif heartbeat.status == WorkerStatus.DEGRADED:
            _append_reason(review_reasons, "worker_degraded")
        elif heartbeat.status != WorkerStatus.ACTIVE:
            _append_reason(deny_reasons, "worker_not_considerable")

        if assignment.capability not in profile.available_cells:
            _append_reason(deny_reasons, "worker_capability_missing")

        if (
            assignment.required_runtime is not None
            and assignment.required_runtime not in profile.supported_runtimes
        ):
            _append_reason(deny_reasons, "runtime_mismatch")

        if (
            assignment.sensitivity is not None
            and SENSITIVITY_RANK[assignment.sensitivity]
            > SENSITIVITY_RANK[profile.max_sensitivity]
        ):
            _append_reason(deny_reasons, "sensitivity_exceeded")

        if assignment.network_required and not profile.network_access:
            _append_reason(deny_reasons, "network_not_allowed")

        return heartbeat

    def _check_governance_evidence(
        self,
        assignment: WorkerAssignment,
        deny_reasons: list[str],
        details: dict[str, Any],
    ) -> DecisionRecord | None:
        decision = self.decisions.get(assignment.governance_decision_id)
        if decision is None:
            deny_reasons.append("governance_evidence_missing")
            return None

        details["decision_source"] = decision.source
        details["decision_type"] = decision.decision_type
        if not _is_preflight_allow(decision):
            deny_reasons.append("governance_evidence_not_preflight_allow")
            return None

        request, evidence_worker_id, evidence_room_id = _preflight_evidence(decision)
        if request is None:
            deny_reasons.append("governance_evidence_not_preflight_allow")
            return None

        reason_count = len(deny_reasons)
        _append_mismatch(
            deny_reasons,
            assignment.worker_id,
            evidence_worker_id,
            "evidence_worker_mismatch",
        )
        _append_mismatch(
            deny_reasons,
            assignment.capability,
            request.get("capability"),
            "evidence_capability_mismatch",
        )
        _append_mismatch(
            deny_reasons,
            assignment.required_runtime,
            request.get("required_runtime"),
            "evidence_runtime_mismatch",
        )
        _append_mismatch(
            deny_reasons,
            assignment.sensitivity.value if assignment.sensitivity is not None else None,
            request.get("sensitivity"),
            "evidence_sensitivity_mismatch",
        )
        _append_mismatch(
            deny_reasons,
            assignment.network_required,
            request.get("network_required"),
            "evidence_network_requirement_mismatch",
        )
        _append_mismatch(
            deny_reasons,
            assignment.room_id,
            evidence_room_id,
            "evidence_room_mismatch",
        )
        if len(deny_reasons) != reason_count:
            return None
        return decision

    def _check_freshness(
        self,
        *,
        assignment: WorkerAssignment,
        heartbeat: WorkerHeartbeat | None,
        evidence: DecisionRecord,
        deny_reasons: list[str],
        review_reasons: list[str],
        details: dict[str, Any],
        now: datetime,
    ) -> None:
        result = self.freshness.validate(
            assignment=assignment,
            heartbeat=heartbeat,
            evidence=evidence,
            now=now,
        )
        details["freshness"] = {
            "recommendation": result.recommendation.value,
            "heartbeat_label": result.heartbeat_label.value,
            "evidence_label": result.evidence_label.value,
            "assignment_age_label": result.assignment_age_label.value
            if result.assignment_age_label is not None
            else None,
            "reasons": list(result.reasons),
            **result.details,
        }

        if result.recommendation == WorkerFreshnessRecommendation.CONTINUE:
            return

        target = (
            review_reasons
            if result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
            else deny_reasons
        )
        for reason in result.reasons:
            if reason != "freshness_policy_passed":
                _append_reason(target, reason)


def _is_preflight_allow(decision: DecisionRecord) -> bool:
    return (
        decision.decision_type == "governance_decision"
        and decision.source == "worker_execution_preflight"
        and decision.details.get("decision") == "allow"
        and decision.details.get("family") == "worker_execution_preflight"
        and isinstance(decision.details.get("governance_decision"), dict)
    )


def _preflight_evidence(
    decision: DecisionRecord,
) -> tuple[dict[str, Any] | None, str | None, str | None]:
    governance_decision = decision.details.get("governance_decision")
    if not isinstance(governance_decision, dict):
        return None, None, None
    governance_details = governance_decision.get("details")
    if not isinstance(governance_details, dict):
        return None, None, None
    request = governance_details.get("request")
    if not isinstance(request, dict):
        return None, None, None
    worker_id = governance_details.get("worker_id")
    room_id = decision.details.get("room_id") or governance_decision.get("room_id")
    return request, worker_id, room_id


def _append_mismatch(
    reasons: list[str],
    actual: Any,
    expected: Any,
    reason: str,
) -> None:
    if actual != expected:
        _append_reason(reasons, reason)


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _outcome_to_guard_decision(
    outcome: WorkerAssignmentSchedulingEligibilityOutcome,
) -> GuardDecisionType | None:
    if outcome == WorkerAssignmentSchedulingEligibilityOutcome.ALLOW:
        return GuardDecisionType.ALLOW
    if outcome == WorkerAssignmentSchedulingEligibilityOutcome.DENY:
        return GuardDecisionType.BLOCK
    if outcome == WorkerAssignmentSchedulingEligibilityOutcome.REQUIRE_REVIEW:
        return GuardDecisionType.ESCALATE
    return None
