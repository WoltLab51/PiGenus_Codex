from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.context_registry import ContextRegistry
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import KNOWN_CONTEXTS
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, CellRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase26-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_context_list(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "context-list",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_context_registry_lists_known_contexts_from_schema():
    contexts = ContextRegistry().list_contexts()

    assert [context.name for context in contexts] == sorted(KNOWN_CONTEXTS)


def test_context_list_cli_prints_known_contexts_without_database():
    result = run_context_list()

    for context_name in sorted(KNOWN_CONTEXTS):
        assert context_name in result.stdout


def test_context_list_cli_can_show_registered_allowed_cells_without_mutating_storage():
    path = db_path("context-cells")
    database = Database(path)
    database.initialize()
    cells = CellRepository(database)
    cells.add(
        CellSpec(
            name="developer_cell",
            version="0.1.0",
            allowed_contexts=["developer/default"],
        )
    )
    cells.add(
        CellSpec(
            name="trading_cell",
            version="0.1.0",
            allowed_contexts=["trading/default"],
        )
    )
    cells.add(CellSpec(name="global_cell", version="0.1.0", allowed_contexts=["*"]))
    database.close()

    result = run_context_list("--db", str(path), "--show-cells")

    database = Database(path)
    assert (
        "developer/default | allowed_cells=developer_cell@0.1.0, global_cell@0.1.0"
        in result.stdout
    )
    assert "trading/default | allowed_cells=global_cell@0.1.0, trading_cell@0.1.0" in result.stdout
    assert CellRepository(database).count() == 3
    assert AuditRepository(database).count() == 0
    assert MemoryRepository(database).count() == 0
    database.close()


def test_context_list_cli_does_not_create_missing_database_when_showing_cells():
    path = db_path("missing-db")

    result = run_context_list("--db", str(path), "--show-cells")

    assert "developer/default | allowed_cells=-" in result.stdout
    assert not path.exists()
