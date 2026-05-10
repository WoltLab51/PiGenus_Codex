from __future__ import annotations

from pigenus.core.guard_pipeline import GuardPipeline
from pigenus.schemas.systemform import (
    ActorIdentity,
    ActorStatus,
    ActorType,
    CellContract,
    ContractStatus,
    GovernanceDecision,
    GuardDecisionType,
    MeaningObject,
    Room,
    RoomProtectionLevel,
    Sensitivity,
    TruthStatus,
)


def actor(status: ActorStatus = ActorStatus.ACTIVE) -> ActorIdentity:
    return ActorIdentity(
        id="cell_memory_writer_0_1_0",
        actor_type=ActorType.CELL,
        name="memory_writer",
        version="0.1.0",
        status=status,
    )


def room(room_id: str) -> Room:
    return Room(
        id=room_id,
        name=room_id.removeprefix("room_"),
        protection_level=RoomProtectionLevel.MEDIUM,
    )


def contract(**overrides) -> CellContract:
    data = {
        "actor_id": "cell_memory_writer_0_1_0",
        "version": "0.1.0",
        "status": ContractStatus.ACTIVE,
        "room_scope": ["room_developer", "room_private", "room_family"],
        "capabilities": ["consume.MemoryProposal"],
        "permissions": {"memory_write": True},
        "governance_policy_id": "policy_runtime_default",
    }
    data.update(overrides)
    return CellContract(**data)


def meaning(
    *,
    room_id: str = "room_developer",
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
    truth_status: TruthStatus = TruthStatus.VERIFIED,
) -> MeaningObject:
    return MeaningObject(
        type="fact",
        content={"text": "Guard pipeline test meaning."},
        room_id=room_id,
        truth_status=truth_status,
        sensitivity=sensitivity,
        created_by="test",
    )


def test_guard_pipeline_allows_when_contract_and_room_flow_allow():
    result = GuardPipeline().evaluate(
        actor=actor(),
        room=room("room_developer"),
        contract=contract(),
        action="memory_write",
        capability="consume.MemoryProposal",
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(),
    )

    assert result.allowed is True
    assert result.decision == GuardDecisionType.ALLOW
    assert result.reason == "allowed"
    assert [step.name for step in result.trace] == ["contract_validation", "room_flow"]


def test_guard_pipeline_blocks_when_contract_validation_blocks():
    result = GuardPipeline().evaluate(
        actor=actor(ActorStatus.REVOKED),
        room=room("room_developer"),
        contract=contract(),
        action="memory_write",
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(),
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.BLOCK
    assert result.reason == "actor_revoked"
    assert len(result.trace) == 2


def test_guard_pipeline_blocks_take_precedence_over_room_review():
    result = GuardPipeline().evaluate(
        actor=actor(),
        room=room("room_developer"),
        contract=contract(permissions={"memory_write": False}),
        action="memory_write",
        source_room=room("room_private"),
        target_room=room("room_family"),
        meaning=meaning(room_id="room_private", sensitivity=Sensitivity.PRIVATE),
    )

    assert result.decision == GuardDecisionType.BLOCK
    assert result.reason == "permission_not_allowed"
    assert result.trace[0].reason == "permission_not_allowed"
    assert result.trace[1].reason == "matrix_review"


def test_guard_pipeline_escalates_when_contract_requires_human_approval():
    result = GuardPipeline().evaluate(
        actor=actor(),
        room=room("room_developer"),
        contract=contract(human_approval_required=["memory_write"]),
        action="memory_write",
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.ESCALATE
    assert result.reason == "human_approval_required"
    assert result.requires_human is True
    assert [step.name for step in result.trace] == ["contract_validation"]


def test_guard_pipeline_escalates_when_room_flow_requires_review():
    result = GuardPipeline().evaluate(
        actor=actor(),
        room=room("room_private"),
        contract=contract(room_scope=["room_private"]),
        action="memory_write",
        source_room=room("room_private"),
        target_room=room("room_family"),
        meaning=meaning(room_id="room_private", sensitivity=Sensitivity.PRIVATE),
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.ESCALATE
    assert result.reason == "matrix_review"
    assert result.requires_human is True


def test_guard_pipeline_blocks_when_room_flow_blocks():
    result = GuardPipeline().evaluate(
        actor=actor(),
        room=room("room_private"),
        contract=contract(room_scope=["room_private"]),
        action="memory_write",
        source_room=room("room_private"),
        target_room=room("room_public"),
        meaning=meaning(room_id="room_private", sensitivity=Sensitivity.PRIVATE),
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.BLOCK
    assert result.reason == "sensitive_meaning_public_export_blocked"


def test_guard_pipeline_converts_final_result_to_governance_decision_with_trace():
    pipeline = GuardPipeline()
    result = pipeline.evaluate(
        actor=actor(),
        room=room("room_developer"),
        contract=contract(),
        action="memory_write",
    )

    decision = pipeline.to_governance_decision(
        result,
        actor_id="cell_memory_writer_0_1_0",
        room_id="room_developer",
        event_id="evt_example",
    )

    assert isinstance(decision, GovernanceDecision)
    assert decision.decision == GuardDecisionType.ALLOW
    assert decision.reason == "allowed"
    assert decision.details["trace"][0]["name"] == "contract_validation"
