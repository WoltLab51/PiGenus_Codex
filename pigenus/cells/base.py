from __future__ import annotations

from abc import ABC, abstractmethod

from pigenus.schemas.cells import CellSpec


class BaseCell(ABC):
    """Base interface for small, versioned PiGenus functional units."""

    @property
    @abstractmethod
    def spec(self) -> CellSpec:
        """Return the stable cell specification."""
