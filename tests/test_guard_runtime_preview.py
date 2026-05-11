from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.cells.memory_writer import MemoryWriterCell
from pigenus.core.audit import AuditLogger
from pigenus.core.guard_runtime_preview import GuardPipelineRuntimePreview
from pigenus.core.orchestrator import SimpleOrchestrator
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.memory import MemoryObject
from pigenus.schemas.systemform import (
    GuardDecisionType,
    MeaningObject,
    Room,
    RoomProtectionLevel,
    Sensitivity,
    TruthStatus,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def room(room_id: str) -> Room:
    return Room(
        id=room_id,
        name=room_id.removeprefix("room_"),
        protection_level=RoomProtectionLevel.MEDIUM,
    )


def writable_cell(*, allowed_contexts: list[str] | None = None) -> CellSpec:
    return CellSpec(
        name="memory_writer",
        version="0.1.0",
        input_event_types=["MemoryProposal"],
        output_event_types=["MemoryStored"],
        permissions=["memory_write"],
        allowed_contexts=allowed_contexts or ["developer/default"],
    )


def meaning(
    *,
    room_id: str,
    sensitivity: Sensitivity,
    truth_status: TruthStatus = TruthStatus.VERIFIED,
) -> MeaningObject:
    return MeaningObject(
        type="fact",
        content={"text": "Preview meaning."},
        room_id=room_id,
        truth_status=truth_status,
        sensitivity=sensitivity,
        created_by="test",
    )


def test_runtime_preview_allows_adapted_cell_action():
    result = GuardPipelineRuntimePreview().preview_cell_action(
        cell=writable_cell(),
        context={"name": "developer/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context=room("room_sandbox"),
        meaning=meaning(room_id="room_developer", sensitivity=Sensitivity.INTERNAL),
    )

    assert result.allowed is True
    assert result.decision == GuardDecisionType.ALLOW
    assert result.family == "allowed"
    assert [step.name for step in result.trace] == ["contract_validation", "room_flow"]


def test_runtime_preview_escalates_review_flow_without_enforcing():
    result = GuardPipelineRuntimePreview().preview_cell_action(
        cell=writable_cell(allowed_contexts=["private/default", "family/default"]),
        context={"name": "private/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context=room("room_family"),
        meaning=meaning(room_id="room_private", sensitivity=Sensitivity.PRIVATE),
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.ESCALATE
    assert result.family == "room_flow"
    assert result.reason == "matrix_review"
    assert result.requires_human is True


def test_runtime_preview_blocks_sensitive_public_export():
    result = GuardPipelineRuntimePreview().preview_cell_action(
        cell=writable_cell(allowed_contexts=["private/default"]),
        context={"name": "private/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context=room("room_public"),
        meaning=meaning(room_id="room_private", sensitivity=Sensitivity.PRIVATE),
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.BLOCK
    assert result.family == "room_flow"
    assert result.reason == "sensitive_meaning_public_export_blocked"


def test_runtime_preview_applies_truth_status_override():
    result = GuardPipelineRuntimePreview().preview_cell_action(
        cell=writable_cell(),
        context={"name": "developer/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context=room("room_sandbox"),
        meaning=meaning(
            room_id="room_developer",
            sensitivity=Sensitivity.INTERNAL,
            truth_status=TruthStatus.CONTESTED,
        ),
    )

    assert result.allowed is False
    assert result.decision == GuardDecisionType.ESCALATE
    assert result.reason == "truth_status_requires_review"


def test_runtime_preview_can_use_memory_object_as_meaning_source():
    memory = MemoryObject(
        memory_type="fact",
        context={"name": "developer/default"},
        status="canonical",
        content={"text": "PiGenus has a runtime preview."},
        human_summary="PiGenus has a runtime preview.",
        confidence=0.9,
    )

    result = GuardPipelineRuntimePreview().preview_cell_action(
        cell=writable_cell(),
        context={"name": "developer/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context=room("room_sandbox"),
        memory=memory,
    )

    assert result.allowed is True
    assert result.trace[1].name == "room_flow"


def test_runtime_preview_does_not_mutate_orchestrator_storage_or_behavior():
    path = db_path("guard-preview-shadow")
    orchestrator = SimpleOrchestrator(path)
    starting_events = orchestrator.event_bus.count()
    starting_audits = orchestrator.audit.count()

    result = GuardPipelineRuntimePreview().preview_cell_action(
        cell=orchestrator.memory_writer.spec,
        context={"name": "developer/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
        target_context=room("room_sandbox"),
        meaning=meaning(room_id="room_developer", sensitivity=Sensitivity.INTERNAL),
    )

    assert result.decision == GuardDecisionType.ALLOW
    assert orchestrator.event_bus.count() == starting_events
    assert orchestrator.audit.count() == starting_audits

    demo = orchestrator.run_demo()

    assert demo.events_stored == 5
    assert orchestrator.event_bus.count() == starting_events + 5
    orchestrator.close()


def test_runtime_preview_does_not_mutate_repositories():
    path = db_path("guard-preview-repositories")
    database = Database(path)
    database.initialize()
    audits = AuditRepository(database)
    memory = MemoryRepository(database)
    cell = MemoryWriterCell(memory, AuditLogger(audits))

    GuardPipelineRuntimePreview().preview_cell_action(
        cell=cell.spec,
        context={"name": "developer/default"},
        action="memory_write",
        capability="consume.MemoryProposal",
    )

    assert memory.count() == 0
    assert audits.count() == 0
    database.close()
