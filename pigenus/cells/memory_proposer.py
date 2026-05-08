from __future__ import annotations

from pigenus.cells.base import BaseCell
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.events import Event


class MemoryProposerCell(BaseCell):
    """Turns permitted memory intent into a durable-memory proposal event."""

    @property
    def spec(self) -> CellSpec:
        return CellSpec(
            name="memory_proposer",
            version="0.1.0",
            input_event_types=["TaskRequest"],
            output_event_types=["MemoryProposal"],
            permissions=[],
            description="Proposes durable memory writes without storing them.",
        )

    def propose(self, task_event: Event) -> Event:
        memory_text = str(task_event.payload.get("memory_text") or "").strip()
        if not memory_text:
            raise ValueError("TaskRequest does not contain memory_text.")

        return Event(
            object_type="MemoryProposal",
            context=task_event.context,
            created_by_cell=self.spec.cell_id,
            payload={
                "action": "memory_write",
                "memory_type": "fact",
                "content": {"text": memory_text},
                "human_summary": memory_text,
                "importance": 0.5,
                "confidence": 0.9,
                "source_event_id": task_event.event_id,
            },
        )
