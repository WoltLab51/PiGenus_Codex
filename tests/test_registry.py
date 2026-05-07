from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.core.registry import CellRegistry
from pigenus.schemas.cells import CellSpec
from pigenus.storage.database import Database
from pigenus.storage.repositories import CellRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_cell_registry_can_register_a_cell():
    database = Database(db_path("cells"))
    database.initialize()
    registry = CellRegistry(CellRepository(database))
    spec = CellSpec(
        name="example_cell",
        version="0.1.0",
        input_event_types=["TaskRequest"],
        output_event_types=["ExampleEvent"],
        permissions=["memory_write"],
    )

    registry.register(spec)

    assert registry.get("example_cell@0.1.0") == spec
    database.close()
