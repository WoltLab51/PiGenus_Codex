from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.core.orchestrator import SimpleOrchestrator
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_full_demo_flow_works():
    path = db_path("demo")
    orchestrator = SimpleOrchestrator(path)

    result = orchestrator.run_demo("Merke dir: PiGenus ist der Zellkern.")
    orchestrator.close()

    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    audit_repository = AuditRepository(database)

    assert result.final_response == "Gespeichert: PiGenus ist der Zellkern."
    assert memory_repository.get(result.memory_id) is not None
    assert memory_repository.count() == 1
    assert result.events_stored == 4
    assert audit_repository.count() == 2
    database.close()


def test_demo_flow_reports_events_from_the_current_run_only():
    path = db_path("demo-repeat")
    orchestrator = SimpleOrchestrator(path)

    first = orchestrator.run_demo()
    second = orchestrator.run_demo()
    orchestrator.close()

    assert first.events_stored == 4
    assert second.events_stored == 4
