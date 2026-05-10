from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from pigenus.cells.input_cell import InputCell
from pigenus.cells.memory_proposer import MemoryProposerCell
from pigenus.core.context_boundary import ContextBoundaryEngine
from pigenus.core.orchestrator import SimpleOrchestrator
from pigenus.schemas.context import Context
from pigenus.schemas.events import Event
from pigenus.storage.database import Database


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_context_schema_accepts_known_contexts():
    context = Context(name="developer/default")

    assert context.as_event_context() == {"name": "developer/default"}


def test_event_contract_rejects_unknown_contexts():
    with pytest.raises(ValidationError):
        Event(
            object_type="TaskRequest",
            context={"name": "unknown/default"},
            created_by_cell="input_cell@0.1.0",
            payload={"raw_text": "Merke dir: X", "action": "memory_write"},
        )


def test_context_boundary_allows_cell_in_allowed_context():
    engine = ContextBoundaryEngine()
    cell = InputCell()

    decision = engine.check(cell=cell.spec, context={"name": "developer/default"})

    assert decision.allowed is True
    assert decision.room_id == "room_developer"
    assert decision.protection_level == "medium"
    assert decision.reason == "context_allowed"


def test_context_boundary_blocks_cell_in_foreign_context():
    engine = ContextBoundaryEngine()
    cell = InputCell()

    decision = engine.check(cell=cell.spec, context={"name": "trading/default"})

    assert decision.allowed is False
    assert decision.room_id == "room_trading"
    assert decision.protection_level == "very_high"
    with pytest.raises(PermissionError):
        engine.require_allowed(cell=cell.spec, context={"name": "trading/default"})


def test_orchestrator_blocks_demo_in_disallowed_context_without_writing_events():
    path = db_path("context-blocked")
    orchestrator = SimpleOrchestrator(path)

    with pytest.raises(PermissionError):
        orchestrator.run_demo(context={"name": "trading/default"})
    orchestrator.close()

    database = Database(path)
    database.initialize()
    row = database.fetchone("SELECT COUNT(*) AS count FROM events")

    assert int(row["count"]) == 0
    database.close()


def test_memory_proposal_preserves_task_context():
    input_cell = InputCell()
    proposer = MemoryProposerCell()
    context = {"name": "developer/default"}

    task_event = input_cell.create_task_request("Merke dir: PiGenus ist der Zellkern.", context)
    proposal_event = proposer.propose(task_event)

    assert proposal_event.context == task_event.context
