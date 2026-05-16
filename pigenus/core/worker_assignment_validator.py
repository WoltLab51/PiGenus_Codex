from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import WorkerAssignment, WorkerAssignmentStatus
from pigenus.storage.repositories import DecisionRepository, WorkerRepository


@dataclass(frozen=True)
class WorkerAssignmentValidationResult:
    """Result of validating assignment intent before persistence."""

    assignment_id: str
    valid: bool
    reasons: tuple[str, ...]
    details: dict[str, Any]


class WorkerAssignmentValidator:
    """Checks assignment intent evidence without creating assignments."""

    def __init__(
        self,
        *,
        workers: WorkerRepository,
        decisions: DecisionRepository,
    ) -> None:
        self.workers = workers
        self.decisions = decisions

    def validate(self, assignment: WorkerAssignment) -> WorkerAssignmentValidationResult:
        reasons: list[str] = []
        details: dict[str, Any] = {
            "assignment_id": assignment.id,
            "governance_decision_id": assignment.governance_decision_id,
            "worker_id": assignment.worker_id,
        }

        if self.workers.get_profile(assignment.worker_id) is None:
            reasons.append("worker_unknown")

        if assignment.status != WorkerAssignmentStatus.PENDING:
            reasons.append("assignment_status_must_be_pending")

        decision = self.decisions.get(assignment.governance_decision_id)
        if decision is None:
            reasons.append("governance_decision_unknown")
            return _result(assignment, reasons, details)

        details["decision_source"] = decision.source
        details["decision_type"] = decision.decision_type
        self._validate_decision_contract(decision, reasons)
        self._validate_matching_evidence(assignment, decision, reasons)
        return _result(assignment, reasons, details)

    def _validate_decision_contract(
        self,
        decision: DecisionRecord,
        reasons: list[str],
    ) -> None:
        if decision.decision_type != "governance_decision":
            reasons.append("evidence_type_invalid")
        if decision.source != "worker_execution_preflight":
            reasons.append("evidence_source_invalid")
        if decision.details.get("decision") != "allow":
            reasons.append("evidence_decision_not_allow")
        if decision.details.get("family") != "worker_execution_preflight":
            reasons.append("evidence_family_invalid")
        if not isinstance(decision.details.get("governance_decision"), dict):
            reasons.append("evidence_governance_decision_missing")

    def _validate_matching_evidence(
        self,
        assignment: WorkerAssignment,
        decision: DecisionRecord,
        reasons: list[str],
    ) -> None:
        governance_decision = decision.details.get("governance_decision")
        if not isinstance(governance_decision, dict):
            return

        governance_details = governance_decision.get("details")
        if not isinstance(governance_details, dict):
            reasons.append("evidence_details_missing")
            return

        request = governance_details.get("request")
        if not isinstance(request, dict):
            reasons.append("evidence_request_missing")
            return

        evidence_worker_id = governance_details.get("worker_id")
        evidence_room_id = decision.details.get("room_id") or governance_decision.get("room_id")

        _append_mismatch(
            reasons,
            assignment.worker_id,
            evidence_worker_id,
            "worker_mismatch",
        )
        _append_mismatch(
            reasons,
            assignment.capability,
            request.get("capability"),
            "capability_mismatch",
        )
        _append_mismatch(
            reasons,
            assignment.required_runtime,
            request.get("required_runtime"),
            "runtime_mismatch",
        )
        _append_mismatch(
            reasons,
            assignment.sensitivity.value if assignment.sensitivity is not None else None,
            request.get("sensitivity"),
            "sensitivity_mismatch",
        )
        _append_mismatch(
            reasons,
            assignment.network_required,
            request.get("network_required"),
            "network_requirement_mismatch",
        )
        _append_mismatch(
            reasons,
            assignment.room_id,
            evidence_room_id,
            "room_mismatch",
        )


def _append_mismatch(
    reasons: list[str],
    actual: Any,
    expected: Any,
    reason: str,
) -> None:
    if actual != expected:
        reasons.append(reason)


def _result(
    assignment: WorkerAssignment,
    reasons: list[str],
    details: dict[str, Any],
) -> WorkerAssignmentValidationResult:
    if reasons:
        return WorkerAssignmentValidationResult(
            assignment_id=assignment.id,
            valid=False,
            reasons=tuple(reasons),
            details=details,
        )
    return WorkerAssignmentValidationResult(
        assignment_id=assignment.id,
        valid=True,
        reasons=("worker_assignment_valid",),
        details=details,
    )
