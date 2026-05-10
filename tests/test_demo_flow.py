from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.core.orchestrator import SimpleOrchestrator
from pigenus.schemas.cells import CellSpec
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, DecisionRepository, MemoryRepository


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
    decision_repository = DecisionRepository(database)

    assert result.final_response == "Gespeichert: PiGenus ist der Zellkern."
    assert memory_repository.get(result.memory_id) is not None
    assert memory_repository.count() == 1
    assert result.events_stored == 5
    assert audit_repository.count() == 2
    assert decision_repository.count() == 1
    assert decision_repository.list()[0].decision_type == "governance_decision"
    database.close()


def test_demo_flow_reports_events_from_the_current_run_only():
    path = db_path("demo-repeat")
    orchestrator = SimpleOrchestrator(path)

    first = orchestrator.run_demo()
    second = orchestrator.run_demo()
    orchestrator.close()

    assert first.events_stored == 5
    assert second.events_stored == 5


def test_orchestrator_guard_preview_logs_review_without_stopping_later_demo():
    path = db_path("demo-preview-block")
    orchestrator = SimpleOrchestrator(path)
    preview_cell = CellSpec(
        name="memory_writer",
        version="0.1.0",
        input_event_types=["MemoryProposal"],
        output_event_types=["MemoryStored"],
        permissions=["memory_write"],
        allowed_contexts=["private/default"],
    )

    orchestrator.preview_guard_for_cell(
        cell=preview_cell,
        context={"name": "private/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context={"name": "family/default"},
        source_event_id="evt_preview",
    )
    demo = orchestrator.run_demo()
    orchestrator.close()

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()

    assert demo.events_stored == 5
    assert len(decisions) == 2
    assert decisions[0].source == "orchestrator_guard_preview"
    assert decisions[0].details["decision"] == "escalate"
    assert decisions[1].details["decision"] == "allow"
    database.close()
