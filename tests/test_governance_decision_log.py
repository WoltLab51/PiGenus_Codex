from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.core.governance_decision_log import (
    GovernanceDecisionLogger,
    governance_decision_to_record,
)
from pigenus.core.guard_pipeline import GuardPipeline
from pigenus.schemas.systemform import (
    ActorIdentity,
    ActorStatus,
    ActorType,
    CellContract,
    ContractStatus,
    GovernanceDecision,
    GuardDecisionType,
    Room,
    RoomProtectionLevel,
    Sensitivity,
    TruthStatus,
    MeaningObject,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import DecisionRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "governance-decision-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def actor() -> ActorIdentity:
    return ActorIdentity(
        id="cell_memory_writer_0_1_0",
        actor_type=ActorType.CELL,
        name="memory_writer",
        version="0.1.0",
        status=ActorStatus.ACTIVE,
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
        "room_scope": ["room_developer", "room_private"],
        "capabilities": ["consume.MemoryProposal"],
        "permissions": {"memory_write": True},
        "governance_policy_id": "policy_runtime_default",
    }
    data.update(overrides)
    return CellContract(**data)


def meaning(*, sensitivity: Sensitivity, room_id: str = "room_developer") -> MeaningObject:
    return MeaningObject(
        type="fact",
        content={"text": "Governance decision test meaning."},
        room_id=room_id,
        truth_status=TruthStatus.VERIFIED,
        sensitivity=sensitivity,
        created_by="test",
    )


def pipeline_decision(
    *,
    source_room_id: str = "room_developer",
    target_room_id: str | None = "room_sandbox",
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
    contract_override: dict | None = None,
) -> GovernanceDecision:
    pipeline = GuardPipeline()
    source_room = room(source_room_id)
    target_room = room(target_room_id) if target_room_id is not None else None
    result = pipeline.evaluate(
        actor=actor(),
        room=source_room,
        contract=contract(**(contract_override or {})),
        action="memory_write",
        capability="consume.MemoryProposal",
        source_room=source_room if target_room is not None else None,
        target_room=target_room,
        meaning=meaning(sensitivity=sensitivity, room_id=source_room_id),
    )
    return pipeline.to_governance_decision(
        result,
        actor_id="cell_memory_writer_0_1_0",
        room_id=source_room_id,
        event_id="evt_example",
    )


def test_governance_decision_logger_persists_allow_decision():
    path = db_path("allow")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    logger = GovernanceDecisionLogger(repository)
    decision = pipeline_decision()

    record = logger.add(decision)

    stored = repository.list()[0]
    assert repository.count() == 1
    assert stored == record
    assert stored.decision_type == "governance_decision"
    assert stored.subject_id == "evt_example"
    assert stored.actor == "cell_memory_writer_0_1_0"
    assert stored.reason == "allowed"
    assert stored.context == {"name": "developer/default"}
    assert stored.details["decision"] == "allow"
    database.close()


def test_governance_decision_trace_order_survives_serialization():
    decision = pipeline_decision()

    record = governance_decision_to_record(decision)

    assert [step["name"] for step in record.details["trace"]] == [
        "contract_validation",
        "room_flow",
    ]


def test_governance_decision_logger_persists_block_decision():
    path = db_path("block")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    decision = pipeline_decision(
        source_room_id="room_private",
        target_room_id="room_public",
        sensitivity=Sensitivity.PRIVATE,
        contract_override={"room_scope": ["room_private"]},
    )

    GovernanceDecisionLogger(repository).add(decision, context={"name": "private/default"})

    stored = repository.list()[0]
    assert stored.context == {"name": "private/default"}
    assert stored.details["decision"] == "block"
    assert stored.details["governance_decision"]["reason"] == "sensitive_meaning_public_export_blocked"
    database.close()


def test_governance_decision_logger_persists_escalate_decision():
    path = db_path("escalate")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    decision = pipeline_decision(
        target_room_id=None,
        contract_override={"human_approval_required": ["memory_write"]},
    )

    GovernanceDecisionLogger(repository).add(decision)

    stored = repository.list()[0]
    assert stored.details["decision"] == "escalate"
    assert stored.details["requires_human"] is True
    assert stored.details["trace"][0]["reason"] == "human_approval_required"
    database.close()
