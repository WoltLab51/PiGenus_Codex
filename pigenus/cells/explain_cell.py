from __future__ import annotations

from pigenus.cells.base import BaseCell
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.events import Event
from pigenus.schemas.memory import MemoryObject


class ExplainCell(BaseCell):
    """Creates deterministic human-readable responses without an LLM."""

    @property
    def spec(self) -> CellSpec:
        return CellSpec(
            name="explain_cell",
            version="0.1.0",
            input_event_types=["MemoryStored"],
            output_event_types=["HumanResponse"],
            permissions=[],
            description="Formats local runtime results for humans.",
        )

    def explain(self, memory: MemoryObject) -> tuple[str, Event]:
        response = f"Gespeichert: {memory.human_summary}"
        event = Event(
            object_type="HumanResponse",
            context=memory.context,
            created_by_cell=self.spec.cell_id,
            payload={"response": response, "memory_id": memory.memory_id},
        )
        return response, event
