from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.runtime_overview import RuntimeOverviewBuilder
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.events import Event
from pigenus.schemas.memory import MemoryObject
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    CellRepository,
    DecisionRepository,
    EventRepository,
    MemoryRepository,
)


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase210-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_runtime_overview(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "runtime-overview",
            "--db",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def task_event() -> Event:
    return Event(
        object_type="TaskRequest",
        context={"name": "developer/default"},
        created_by_cell="input_cell@0.1.0",
        payload={"raw_text": "Merke dir: PiGenus ist der Zellkern.", "action": "memory_write"},
    )


def memory() -> MemoryObject:
    return MemoryObject(
        memory_type="fact",
        context={"name": "developer/default"},
        status="active",
        content={"text": "PiGenus ist der Zellkern."},
        human_summary="PiGenus ist der Zellkern.",
    )


def decision() -> DecisionRecord:
    return DecisionRecord(
        decision_type="memory_lifecycle_status_change",
        context={"name": "developer/default"},
        subject_id="mem_example",
        actor="memory_lifecycle@0.1.0",
        reason="review_due",
        source="automatic",
        details={"old_status": "active", "new_status": "watch"},
    )


def populate_database(path: Path) -> None:
    database = Database(path)
    database.initialize()
    EventRepository(database).add(task_event())
    MemoryRepository(database).add(memory())
    CellRepository(database).add(CellSpec(name="input_cell", version="0.1.0"))
    AuditRepository(database).add(
        actor="input_cell@0.1.0",
        action="example",
        context={"name": "developer/default"},
        details={},
    )
    DecisionRepository(database).add(decision())
    database.close()


def test_runtime_overview_builder_counts_runtime_storage_and_registries():
    path = db_path("builder")
    populate_database(path)
    database = Database(path)
    database.initialize()

    overview = RuntimeOverviewBuilder(
        events=EventRepository(database),
        memory=MemoryRepository(database),
        cells=CellRepository(database),
        audit=AuditRepository(database),
        decisions=DecisionRepository(database),
    ).build()

    assert overview.event_count == 1
    assert overview.memory_count == 1
    assert overview.cell_count == 1
    assert overview.audit_count == 1
    assert overview.decision_count == 1
    assert "developer/default" in overview.contexts
    assert "developer/default:memory_write" in overview.default_permissions
    database.close()


def test_runtime_overview_cli_prints_counts_and_static_boundaries():
    path = db_path("cli")
    populate_database(path)

    result = run_runtime_overview(path)

    assert "PiGenus Runtime Overview" in result.stdout
    assert "Events: 1" in result.stdout
    assert "Memory objects: 1" in result.stdout
    assert "Cells: 1" in result.stdout
    assert "Audit logs: 1" in result.stdout
    assert "Decision records: 1" in result.stdout
    assert "developer/default" in result.stdout
    assert "developer/default:memory_write" in result.stdout


def test_runtime_overview_cli_is_read_only():
    path = db_path("read-only")
    populate_database(path)

    run_runtime_overview(path)

    database = Database(path)
    database.initialize()
    assert EventRepository(database).count() == 1
    assert MemoryRepository(database).count() == 1
    assert CellRepository(database).count() == 1
    assert AuditRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    database.close()
