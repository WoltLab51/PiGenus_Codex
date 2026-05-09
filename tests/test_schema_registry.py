from __future__ import annotations

import subprocess
import sys
from typing import get_args

import pytest

from pigenus.schemas.events import Event, EventType, REQUIRED_PAYLOAD_KEYS
from pigenus.schemas.registry import SchemaRegistry


def test_schema_registry_lists_all_runtime_event_types():
    registry = SchemaRegistry()

    listed_types = {contract.object_type for contract in registry.list_event_contracts()}
    runtime_types = {str(value) for value in get_args(EventType)}

    assert listed_types == runtime_types


def test_schema_registry_uses_runtime_required_payload_keys():
    registry = SchemaRegistry()

    for contract in registry.list_event_contracts():
        assert contract.required_payload_keys == tuple(
            sorted(REQUIRED_PAYLOAD_KEYS.get(contract.object_type, set()))
        )


def test_schema_registry_rejects_unknown_event_type():
    registry = SchemaRegistry()

    with pytest.raises(KeyError):
        registry.get_event_contract("UnknownEvent")


def test_schema_registry_contract_matches_event_validation():
    registry = SchemaRegistry()
    contract = registry.get_event_contract("MemoryProposal")

    payload = {key: "value" for key in contract.required_payload_keys}
    payload["content"] = {"text": "PiGenus ist der Zellkern."}
    Event(
        object_type=contract.object_type,
        context={"name": "developer/default"},
        created_by_cell="memory_proposer@0.1.0",
        payload=payload,
    )


def test_schema_list_cli_outputs_known_contracts():
    result = subprocess.run(
        [sys.executable, "-m", "pigenus.cli.main", "schema-list"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "MemoryProposal | schema 1.0 | required:" in result.stdout
    assert "source_event_id" in result.stdout
    assert "TaskRequest | schema 1.0 | required:" in result.stdout
