from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.schemas.cells import CellState
from pigenus.storage.database import Database
from pigenus.storage.repositories import CellStateRepository, MemoryRepository


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
