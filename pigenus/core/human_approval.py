from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from pigenus.schemas.base import new_id, utc_now
from pigenus.schemas.context import Context
from pigenus.schemas.decisions import DecisionRecord
from pigenus.storage.repositories import DecisionRepository


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HumanApprovalRecord(BaseModel):
    """Minimal approval placeholder linked to a governance decision."""

    approval_id: str = Field(default_factory=lambda: new_id("approval"))
    governance_decision_id: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_by: str
    context: dict[str, Any] = Field(default_factory=dict)
    reason: str
    resolved_by: str | None = None
    resolution_reason: str | None = None
    created_at: str = Field(default_factory=lambda: utc_now().isoformat())
    resolved_at: str | None = None


class HumanApprovalLog:
    """Persists approval placeholders through the existing decision log."""

    def __init__(self, repository: DecisionRepository) -> None:
        self.repository = repository

    def create_pending(
        self,
        *,
        governance_decision_id: str,
        requested_by: str,
        context: Context | dict[str, Any],
        reason: str,
    ) -> HumanApprovalRecord:
        record = HumanApprovalRecord(
            governance_decision_id=governance_decision_id,
            requested_by=requested_by,
            context=Context.model_validate(context).as_event_context(),
            reason=reason,
        )
        self.repository.add(human_approval_to_decision_record(record))
        return record

    def approve(
        self,
        approval: HumanApprovalRecord,
        *,
        resolved_by: str,
        reason: str = "approved",
    ) -> HumanApprovalRecord:
        resolved = _resolve(approval, ApprovalStatus.APPROVED, resolved_by, reason)
        self.repository.add(human_approval_to_decision_record(resolved))
        return resolved

    def reject(
        self,
        approval: HumanApprovalRecord,
        *,
        resolved_by: str,
        reason: str = "rejected",
    ) -> HumanApprovalRecord:
        resolved = _resolve(approval, ApprovalStatus.REJECTED, resolved_by, reason)
        self.repository.add(human_approval_to_decision_record(resolved))
        return resolved


def human_approval_to_decision_record(approval: HumanApprovalRecord) -> DecisionRecord:
    data = approval.model_dump(mode="json")
    return DecisionRecord(
        decision_type="human_approval",
        context=approval.context,
        subject_id=approval.governance_decision_id,
        actor=approval.resolved_by or approval.requested_by,
        reason=approval.resolution_reason or approval.reason,
        source="human_approval_stub",
        created_at=utc_now(),
        details={
            "approval": data,
            "approval_id": approval.approval_id,
            "governance_decision_id": approval.governance_decision_id,
            "status": data["status"],
        },
    )


def _resolve(
    approval: HumanApprovalRecord,
    status: ApprovalStatus,
    resolved_by: str,
    reason: str,
) -> HumanApprovalRecord:
    data = approval.model_dump(mode="json")
    data["status"] = status
    data["resolved_by"] = resolved_by
    data["resolution_reason"] = reason
    data["resolved_at"] = utc_now().isoformat()
    return HumanApprovalRecord.model_validate(data)
