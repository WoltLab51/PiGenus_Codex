from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigenus.core.audit import AuditLogger
from pigenus.core.governance_decision_log import ROOM_ID_TO_CONTEXT_NAME
from pigenus.core.worker_assignment_status_transition_validator import (
    WorkerAssignmentStatusTransitionValidationResult,
    WorkerAssignmentStatusTransitionValidator,
)
from pigenus.schemas.base import utc_now
from pigenus.schemas.systemform import WorkerAssignment, WorkerAssignmentStatus
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


@dataclass(frozen=True)
class WorkerAssignmentStatusTransitionResult:
    """Result of attempting to apply an assignment status transition."""

    assignment: WorkerAssignment | None
    audit_id: str | None
    validation: WorkerAssignmentStatusTransitionValidationResult

    @property
    def transitioned(self) -> bool:
        return self.assignment is not None and self.audit_id is not None


class WorkerAssignmentStatusTransitionService:
    """Applies validated assignment status transitions and writes audit."""

    def __init__(
        self,
        *,
        validator: WorkerAssignmentStatusTransitionValidator,
        assignments: WorkerAssignmentRepository,
        audit_logger: AuditLogger,
    ) -> None:
        self.validator = validator
        self.assignments = assignments
        self.audit_logger = audit_logger

    def transition(
        self,
        assignment_id: str,
        target_status: WorkerAssignmentStatus | str,
        *,
        actor_id: str,
        reason: str | None = None,
    ) -> WorkerAssignmentStatusTransitionResult:
        assignment = self.assignments.get(assignment_id)
        if assignment is None:
            return WorkerAssignmentStatusTransitionResult(
                assignment=None,
                audit_id=None,
                validation=_missing_assignment_result(
                    assignment_id=assignment_id,
                    target_status=target_status,
                    actor_id=actor_id,
                    reason=reason,
                ),
            )

        validation = self.validator.validate(
            assignment,
            target_status,
            actor_id=actor_id,
            reason=reason,
        )
        if not validation.valid:
            return WorkerAssignmentStatusTransitionResult(
                assignment=None,
                audit_id=None,
                validation=validation,
            )

        target = WorkerAssignmentStatus(target_status)
        updated = self.assignments.update_status(assignment.id, target, utc_now())
        audit_id = self.audit_logger.log(
            actor=actor_id,
            action="worker_assignment_status_changed",
            context=_assignment_context(updated),
            details=_status_change_audit_details(
                assignment=assignment,
                updated=updated,
                actor_id=actor_id,
                reason=reason,
            ),
        )
        return WorkerAssignmentStatusTransitionResult(
            assignment=updated,
            audit_id=audit_id,
            validation=validation,
        )


def _assignment_context(assignment: WorkerAssignment) -> dict[str, Any]:
    return {
        "name": ROOM_ID_TO_CONTEXT_NAME.get(assignment.room_id, "developer/default"),
    }


def _status_change_audit_details(
    *,
    assignment: WorkerAssignment,
    updated: WorkerAssignment,
    actor_id: str,
    reason: str | None,
) -> dict[str, Any]:
    return {
        "assignment_id": assignment.id,
        "worker_id": assignment.worker_id,
        "capability": assignment.capability,
        "room_id": assignment.room_id,
        "old_status": assignment.status.value,
        "new_status": updated.status.value,
        "actor_id": actor_id,
        "reason": reason,
    }


def _missing_assignment_result(
    *,
    assignment_id: str,
    target_status: WorkerAssignmentStatus | str,
    actor_id: str,
    reason: str | None,
) -> WorkerAssignmentStatusTransitionValidationResult:
    target = (
        target_status.value
        if isinstance(target_status, WorkerAssignmentStatus)
        else str(target_status)
    )
    return WorkerAssignmentStatusTransitionValidationResult(
        assignment_id=assignment_id,
        valid=False,
        reasons=("assignment_unknown",),
        details={
            "assignment_id": assignment_id,
            "target_status": target,
            "actor_id": actor_id,
            "reason": reason,
        },
    )
