from __future__ import annotations

from pydantic import ValidationError

from pigenus.schemas.systemform import (
    ActorIdentity,
    ActorStatus,
    ActorType,
    CellContract,
    ContractStatus,
    GovernanceDecision,
    GuardDecisionType,
    MeaningObject,
    ResourceGrant,
    Room,
    RoomProtectionLevel,
    Sensitivity,
    TruthStatus,
)


def test_actor_identity_serializes_as_json_contract():
    actor = ActorIdentity(
        id="cell_memory_writer_v1",
        actor_type=ActorType.CELL,
        name="memory_writer",
        version="0.1.0",
        status=ActorStatus.ACTIVE,
        created_by="human_ronny",
    )

    data = actor.model_dump(mode="json")

    assert data["actor_type"] == "cell"
    assert data["status"] == "active"
    assert data["created_at"]


def test_room_models_governed_boundary():
    room = Room(
        id="room_private",
        name="private/default",
        protection_level=RoomProtectionLevel.HIGH,
        default_policy_id="policy_private_default",
    )

    data = room.model_dump(mode="json")

    assert data["id"] == "room_private"
    assert data["protection_level"] == "high"


def test_meaning_object_requires_room_truth_and_creator():
    meaning = MeaningObject(
        type="fact",
        content={"claim": "PiGenus is the local runtime core."},
        room_id="room_developer",
        truth_status=TruthStatus.BELIEVED,
        confidence=0.75,
        sensitivity=Sensitivity.INTERNAL,
        created_by="cell_memory_proposer_v1",
    )

    data = meaning.model_dump(mode="json")

    assert meaning.id.startswith("bo_")
    assert data["truth_status"] == "believed"
    assert data["sensitivity"] == "internal"


def test_meaning_object_rejects_invalid_confidence():
    try:
        MeaningObject(
            type="fact",
            content={"claim": "Bad confidence."},
            room_id="room_developer",
            truth_status=TruthStatus.BELIEVED,
            confidence=1.5,
            sensitivity=Sensitivity.INTERNAL,
            created_by="cell_memory_proposer_v1",
        )
    except ValidationError as exc:
        assert "confidence" in str(exc)
    else:
        raise AssertionError("Expected invalid confidence to fail validation.")


def test_cell_contract_requires_scope_permissions_and_policy():
    contract = CellContract(
        actor_id="cell_memory_writer_v1",
        version="0.1.0",
        status=ContractStatus.ACTIVE,
        room_scope=["room_developer"],
        capabilities=["memory.write"],
        permissions={"memory_write": True},
        obligations=["audit.memory_write"],
        resource_limits={"max_events_per_minute": 30},
        risk_profile={"data_write": "medium"},
        governance_policy_id="policy_developer_default",
    )

    data = contract.model_dump(mode="json")

    assert contract.id.startswith("contract_")
    assert data["status"] == "active"
    assert data["permissions"] == {"memory_write": True}


def test_cell_contract_rejects_empty_permissions():
    try:
        CellContract(
            actor_id="cell_memory_writer_v1",
            version="0.1.0",
            room_scope=["room_developer"],
            permissions={},
            governance_policy_id="policy_developer_default",
        )
    except ValidationError as exc:
        assert "permissions" in str(exc)
    else:
        raise AssertionError("Expected empty permissions to fail validation.")


def test_resource_grant_models_explicit_budget():
    grant = ResourceGrant(
        actor_id="cell_memory_writer_v1",
        room_id="room_developer",
        limits={
            "cpu_ms_per_minute": 500,
            "memory_mb": 128,
            "max_events_per_minute": 30,
        },
        granted_by="human_ronny",
    )

    assert grant.id.startswith("rg_")
    assert grant.model_dump(mode="json")["limits"]["memory_mb"] == 128


def test_governance_decision_models_guard_result():
    decision = GovernanceDecision(
        decision=GuardDecisionType.ESCALATE,
        reason="human approval required",
        actor_id="cell_memory_writer_v1",
        room_id="room_private",
        event_id="evt_example",
        rule_id="rule_private_write_review",
        requires_human=True,
    )

    data = decision.model_dump(mode="json")

    assert decision.id.startswith("gdec_")
    assert data["decision"] == "escalate"
    assert data["audit_required"] is True
