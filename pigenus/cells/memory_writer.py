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
            input_event_types=["MemoryProposal", "GuardDecision"],
            output_event_types=["MemoryStored"],
            permissions=["memory_write"],
            description="Persists memory objects after guard approval.",
        )

    def write(self, proposal_event: Event, guard_event: Event) -> tuple[MemoryObject, Event]:
        if proposal_event.object_type != "MemoryProposal":
            raise ValueError("MemoryWriterCell only accepts MemoryProposal events.")

        if not guard_event.payload.get("allowed"):
            raise PermissionError(guard_event.payload.get("reason", "permission denied"))

        if guard_event.payload.get("source_event_id") != proposal_event.event_id:
            raise PermissionError("guard decision does not match memory proposal")

        human_summary = str(proposal_event.payload.get("human_summary") or "").strip()
        if not human_summary:
            raise ValueError("MemoryProposal does not contain human_summary.")

        memory = MemoryObject(
            memory_type=str(proposal_event.payload["memory_type"]),
            context=proposal_event.context,
            status="active",
            content=dict(proposal_event.payload["content"]),
            human_summary=human_summary,
            importance=float(proposal_event.payload.get("importance", 0.5)),
            confidence=float(proposal_event.payload.get("confidence", 0.5)),
        )
        self.repository.add(memory)
        self.audit_logger.log(
            actor=self.spec.cell_id,
            action="memory_write",
            context=proposal_event.context,
            details={
                "memory_id": memory.memory_id,
                "proposal_event_id": proposal_event.event_id,
                "source_event_id": proposal_event.payload["source_event_id"],
            },
        )

        event = Event(
            object_type="MemoryStored",
            context=proposal_event.context,
            created_by_cell=self.spec.cell_id,
            payload={
                "memory_id": memory.memory_id,
                "source_event_id": proposal_event.payload["source_event_id"],
                "proposal_event_id": proposal_event.event_id,
                "human_summary": memory.human_summary,
            },
        )
        return memory, event
