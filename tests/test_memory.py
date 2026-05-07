from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.cells.input_cell import InputCell
from pigenus.cells.memory_writer import MemoryWriterCell
from pigenus.cells.rule_guard import RuleGuardCell
from pigenus.schemas.events import Event
from pigenus.core.audit import AuditLogger
from pigenus.core.permissions import PermissionEngine
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
    guard_cell = RuleGuardCell(PermissionEngine(), audit)
    writer = MemoryWriterCell(memory_repository, audit)

    task_event = input_cell.create_task_request(
        "Merke dir: PiGenus ist der Zellkern.",
        {"name": "developer/default"},
    )
    guard_event = guard_cell.check(task_event)
    memory, stored_event = writer.write(task_event, guard_event)

    assert stored_event.object_type == "MemoryStored"
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
    writer = MemoryWriterCell(memory_repository, audit)

    task_event = input_cell.create_task_request("Nicht speichern.", {"name": "developer/default"})
    guard_event = Event(
        object_type="GuardDecision",
        context=task_event.context,
        created_by_cell="rule_guard@0.1.0",
        payload={"allowed": False, "reason": "action_not_allowed"},
    )

    try:
        writer.write(task_event, guard_event)
    except PermissionError as exc:
        assert str(exc) == "action_not_allowed"
    else:
        raise AssertionError("Expected denied guard decision to raise PermissionError.")

    assert memory_repository.count() == 0
    database.close()
