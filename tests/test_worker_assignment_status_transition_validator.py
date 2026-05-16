from __future__ import annotations

from datetime import datetime, timezone

from pigenus.core.worker_assignment_status_transition_validator import (
    WorkerAssignmentStatusTransitionValidator,
)
from pigenus.schemas.systemform import WorkerAssignment, WorkerAssignmentStatus


def assignment(status: WorkerAssignmentStatus) -> WorkerAssignment:
    return WorkerAssignment(
        id="wasg_transition",
        worker_id="worker_local",
        capability="meaning_ingester",
        room_id="room_developer",
        governance_decision_id="dec_preflight",
        created_by_actor_id="agent_scheduler_preview",
        status=status,
        required_runtime="python",
        network_required=True,
        created_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
    )


def validator() -> WorkerAssignmentStatusTransitionValidator:
    return WorkerAssignmentStatusTransitionValidator()


def test_worker_assignment_status_transition_validator_allows_documented_edges():
    allowed = [
        (WorkerAssignmentStatus.PENDING, WorkerAssignmentStatus.ASSIGNED),
        (WorkerAssignmentStatus.PENDING, WorkerAssignmentStatus.REJECTED),
        (WorkerAssignmentStatus.PENDING, WorkerAssignmentStatus.CANCELLED),
        (WorkerAssignmentStatus.PENDING, WorkerAssignmentStatus.EXPIRED),
        (WorkerAssignmentStatus.ASSIGNED, WorkerAssignmentStatus.CANCELLED),
        (WorkerAssignmentStatus.ASSIGNED, WorkerAssignmentStatus.EXPIRED),
    ]

    for current, target in allowed:
        result = validator().validate(
            assignment(current),
            target,
            actor_id="agent_operator",
            reason="operator_request",
        )

        assert result.valid is True
        assert result.reasons == ("status_transition_valid",)
        assert result.details["current_status"] == current.value
        assert result.details["target_status"] == target.value
        assert result.details["actor_id"] == "agent_operator"
        assert result.details["reason"] == "operator_request"


def test_worker_assignment_status_transition_validator_rejects_noop():
    result = validator().validate(
        assignment(WorkerAssignmentStatus.PENDING),
        WorkerAssignmentStatus.PENDING,
    )

    assert result.valid is False
    assert result.reasons == ("status_transition_noop",)


def test_worker_assignment_status_transition_validator_rejects_undocumented_edges():
    invalid = [
        (WorkerAssignmentStatus.ASSIGNED, WorkerAssignmentStatus.PENDING),
        (WorkerAssignmentStatus.ASSIGNED, WorkerAssignmentStatus.REJECTED),
        (WorkerAssignmentStatus.REJECTED, WorkerAssignmentStatus.CANCELLED),
        (WorkerAssignmentStatus.CANCELLED, WorkerAssignmentStatus.EXPIRED),
        (WorkerAssignmentStatus.EXPIRED, WorkerAssignmentStatus.CANCELLED),
    ]

    for current, target in invalid:
        result = validator().validate(assignment(current), target)

        assert result.valid is False
        assert "status_transition_valid" not in result.reasons


def test_worker_assignment_status_transition_validator_rejects_terminal_reactivation():
    for current in (
        WorkerAssignmentStatus.REJECTED,
        WorkerAssignmentStatus.CANCELLED,
        WorkerAssignmentStatus.EXPIRED,
    ):
        result = validator().validate(
            assignment(current),
            WorkerAssignmentStatus.ASSIGNED,
        )

        assert result.valid is False
        assert result.reasons == ("assignment_status_terminal",)


def test_worker_assignment_status_transition_validator_rejects_unknown_target_status():
    result = validator().validate(assignment(WorkerAssignmentStatus.PENDING), "running")

    assert result.valid is False
    assert result.reasons == ("target_status_unknown",)
    assert result.details["target_status"] == "running"


def test_worker_assignment_status_transition_validator_does_not_mutate_assignment():
    item = assignment(WorkerAssignmentStatus.PENDING)

    result = validator().validate(item, WorkerAssignmentStatus.ASSIGNED)

    assert result.valid is True
    assert item.status == WorkerAssignmentStatus.PENDING
