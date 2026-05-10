from __future__ import annotations

from dataclasses import dataclass

from pigenus.core.context_registry import ContextRegistry
from pigenus.core.permission_registry import PermissionRegistry
from pigenus.storage.repositories import (
    AuditRepository,
    CellRepository,
    DecisionRepository,
    EventRepository,
    MeaningRepository,
    MemoryRepository,
)


@dataclass(frozen=True)
class RuntimeOverview:
    """Read-only summary of the local PiGenus runtime."""

    event_count: int
    memory_count: int
    meaning_count: int
    cell_count: int
    audit_count: int
    decision_count: int
    contexts: tuple[str, ...]
    default_permissions: tuple[str, ...]


class RuntimeOverviewBuilder:
    """Builds a small operator overview from existing storage and registries."""

    def __init__(
        self,
        *,
        events: EventRepository,
        memory: MemoryRepository,
        meanings: MeaningRepository,
        cells: CellRepository,
        audit: AuditRepository,
        decisions: DecisionRepository,
        contexts: ContextRegistry | None = None,
        permissions: PermissionRegistry | None = None,
    ) -> None:
        self.events = events
        self.memory = memory
        self.meanings = meanings
        self.cells = cells
        self.audit = audit
        self.decisions = decisions
        self.contexts = contexts or ContextRegistry()
        self.permissions = permissions or PermissionRegistry()

    def build(self) -> RuntimeOverview:
        return RuntimeOverview(
            event_count=self.events.count(),
            memory_count=self.memory.count(),
            meaning_count=self.meanings.count(),
            cell_count=self.cells.count(),
            audit_count=self.audit.count(),
            decision_count=self.decisions.count(),
            contexts=tuple(context.name for context in self.contexts.list_contexts()),
            default_permissions=tuple(
                f"{rule.context}:{rule.action}" for rule in self.permissions.list_default_rules()
            ),
        )
