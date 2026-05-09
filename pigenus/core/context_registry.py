from __future__ import annotations

from dataclasses import dataclass

from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import KNOWN_CONTEXTS


@dataclass(frozen=True)
class ContextInspection:
    """Inspectable context boundary metadata."""

    name: str
    allowed_cell_ids: tuple[str, ...] = ()


class ContextRegistry:
    """Read-only registry for known execution contexts."""

    def list_contexts(self, cells: list[CellSpec] | None = None) -> list[ContextInspection]:
        known_contexts = sorted(KNOWN_CONTEXTS)
        cells = cells or []
        inspections: list[ContextInspection] = []

        for context_name in known_contexts:
            allowed = tuple(
                sorted(
                    cell.cell_id
                    for cell in cells
                    if "*" in cell.allowed_contexts or context_name in cell.allowed_contexts
                )
            )
            inspections.append(ContextInspection(name=context_name, allowed_cell_ids=allowed))

        return inspections
