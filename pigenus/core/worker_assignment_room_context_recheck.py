from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from pigenus.core.room_flow import RoomFlowDecisionType, RoomFlowRules
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    ContextFrame,
    ContextStack,
    Room,
    RoomProtectionLevel,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerProfile,
)
from pigenus.storage.repositories import DecisionRepository, WorkerRepository
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


class WorkerAssignmentRoomContextRecheckOutcome(str, Enum):
    """Read-only room/context outcome for assigned worker intent."""

    ALLOW = "allow_context"
    DENY = "deny_context"
    REQUIRE_REVIEW = "require_review"
    NOT_CONSIDERED = "not_considered"


@dataclass(frozen=True)
class WorkerAssignmentRoomContextRecheckResult:
    """Result of checking assignment room and context compatibility."""

    assignment_id: str
    outcome: WorkerAssignmentRoomContextRecheckOutcome
    reasons: tuple[str, ...]
    details: dict[str, Any]

    @property
    def context_compatible(self) -> bool:
        return self.outcome == WorkerAssignmentRoomContextRecheckOutcome.ALLOW


class WorkerAssignmentRoomContextRecheckValidator:
    """Read-only check for assignment room and context compatibility."""

    def __init__(
        self,
        *,
        assignments: WorkerAssignmentRepository,
        workers: WorkerRepository,
        decisions: DecisionRepository,
        room_flow: RoomFlowRules | None = None,
    ) -> None:
        self.assignments = assignments
        self.workers = workers
        self.decisions = decisions
        self.room_flow = room_flow or RoomFlowRules()

    def validate(
        self,
        assignment_id: str,
        *,
        context_stack: ContextStack | None = None,
        context_frames: Iterable[ContextFrame] | None = None,
        source_room_id: str | None = None,
        target_room_id: str | None = None,
    ) -> WorkerAssignmentRoomContextRecheckResult:
        assignment = self.assignments.get(assignment_id)
        if assignment is None:
            return WorkerAssignmentRoomContextRecheckResult(
                assignment_id=assignment_id,
                outcome=WorkerAssignmentRoomContextRecheckOutcome.NOT_CONSIDERED,
                reasons=("assignment_unknown",),
                details={"assignment_id": assignment_id},
            )

        details: dict[str, Any] = {
            "assignment_id": assignment.id,
            "assignment_status": assignment.status.value,
            "worker_id": assignment.worker_id,
            "capability": assignment.capability,
            "room_id": assignment.room_id,
            "context_stack_id": context_stack.id if context_stack is not None else None,
            "governance_decision_id": assignment.governance_decision_id,
        }

        if assignment.status != WorkerAssignmentStatus.ASSIGNED:
            return WorkerAssignmentRoomContextRecheckResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentRoomContextRecheckOutcome.NOT_CONSIDERED,
                reasons=("assignment_status_not_considered",),
                details=details,
            )

        deny_reasons: list[str] = []
        review_reasons: list[str] = []

        self._check_assignment_room(assignment, deny_reasons)
        self._check_evidence_room(assignment, deny_reasons, details)
        self._check_worker_home_room(assignment, review_reasons, deny_reasons, details)
        self._check_context(
            assignment=assignment,
            context_stack=context_stack,
            context_frames=list(context_frames or ()),
            deny_reasons=deny_reasons,
            review_reasons=review_reasons,
            details=details,
        )
        self._check_room_flow(
            source_room_id=source_room_id,
            target_room_id=target_room_id,
            deny_reasons=deny_reasons,
            review_reasons=review_reasons,
            details=details,
        )

        if deny_reasons:
            return WorkerAssignmentRoomContextRecheckResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentRoomContextRecheckOutcome.DENY,
                reasons=tuple(deny_reasons),
                details=details,
            )

        if review_reasons:
            return WorkerAssignmentRoomContextRecheckResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentRoomContextRecheckOutcome.REQUIRE_REVIEW,
                reasons=tuple(review_reasons),
                details=details,
            )

        return WorkerAssignmentRoomContextRecheckResult(
            assignment_id=assignment.id,
            outcome=WorkerAssignmentRoomContextRecheckOutcome.ALLOW,
            reasons=("room_context_recheck_passed",),
            details=details,
        )

    @staticmethod
    def _check_assignment_room(
        assignment: WorkerAssignment,
        deny_reasons: list[str],
    ) -> None:
        if not assignment.room_id:
            _append_reason(deny_reasons, "room_missing")

    def _check_evidence_room(
        self,
        assignment: WorkerAssignment,
        deny_reasons: list[str],
        details: dict[str, Any],
    ) -> None:
        decision = self.decisions.get(assignment.governance_decision_id)
        evidence_room_id = _evidence_room_id(decision)
        details["evidence_room_id"] = evidence_room_id
        if evidence_room_id != assignment.room_id:
            _append_reason(deny_reasons, "room_evidence_mismatch")

    def _check_worker_home_room(
        self,
        assignment: WorkerAssignment,
        review_reasons: list[str],
        deny_reasons: list[str],
        details: dict[str, Any],
    ) -> None:
        profile = self.workers.get_profile(assignment.worker_id)
        details["worker_home_room_id"] = (
            profile.home_room_id if profile is not None else None
        )
        if profile is None:
            _append_reason(deny_reasons, "worker_unknown")
            return
        if profile.home_room_id != assignment.room_id:
            _append_reason(review_reasons, "worker_home_room_mismatch")

    def _check_context(
        self,
        *,
        assignment: WorkerAssignment,
        context_stack: ContextStack | None,
        context_frames: list[ContextFrame],
        deny_reasons: list[str],
        review_reasons: list[str],
        details: dict[str, Any],
    ) -> None:
        if context_stack is None:
            _append_reason(review_reasons, "context_stack_not_evaluated")
            details["context_frame_ids"] = []
            return

        frame_by_id = {frame.id: frame for frame in context_frames}
        missing_frame_ids = [
            frame_id for frame_id in context_stack.frame_ids if frame_id not in frame_by_id
        ]
        details["context_frame_ids"] = list(context_stack.frame_ids)
        details["missing_context_frame_ids"] = missing_frame_ids
        if missing_frame_ids:
            _append_reason(review_reasons, "context_stack_missing")

        for frame_id in context_stack.frame_ids:
            frame = frame_by_id.get(frame_id)
            if frame is None:
                continue
            if frame.room_id is not None and frame.room_id != assignment.room_id:
                _append_reason(deny_reasons, "context_room_mismatch")
            if assignment.capability in frame.denied_capabilities:
                _append_reason(deny_reasons, "context_policy_mismatch")
            if (
                frame.allowed_capabilities
                and assignment.capability not in frame.allowed_capabilities
            ):
                _append_reason(deny_reasons, "context_policy_mismatch")

    def _check_room_flow(
        self,
        *,
        source_room_id: str | None,
        target_room_id: str | None,
        deny_reasons: list[str],
        review_reasons: list[str],
        details: dict[str, Any],
    ) -> None:
        if source_room_id is None or target_room_id is None:
            return

        decision = self.room_flow.decide(
            source_room=_room(source_room_id),
            target_room=_room(target_room_id),
        )
        details["room_flow"] = {
            "decision": decision.decision.value,
            "reason": decision.reason,
            "source_room_id": decision.source_room_id,
            "target_room_id": decision.target_room_id,
        }
        if decision.decision == RoomFlowDecisionType.BLOCK:
            _append_reason(deny_reasons, "room_flow_blocked")
        elif decision.decision == RoomFlowDecisionType.REVIEW:
            _append_reason(review_reasons, "room_flow_review_required")


def _evidence_room_id(decision: DecisionRecord | None) -> str | None:
    if decision is None:
        return None
    governance_decision = decision.details.get("governance_decision")
    if not isinstance(governance_decision, dict):
        return None
    return decision.details.get("room_id") or governance_decision.get("room_id")


def _room(room_id: str) -> Room:
    return Room(
        id=room_id,
        name=room_id.removeprefix("room_"),
        protection_level=RoomProtectionLevel.MEDIUM,
    )


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)
