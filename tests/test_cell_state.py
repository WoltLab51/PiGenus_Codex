from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.orchestrator import SimpleOrchestrator
from pigenus.schemas.cells import CellSpec, CellState
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, CellRepository, CellStateRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_cell_state_is_persisted_separately_from_core_memory():
    database = Database(db_path("cell-state"))
    database.initialize()
    states = CellStateRepository(database)
    memory = MemoryRepository(database)

    state = CellState(
        cell_id="memory_proposer@0.1.0",
        state={"failure_count": 0, "last_cursor": "batch-1"},
    )
    states.set(state)

    assert states.get("memory_proposer@0.1.0") == state
    assert states.count() == 1
    assert memory.count() == 0
    database.close()


def test_cell_repository_lists_registered_cells_and_updates_last_used_at():
    database = Database(db_path("cell-lifecycle"))
    database.initialize()
    cells = CellRepository(database)
    spec = CellSpec(
        name="example_cell",
        version="0.1.0",
        status="watch",
        fitness=0.25,
    )

    cells.add(spec)
    updated = cells.touch(spec.cell_id, used_at="2026-05-09T12:00:00+00:00")

    assert updated is not None
    assert updated.status == "watch"
    assert updated.fitness == 0.25
    assert updated.last_used_at is not None
    assert updated.last_used_at.isoformat() == "2026-05-09T12:00:00+00:00"
    assert cells.list() == [updated]
    database.close()


def test_cell_repository_preserves_lifecycle_fields_when_reregistering():
    database = Database(db_path("cell-reregister"))
    database.initialize()
    cells = CellRepository(database)
    spec = CellSpec(name="example_cell", version="0.1.0")
    cells.add(spec)
    cells.touch(spec.cell_id, used_at="2026-05-09T12:00:00+00:00")

    cells.add(
        CellSpec(
            name="example_cell",
            version="0.1.0",
            input_event_types=["TaskRequest"],
            status="active",
        )
    )

    updated = cells.get(spec.cell_id)
    assert updated is not None
    assert updated.input_event_types == ["TaskRequest"]
    assert updated.last_used_at is not None
    assert updated.last_used_at.isoformat() == "2026-05-09T12:00:00+00:00"
    database.close()


def test_orchestrator_registers_cells_and_updates_last_used_at():
    path = db_path("orchestrated-cells")
    orchestrator = SimpleOrchestrator(path)

    orchestrator.run_demo()
    orchestrator.close()

    database = Database(path)
    database.initialize()
    cells = CellRepository(database).list()

    assert {cell.cell_id for cell in cells} == {
        "explain_cell@0.1.0",
        "input_cell@0.1.0",
        "memory_proposer@0.1.0",
        "memory_writer@0.1.0",
        "rule_guard@0.1.0",
    }
    assert all(cell.status == "active" for cell in cells)
    assert all(cell.last_used_at is not None for cell in cells)
    database.close()


def test_cell_list_cli_is_read_only_and_filters_by_status():
    path = db_path("cell-list")
    database = Database(path)
    database.initialize()
    cells = CellRepository(database)
    cells.add(CellSpec(name="active_cell", version="0.1.0", status="active"))
    cells.add(CellSpec(name="watch_cell", version="0.1.0", status="watch"))
    database.close()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "cell-list",
            "--db",
            str(path),
            "--status",
            "watch",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    database = Database(path)
    database.initialize()
    assert "watch_cell@0.1.0 | watch | fitness=0.00 | last_used_at=-" in result.stdout
    assert "active_cell" not in result.stdout
    assert CellRepository(database).count() == 2
    assert AuditRepository(database).count() == 0
    database.close()


def test_cell_list_cli_reports_empty_database():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "cell-list",
            "--db",
            str(db_path("empty-cells")),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "No cells found." in result.stdout
