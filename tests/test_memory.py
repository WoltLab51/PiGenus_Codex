from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.cells.input_cell import InputCell
from pigenus.cells.memory_proposer import MemoryProposerCell
from pigenus.cells.memory_writer import MemoryWriterCell
from pigenus.cells.rule_guard import RuleGuardCell
from pigenus.core.audit import AuditLogger
from pigenus.core.permissions import PermissionEngine
from pigenus.schemas.events import Event
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_memory_writer_cell_stores_a_memory_object():
    database = Database(db_path("memory"))
    database.initialize()
    audit = AuditLogger(AuditRepository(database))
    memory_repository = MemoryRepository(database)
    input_cell = InputCell()
    proposer = MemoryProposerCell()
    guard_cell = RuleGuardCell(PermissionEngine(), audit)
    writer = MemoryWriterCell(memory_repository, audit)

    task_event = input_cell.create_task_request(
        "Merke dir: PiGenus ist der Zellkern.",
        {"name": "developer/default"},
    )
    proposal_event = proposer.propose(task_event)
    guard_event = guard_cell.check(proposal_event)
    memory, stored_event = writer.write(proposal_event, guard_event)

    assert stored_event.object_type == "MemoryStored"
    assert stored_event.payload["proposal_event_id"] == proposal_event.event_id
    assert memory_repository.get(memory.memory_id) == memory
    assert memory_repository.count() == 1
    assert audit.count() == 2
    database.close()


def test_memory_writer_cell_rejects_denied_guard_decisions():
    database = Database(db_path("memory-denied"))
    database.initialize()
    audit = AuditLogger(AuditRepository(database))
    memory_repository = MemoryRepository(database)
    input_cell = InputCell()
    proposer = MemoryProposerCell()
    writer = MemoryWriterCell(memory_repository, audit)

    task_event = input_cell.create_task_request("Nicht speichern.", {"name": "developer/default"})
    proposal_event = proposer.propose(
        input_cell.create_task_request(
            "Merke dir: PiGenus ist der Zellkern.",
            {"name": "developer/default"},
        )
    )
    guard_event = Event(
        object_type="GuardDecision",
        context=task_event.context,
        created_by_cell="rule_guard@0.1.0",
        payload={
            "action": "unknown_critical_action",
            "allowed": False,
            "reason": "action_not_allowed",
            "blocking_cell": "rule_guard@0.1.0",
            "source_event_id": proposal_event.event_id,
        },
    )

    try:
        writer.write(proposal_event, guard_event)
    except PermissionError as exc:
        assert str(exc) == "action_not_allowed"
    else:
        raise AssertionError("Expected denied guard decision to raise PermissionError.")

    assert memory_repository.count() == 0
    database.close()


def test_memory_writer_requires_memory_proposal_events():
    database = Database(db_path("memory-proposal-required"))
    database.initialize()
    audit = AuditLogger(AuditRepository(database))
    memory_repository = MemoryRepository(database)
    input_cell = InputCell()
    guard_cell = RuleGuardCell(PermissionEngine(), audit)
    writer = MemoryWriterCell(memory_repository, audit)

    task_event = input_cell.create_task_request(
        "Merke dir: PiGenus ist der Zellkern.",
        {"name": "developer/default"},
    )
    guard_event = guard_cell.check(task_event)

    try:
        writer.write(task_event, guard_event)
    except ValueError as exc:
        assert str(exc) == "MemoryWriterCell only accepts MemoryProposal events."
    else:
        raise AssertionError("Expected direct TaskRequest write to fail.")

    assert memory_repository.count() == 0
    database.close()


def test_memory_writer_rejects_guard_decisions_for_other_events():
    database = Database(db_path("memory-guard-mismatch"))
    database.initialize()
    audit = AuditLogger(AuditRepository(database))
    memory_repository = MemoryRepository(database)
    input_cell = InputCell()
    proposer = MemoryProposerCell()
    writer = MemoryWriterCell(memory_repository, audit)

    task_event = input_cell.create_task_request(
        "Merke dir: PiGenus ist der Zellkern.",
        {"name": "developer/default"},
    )
    proposal_event = proposer.propose(task_event)
    guard_event = Event(
        object_type="GuardDecision",
        context=proposal_event.context,
        created_by_cell="rule_guard@0.1.0",
        payload={
            "action": "memory_write",
            "allowed": True,
            "reason": "default_context_allow",
            "blocking_cell": "",
            "source_event_id": task_event.event_id,
        },
    )

    try:
        writer.write(proposal_event, guard_event)
    except PermissionError as exc:
        assert str(exc) == "guard decision does not match memory proposal"
    else:
        raise AssertionError("Expected mismatched guard decision to fail.")

    assert memory_repository.count() == 0
    database.close()
