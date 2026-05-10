from __future__ import annotations

from datetime import timedelta

from pigenus.core.contract_validator import ContractValidator
from pigenus.schemas.base import utc_now
from pigenus.schemas.systemform import (
    ActorIdentity,
    ActorStatus,
    ActorType,
    CellContract,
    ContractStatus,
    GuardDecisionType,
    ResourceGrant,
    Room,
    RoomProtectionLevel,
)


def actor(status: ActorStatus = ActorStatus.ACTIVE) -> ActorIdentity:
    return ActorIdentity(
        id="cell_memory_writer_0_1_0",
        actor_type=ActorType.CELL,
        name="memory_writer",
        version="0.1.0",
        status=status,
    )


def room() -> Room:
    return Room(
        id="room_developer",
        name="developer/default",
        protection_level=RoomProtectionLevel.MEDIUM,
    )


def contract(**overrides) -> CellContract:
    data = {
        "id": "contract_memory_writer_0_1_0",
        "actor_id": "cell_memory_writer_0_1_0",
        "version": "0.1.0",
        "status": ContractStatus.ACTIVE,
        "room_scope": ["room_developer"],
        "capabilities": ["consume.MemoryProposal", "emit.MemoryStored"],
        "permissions": {"memory_write": True},
        "resource_limits": {"max_events_per_minute": 30, "memory_mb": 128},
        "governance_policy_id": "policy_runtime_default",
    }
    data.update(overrides)
    return CellContract(**data)


def grant(**overrides) -> ResourceGrant:
    data = {
        "actor_id": "cell_memory_writer_0_1_0",
        "room_id": "room_developer",
        "limits": {"max_events_per_minute": 10, "memory_mb": 64},
        "granted_by": "human_ronny",
    }
    data.update(overrides)
    return ResourceGrant(**data)


def test_contract_validator_allows_valid_request():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="memory_write",
        capability="consume.MemoryProposal",
        resource_request={"max_events_per_minute": 5},
        resource_grant=grant(),
    )

    assert result.allowed is True
    assert result.decision == GuardDecisionType.ALLOW
    assert result.reason == "allowed"


def test_contract_validator_blocks_missing_actor():
    result = ContractValidator().validate(
        actor=None,
        room=room(),
        contract=contract(),
        action="memory_write",
    )

    assert result.allowed is False
    assert result.reason == "actor_missing"


def test_contract_validator_blocks_revoked_actor():
    result = ContractValidator().validate(
        actor=actor(ActorStatus.REVOKED),
        room=room(),
        contract=contract(),
        action="memory_write",
    )

    assert result.decision == GuardDecisionType.BLOCK
    assert result.reason == "actor_revoked"


def test_contract_validator_blocks_inactive_contract():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(status=ContractStatus.DRAFT),
        action="memory_write",
    )

    assert result.reason == "contract_not_active"


def test_contract_validator_blocks_expired_contract_by_timestamp():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(expires_at=utc_now() - timedelta(seconds=1)),
        action="memory_write",
    )

    assert result.reason == "contract_expired"


def test_contract_validator_blocks_room_outside_scope():
    result = ContractValidator().validate(
        actor=actor(),
        room=Room(
            id="room_private",
            name="private/default",
            protection_level=RoomProtectionLevel.HIGH,
        ),
        contract=contract(),
        action="memory_write",
    )

    assert result.reason == "room_not_allowed"


def test_contract_validator_blocks_unknown_capability():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="memory_write",
        capability="external.network_call",
    )

    assert result.reason == "capability_not_allowed"


def test_contract_validator_blocks_missing_permission():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="external_call",
    )

    assert result.reason == "permission_not_allowed"


def test_contract_validator_blocks_missing_resource_grant_for_resource_request():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="memory_write",
        resource_request={"max_events_per_minute": 5},
    )

    assert result.reason == "resource_grant_missing"


def test_contract_validator_blocks_resource_request_above_contract_limit():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="memory_write",
        resource_request={"memory_mb": 256},
        resource_grant=grant(limits={"memory_mb": 512}),
    )

    assert result.reason == "resource_limit_exceeded"


def test_contract_validator_blocks_resource_request_above_grant_limit():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="memory_write",
        resource_request={"memory_mb": 96},
        resource_grant=grant(),
    )

    assert result.reason == "resource_grant_limit_exceeded"


def test_contract_validator_escalates_human_approval_actions():
    result = ContractValidator().validate(
        actor=actor(),
        room=room(),
        contract=contract(human_approval_required=["memory_write"]),
        action="memory_write",
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.ESCALATE
    assert result.reason == "human_approval_required"
    assert result.requires_human is True


def test_contract_validator_converts_result_to_governance_decision():
    validator = ContractValidator()
    result = validator.validate(
        actor=actor(),
        room=room(),
        contract=contract(),
        action="memory_write",
    )

    decision = validator.to_governance_decision(
        result,
        actor_id="cell_memory_writer_0_1_0",
        room_id="room_developer",
        event_id="evt_example",
    )

    assert decision.decision == GuardDecisionType.ALLOW
    assert decision.reason == "allowed"
    assert decision.actor_id == "cell_memory_writer_0_1_0"
    assert decision.room_id == "room_developer"
    assert decision.event_id == "evt_example"
