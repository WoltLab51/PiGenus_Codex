from __future__ import annotations

from pigenus.schemas.cells import CellSpec
from pigenus.storage.repositories import CellRepository


class CellRegistry:
    """Registers versioned cells for lookup and persistence."""

    def __init__(self, repository: CellRepository) -> None:
        self.repository = repository
        self._cells: dict[str, CellSpec] = {}

    def register(self, spec: CellSpec) -> CellSpec:
        self._cells[spec.cell_id] = spec
        self.repository.add(spec)
        return spec

    def get(self, cell_id: str) -> CellSpec | None:
        if cell_id in self._cells:
            return self._cells[cell_id]
        spec = self.repository.get(cell_id)
        if spec is not None:
            self._cells[cell_id] = spec
        return spec

    def list(self) -> list[CellSpec]:
        return list(self._cells.values())
