from __future__ import annotations

from pigenus.cells.base import BaseCell
from pigenus.core.audit import AuditLogger
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.events import Event
from pigenus.schemas.memory import MemoryObject
from pigenus.storage.repositories import MemoryRepository


class MemoryWriterCell(BaseCell):
    """Writes permitted memory objects to local SQLite storage."""

    def __init__(self, repository: MemoryRepository, audit_logger: AuditLogger) -> None:
        self.repository = repository
        self.audit_logger = audit_logger

    @property
    def spec(self) -> CellSpec:
        return CellSpec(
            name="memory_writer",
            version="0.1.0",
            input_event_types=["TaskRequest", "GuardDecision"],
            output_event_types=["MemoryStored"],
            permissions=["memory_write"],
            description="Persists memory objects after guard approval.",
        )

    def write(self, task_event: Event, guard_event: Event) -> tuple[MemoryObject, Event]:
        if not guard_event.payload.get("allowed"):
            raise PermissionError(guard_event.payload.get("reason", "permission denied"))

        memory_text = str(task_event.payload.get("memory_text") or "").strip()
        if not memory_text:
            raise ValueError("TaskRequest does not contain memory_text.")

        memory = MemoryObject(
            memory_type="fact",
            context=task_event.context,
            status="active",
            content={"text": memory_text},
            human_summary=memory_text,
            importance=0.5,
            confidence=0.9,
        )
        self.repository.add(memory)
        self.audit_logger.log(
            actor=self.spec.cell_id,
            action="memory_write",
            context=task_event.context,
            details={"memory_id": memory.memory_id, "source_event_id": task_event.event_id},
        )

        event = Event(
            object_type="MemoryStored",
            context=task_event.context,
            created_by_cell=self.spec.cell_id,
            payload={
                "memory_id": memory.memory_id,
                "source_event_id": task_event.event_id,
                "human_summary": memory.human_summary,
            },
        )
        return memory, event
