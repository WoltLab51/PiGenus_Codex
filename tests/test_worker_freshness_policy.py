from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pigenus.core.worker_freshness_policy import (
    FreshnessLabel,
    WorkerFreshnessPolicy,
    WorkerFreshnessPolicyValidator,
    WorkerFreshnessRecommendation,
)
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerHeartbeat,
    WorkerStatus,
)


NOW = datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc)


def assignment(*, updated_at: datetime | None = None) -> WorkerAssignment:
    return WorkerAssignment(
        id="wasg_freshness",
        worker_id="worker_local",
        capability="meaning_ingester",
        room_id="room_developer",
        governance_decision_id="dec_preflight",
        created_by_actor_id="agent_scheduler_preview",
        status=WorkerAssignmentStatus.ASSIGNED,
        required_runtime="python",
        sensitivity=Sensitivity.PRIVATE,
        network_required=True,
        created_at=NOW - timedelta(minutes=5),
        updated_at=updated_at or NOW - timedelta(minutes=5),
    )


def heartbeat(
    *,
    seen_at: datetime | None = None,
    status: WorkerStatus = WorkerStatus.ACTIVE,
) -> WorkerHeartbeat:
    return WorkerHeartbeat(
        worker_id="worker_local",
        status=status,
        seen_at=seen_at or NOW - timedelta(seconds=30),
    )


def evidence(*, created_at: datetime | None = None) -> DecisionRecord:
    return DecisionRecord(
        decision_id="dec_preflight",
        decision_type="governance_decision",
        context={"name": "developer/default"},
        subject_id="evt_preflight",
        actor="agent_preflight",
        reason="worker_execution_preflight_passed",
        source="worker_execution_preflight",
        created_at=created_at or NOW - timedelta(minutes=5),
        details={
            "decision": "allow",
            "family": "worker_execution_preflight",
        },
    )


def validator(
    policy: WorkerFreshnessPolicy | None = None,
) -> WorkerFreshnessPolicyValidator:
    return WorkerFreshnessPolicyValidator(policy)


def test_worker_freshness_policy_allows_fresh_heartbeat_and_evidence():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(),
        evidence=evidence(),
        now=NOW,
    )

    assert result.can_continue is True
    assert result.recommendation == WorkerFreshnessRecommendation.CONTINUE
    assert result.heartbeat_label == FreshnessLabel.FRESH
    assert result.evidence_label == FreshnessLabel.FRESH
    assert result.reasons == ("freshness_policy_passed",)
    assert result.details["now"] == NOW.isoformat()


def test_worker_freshness_policy_marks_missing_heartbeat_not_considered():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=None,
        evidence=evidence(),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.NOT_CONSIDERED
    assert result.heartbeat_label == FreshnessLabel.MISSING
    assert result.reasons == ("heartbeat_missing",)


def test_worker_freshness_policy_marks_review_stale_heartbeat_for_review():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(seen_at=NOW - timedelta(seconds=121)),
        evidence=evidence(),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
    assert result.heartbeat_label == FreshnessLabel.REVIEW_STALE
    assert result.reasons == ("heartbeat_review_stale",)


def test_worker_freshness_policy_denies_hard_stale_heartbeat():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(seen_at=NOW - timedelta(seconds=601)),
        evidence=evidence(),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.DENY_FRESHNESS
    assert result.heartbeat_label == FreshnessLabel.HARD_STALE
    assert result.reasons == ("heartbeat_hard_stale",)


def test_worker_freshness_policy_marks_missing_evidence_not_considered():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(),
        evidence=None,
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.NOT_CONSIDERED
    assert result.evidence_label == FreshnessLabel.MISSING
    assert result.reasons == ("evidence_missing",)


def test_worker_freshness_policy_marks_review_stale_evidence_for_review():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(),
        evidence=evidence(created_at=NOW - timedelta(minutes=16)),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
    assert result.evidence_label == FreshnessLabel.REVIEW_STALE
    assert result.reasons == ("evidence_review_stale",)


def test_worker_freshness_policy_denies_hard_stale_evidence():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(),
        evidence=evidence(created_at=NOW - timedelta(minutes=61)),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.DENY_FRESHNESS
    assert result.evidence_label == FreshnessLabel.HARD_STALE
    assert result.reasons == ("evidence_hard_stale",)


def test_worker_freshness_policy_marks_future_heartbeat_clock_invalid():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(seen_at=NOW + timedelta(seconds=6)),
        evidence=evidence(),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
    assert result.heartbeat_label == FreshnessLabel.CLOCK_INVALID
    assert result.reasons == ("heartbeat_clock_invalid",)


def test_worker_freshness_policy_marks_future_evidence_clock_invalid():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(),
        evidence=evidence(created_at=NOW + timedelta(seconds=6)),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
    assert result.evidence_label == FreshnessLabel.CLOCK_INVALID
    assert result.reasons == ("evidence_clock_invalid",)


def test_worker_freshness_policy_requires_review_for_degraded_heartbeat():
    result = validator().validate(
        assignment=assignment(),
        heartbeat=heartbeat(status=WorkerStatus.DEGRADED),
        evidence=evidence(),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
    assert result.heartbeat_label == FreshnessLabel.FRESH
    assert result.reasons == ("worker_degraded",)


def test_worker_freshness_policy_can_optionally_report_assignment_age():
    policy = WorkerFreshnessPolicy(evaluate_assignment_age=True)

    result = validator(policy).validate(
        assignment=assignment(updated_at=NOW - timedelta(minutes=31)),
        heartbeat=heartbeat(),
        evidence=evidence(),
        now=NOW,
    )

    assert result.recommendation == WorkerFreshnessRecommendation.REQUIRE_REVIEW
    assert result.assignment_age_label == FreshnessLabel.REVIEW_STALE
    assert result.reasons == ("assignment_age_review_stale",)
    assert result.details["assignment_age_label"] == "review_stale"


def test_worker_freshness_policy_does_not_mutate_inputs():
    item = assignment()
    signal = heartbeat()
    record = evidence()
    item_before = item.model_copy(deep=True)
    signal_before = signal.model_copy(deep=True)
    record_before = record.model_copy(deep=True)

    validator().validate(
        assignment=item,
        heartbeat=signal,
        evidence=record,
        now=NOW,
    )

    assert item == item_before
    assert signal == signal_before
    assert record == record_before
