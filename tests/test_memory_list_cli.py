from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.memory import MemoryObject
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase21-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def memory(summary: str, *, status: str = "active", context: str = "developer/default") -> MemoryObject:
    return MemoryObject(
        memory_type="fact",
        context={"name": context},
        status=status,
        content={"text": summary},
        human_summary=summary,
    )


def run_memory_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "memory-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_memory_list_reports_empty_database():
    path = db_path("empty")

    result = run_memory_list(path)

    assert result.returncode == 0
    assert "No memory objects found." in result.stdout


def test_memory_list_prints_memory_rows_without_modifying_data():
    path = db_path("rows")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    item = memory("PiGenus ist der Zellkern.")
    memory_repository.add(item)
    database.close()

    result = run_memory_list(path)

    database = Database(path)
    database.initialize()
    assert item.memory_id in result.stdout
    assert "active | developer/default | PiGenus ist der Zellkern." in result.stdout
    assert MemoryRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_memory_list_filters_by_status():
    path = db_path("status")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    memory_repository.add(memory("Active memory", status="active"))
    memory_repository.add(memory("Stale memory", status="stale"))
    database.close()

    result = run_memory_list(path, "--status", "stale")

    assert "Stale memory" in result.stdout
    assert "Active memory" not in result.stdout


def test_memory_list_filters_by_context():
    path = db_path("context")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    memory_repository.add(memory("Developer memory", context="developer/default"))
    memory_repository.add(memory("Trading memory", context="trading/default"))
    database.close()

    result = run_memory_list(path, "--context", "trading/default")

    assert "Trading memory" in result.stdout
    assert "Developer memory" not in result.stdout
