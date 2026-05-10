from __future__ import annotations

import pytest
from pydantic import ValidationError

from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import Context
from pigenus.schemas.memory import MemoryObject
from pigenus.schemas.systemform import ContractStatus, RoomProtectionLevel, Sensitivity, TruthStatus
from pigenus.schemas.systemform_adapters import (
    cell_spec_actor_id,
    cell_spec_to_contract,
    context_to_room,
    memory_to_meaning_object,
)


def test_context_to_room_maps_known_context_to_systemform_room():
    room = context_to_room(Context(name="private/default"))

    assert room.id == "room_private"
    assert room.name == "private/default"
    assert room.protection_level == RoomProtectionLevel.HIGH
    assert room.default_policy_id == "policy_private_default"


def test_context_to_room_rejects_unknown_contexts():
    with pytest.raises(ValidationError):
        context_to_room({"name": "unknown/default"})


def test_memory_to_meaning_object_preserves_semantic_payload_and_boundary():
    memory = MemoryObject(
        memory_id="mem_example",
        memory_type="fact",
        context={"name": "family/default"},
        status="canonical",
        content={"text": "PiGenus has a working runtime prototype."},
        human_summary="PiGenus has a working runtime prototype.",
        confidence=0.9,
    )

    meaning = memory_to_meaning_object(memory, created_by="cell_memory_writer_v1")

    assert meaning.id == "bo_from_mem_example"
    assert meaning.type == "fact"
    assert meaning.content == memory.content
    assert meaning.room_id == "room_family"
    assert meaning.truth_status == TruthStatus.VERIFIED
    assert meaning.sensitivity == Sensitivity.FAMILY
    assert meaning.source == "memory:mem_example"
    assert meaning.provenance[0]["source_model"] == "MemoryObject"
    assert meaning.created_at == memory.created_at


def test_memory_to_meaning_object_maps_aged_memory_truth_status():
    memory = MemoryObject(
        memory_type="fact",
        context={"name": "developer/default"},
        status="fossil",
        content={"text": "Old runtime note."},
        human_summary="Old runtime note.",
    )

    meaning = memory_to_meaning_object(memory)

    assert meaning.truth_status == TruthStatus.HISTORICAL
    assert meaning.sensitivity == Sensitivity.INTERNAL


def test_cell_spec_to_contract_maps_executable_metadata():
    spec = CellSpec(
        name="memory_writer",
        version="0.1.0",
        input_event_types=["MemoryProposal", "GuardDecision"],
        output_event_types=["MemoryStored"],
        permissions=["memory_write"],
        allowed_contexts=["developer/default", "private/default"],
        description="Persists approved memory.",
    )

    contract = cell_spec_to_contract(spec, governance_policy_id="policy_memory_write")

    assert contract.id == "contract_memory_writer_0_1_0"
    assert contract.actor_id == "cell_memory_writer_0_1_0"
    assert contract.status == ContractStatus.ACTIVE
    assert contract.room_scope == ["room_developer", "room_private"]
    assert contract.permissions == {"memory_write": True}
    assert "consume.MemoryProposal" in contract.capabilities
    assert "emit.MemoryStored" in contract.capabilities
    assert contract.governance_policy_id == "policy_memory_write"


def test_cell_spec_to_contract_gives_permissionless_cells_execute_only():
    spec = CellSpec(
        name="input_cell",
        version="0.1.0",
        input_event_types=["UserInput"],
        output_event_types=["TaskRequest"],
        permissions=[],
    )

    contract = cell_spec_to_contract(spec)

    assert contract.permissions == {"execute": True}


def test_cell_spec_actor_id_is_stable_and_sanitized():
    spec = CellSpec(name="rule_guard", version="0.1.0")

    assert cell_spec_actor_id(spec) == "cell_rule_guard_0_1_0"
