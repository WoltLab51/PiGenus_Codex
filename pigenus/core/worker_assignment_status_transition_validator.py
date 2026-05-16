from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigenus.schemas.systemform import WorkerAssignment, WorkerAssignmentStatus


ALLOWED_WORKER_ASSIGNMENT_STATUS_TRANSITIONS: dict[
    WorkerAssignmentStatus, frozenset[WorkerAssignmentStatus]
] = {
    WorkerAssignmentStatus.PENDING: frozenset(
        {
            WorkerAssignmentStatus.ASSIGNED,
            WorkerAssignmentStatus.REJECTED,
            WorkerAssignmentStatus.CANCELLED,
            WorkerAssignmentStatus.EXPIRED,
        }
    ),
    WorkerAssignmentStatus.ASSIGNED: frozenset(
        {
            WorkerAssignmentStatus.CANCELLED,
            WorkerAssignmentStatus.EXPIRED,
        }
    ),
}
TERMINAL_WORKER_ASSIGNMENT_STATUSES = frozenset(
    {
        WorkerAssignmentStatus.REJECTED,
        WorkerAssignmentStatus.CANCELLED,
        WorkerAssignmentStatus.EXPIRED,
    }
)


@dataclass(frozen=True)
class WorkerAssignmentStatusTransitionValidationResult:
    """Result of checking a worker assignment status transition."""

    assignment_id: str
    valid: bool
    reasons: tuple[str, ...]
    details: dict[str, Any]


class WorkerAssignmentStatusTransitionValidator:
    """Checks assignment status transitions without persisting changes."""

    def validate(
        self,
        assignment: WorkerAssignment,
        target_status: WorkerAssignmentStatus | str,
        *,
        actor_id: str | None = None,
        reason: str | None = None,
    ) -> WorkerAssignmentStatusTransitionValidationResult:
        reasons: list[str] = []
        current_status = assignment.status
        target = _coerce_status(target_status, reasons)
        details: dict[str, Any] = {
            "assignment_id": assignment.id,
            "worker_id": assignment.worker_id,
            "capability": assignment.capability,
            "room_id": assignment.room_id,
            "current_status": current_status.value,
            "target_status": target.value if target is not None else str(target_status),
            "actor_id": actor_id,
            "reason": reason,
        }

        if target is None:
            return _result(assignment, reasons, details)

        if current_status == target:
            reasons.append("status_transition_noop")
        elif current_status in TERMINAL_WORKER_ASSIGNMENT_STATUSES:
            reasons.append("assignment_status_terminal")
        elif target not in ALLOWED_WORKER_ASSIGNMENT_STATUS_TRANSITIONS.get(
            current_status, frozenset()
        ):
            reasons.append("status_transition_not_allowed")

        return _result(assignment, reasons, details)


def _coerce_status(
    status: WorkerAssignmentStatus | str,
    reasons: list[str],
) -> WorkerAssignmentStatus | None:
    if isinstance(status, WorkerAssignmentStatus):
        return status
    try:
        return WorkerAssignmentStatus(status)
    except ValueError:
        reasons.append("target_status_unknown")
        return None


def _result(
    assignment: WorkerAssignment,
    reasons: list[str],
    details: dict[str, Any],
) -> WorkerAssignmentStatusTransitionValidationResult:
    if reasons:
        return WorkerAssignmentStatusTransitionValidationResult(
            assignment_id=assignment.id,
            valid=False,
            reasons=tuple(reasons),
            details=details,
        )
    return WorkerAssignmentStatusTransitionValidationResult(
        assignment_id=assignment.id,
        valid=True,
        reasons=("status_transition_valid",),
        details=details,
    )
