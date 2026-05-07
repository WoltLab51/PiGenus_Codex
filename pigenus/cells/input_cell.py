from __future__ import annotations

from typing import Any

from pigenus.cells.base import BaseCell
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.events import Event


class InputCell(BaseCell):
    """Turns raw local user input into a structured TaskRequest event."""

    @property
    def spec(self) -> CellSpec:
        return CellSpec(
            name="input_cell",
            version="0.1.0",
            input_event_types=["UserInput"],
            output_event_types=["TaskRequest"],
            permissions=[],
            description="Parses raw user text into a task request.",
        )

    def create_task_request(self, text: str, context: dict[str, Any]) -> Event:
        memory_text = self._extract_memory_text(text)
        action = "memory_write" if memory_text else "unknown_critical_action"
        return Event(
            object_type="TaskRequest",
            context=context,
            created_by_cell=self.spec.cell_id,
            payload={
                "raw_text": text,
                "action": action,
                "memory_text": memory_text,
            },
        )

    @staticmethod
    def _extract_memory_text(text: str) -> str:
        prefix = "Merke dir:"
        if text.strip().startswith(prefix):
            return text.split(prefix, 1)[1].strip()
        return ""
