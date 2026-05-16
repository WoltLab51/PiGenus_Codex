from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigenus.core.audit import AuditLogger
from pigenus.core.governance_decision_log import ROOM_ID_TO_CONTEXT_NAME
from pigenus.core.worker_assignment_validator import (
    WorkerAssignmentValidationResult,
    WorkerAssignmentValidator,
)
from pigenus.schemas.systemform import WorkerAssignment
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


@dataclass(frozen=True)
class WorkerAssignmentCreationResult:
    """Result of attempting to create assignment intent."""

    assignment: WorkerAssignment | None
    audit_id: str | None
    validation: WorkerAssignmentValidationResult

    @property
    def created(self) -> bool:
        return self.assignment is not None and self.audit_id is not None


class WorkerAssignmentCreator:
    """Creates pending assignment intent after validation and audit."""

    def __init__(
        self,
        *,
        validator: WorkerAssignmentValidator,
        assignments: WorkerAssignmentRepository,
        audit_logger: AuditLogger,
    ) -> None:
        self.validator = validator
        self.assignments = assignments
        self.audit_logger = audit_logger

    def create(self, assignment: WorkerAssignment) -> WorkerAssignmentCreationResult:
        validation = self.validator.validate(assignment)
        if not validation.valid:
            return WorkerAssignmentCreationResult(
                assignment=None,
                audit_id=None,
                validation=validation,
            )

        self.assignments.add(assignment)
        audit_id = self.audit_logger.log(
            actor=assignment.created_by_actor_id,
            action="worker_assignment_created",
            context=_assignment_context(assignment),
            details=_assignment_audit_details(assignment),
        )
        return WorkerAssignmentCreationResult(
            assignment=assignment,
            audit_id=audit_id,
            validation=validation,
        )


def _assignment_context(assignment: WorkerAssignment) -> dict[str, Any]:
    return {
        "name": ROOM_ID_TO_CONTEXT_NAME.get(assignment.room_id, "developer/default"),
    }


def _assignment_audit_details(assignment: WorkerAssignment) -> dict[str, Any]:
    return {
        "assignment_id": assignment.id,
        "worker_id": assignment.worker_id,
        "capability": assignment.capability,
        "room_id": assignment.room_id,
        "governance_decision_id": assignment.governance_decision_id,
        "status": assignment.status.value,
    }
