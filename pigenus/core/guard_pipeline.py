from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from pigenus.core.contract_validator import ContractValidationResult, ContractValidator
from pigenus.core.room_flow import RoomFlowDecision, RoomFlowDecisionType, RoomFlowRules
from pigenus.schemas.systemform import (
    ActorIdentity,
    CellContract,
    GovernanceDecision,
    GuardDecisionType,
    MeaningObject,
    ResourceGrant,
    Room,
)


class GuardTraceStep(BaseModel):
    """One ordered step in a storage-free guard evaluation."""

    name: str
    family: str
    decision: GuardDecisionType
    reason: str
    requires_human: bool = False
    details: dict[str, str] = Field(default_factory=dict)


class GuardPipelineResult(BaseModel):
    """Final guard result with an ordered explanation trace."""

    allowed: bool
    decision: GuardDecisionType
    family: str
    reason: str
    requires_human: bool = False
    trace: list[GuardTraceStep]


class GuardPipeline:
    """Composes storage-free contract validation and optional room-flow checks."""

    def __init__(
        self,
        *,
        contract_validator: ContractValidator | None = None,
        room_flow_rules: RoomFlowRules | None = None,
    ) -> None:
        self.contract_validator = contract_validator or ContractValidator()
        self.room_flow_rules = room_flow_rules or RoomFlowRules()

    def evaluate(
        self,
        *,
        actor: ActorIdentity | None,
        room: Room | None,
        contract: CellContract | None,
        action: str,
        capability: str | None = None,
        resource_request: dict[str, int | float] | None = None,
        resource_grant: ResourceGrant | None = None,
        source_room: Room | None = None,
        target_room: Room | None = None,
        meaning: MeaningObject | None = None,
        now: datetime | None = None,
    ) -> GuardPipelineResult:
        trace: list[GuardTraceStep] = []

        contract_result = self.contract_validator.validate(
            actor=actor,
            room=room,
            contract=contract,
            action=action,
            capability=capability,
            resource_request=resource_request,
            resource_grant=resource_grant,
            now=now,
        )
        trace.append(_contract_step(contract_result))

        if source_room is not None and target_room is not None:
            room_flow_result = self.room_flow_rules.decide(
                source_room=source_room,
                target_room=target_room,
                meaning=meaning,
            )
            trace.append(_room_flow_step(room_flow_result))

        return _finalize(trace)

    @staticmethod
    def to_governance_decision(
        result: GuardPipelineResult,
        *,
        actor_id: str,
        room_id: str,
        event_id: str | None = None,
        rule_id: str | None = None,
    ) -> GovernanceDecision:
        """Convert the final pipeline result to a Systemform governance decision."""

        return GovernanceDecision(
            decision=result.decision,
            reason=result.reason,
            actor_id=actor_id,
            room_id=room_id,
            event_id=event_id,
            rule_id=rule_id,
            requires_human=result.requires_human,
            details={
                "trace": [step.model_dump(mode="json") for step in result.trace],
            },
        )


def _contract_step(result: ContractValidationResult) -> GuardTraceStep:
    return GuardTraceStep(
        name="contract_validation",
        family=_contract_family(result.reason),
        decision=result.decision,
        reason=result.reason,
        requires_human=result.requires_human,
    )


def _room_flow_step(result: RoomFlowDecision) -> GuardTraceStep:
    return GuardTraceStep(
        name="room_flow",
        family="room_flow",
        decision=_room_flow_to_guard(result.decision),
        reason=result.reason,
        requires_human=result.requires_human,
        details={
            "source_room_id": result.source_room_id,
            "target_room_id": result.target_room_id,
        },
    )


def _room_flow_to_guard(decision: RoomFlowDecisionType) -> GuardDecisionType:
    if decision in {RoomFlowDecisionType.ALLOW, RoomFlowDecisionType.ALLOW_READ}:
        return GuardDecisionType.ALLOW
    if decision == RoomFlowDecisionType.REVIEW:
        return GuardDecisionType.ESCALATE
    return GuardDecisionType.BLOCK


def _finalize(trace: list[GuardTraceStep]) -> GuardPipelineResult:
    for step in trace:
        if step.decision == GuardDecisionType.BLOCK:
            return GuardPipelineResult(
                allowed=False,
                decision=GuardDecisionType.BLOCK,
                family=step.family,
                reason=step.reason,
                requires_human=step.requires_human,
                trace=trace,
            )

    for step in trace:
        if step.decision == GuardDecisionType.ESCALATE:
            return GuardPipelineResult(
                allowed=False,
                decision=GuardDecisionType.ESCALATE,
                family=step.family,
                reason=step.reason,
                requires_human=True,
                trace=trace,
            )

    return GuardPipelineResult(
        allowed=True,
        decision=GuardDecisionType.ALLOW,
        family="allowed",
        reason="allowed",
        trace=trace,
    )


def _contract_family(reason: str) -> str:
    if reason.startswith("actor_"):
        return "actor"
    if reason.startswith("contract_"):
        return "contract"
    if reason.startswith("room_"):
        return "room_scope"
    if reason.startswith("capability_"):
        return "capability"
    if reason.startswith("permission_"):
        return "permission"
    if reason.startswith("resource_"):
        return "resource"
    if reason.startswith("human_"):
        return "approval"
    if reason in {"allowed", "contract_valid"}:
        return "contract"
    return "policy"
