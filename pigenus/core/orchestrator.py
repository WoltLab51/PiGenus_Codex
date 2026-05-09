from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pigenus.cells.explain_cell import ExplainCell
from pigenus.cells.input_cell import InputCell
from pigenus.cells.memory_proposer import MemoryProposerCell
from pigenus.cells.memory_writer import MemoryWriterCell
from pigenus.cells.rule_guard import RuleGuardCell
from pigenus.core.audit import AuditLogger
from pigenus.core.context_boundary import ContextBoundaryEngine
from pigenus.core.event_bus import EventBus
from pigenus.core.permissions import PermissionEngine
from pigenus.core.registry import CellRegistry
from pigenus.schemas.context import Context
from pigenus.schemas.cells import CellSpec
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    CellRepository,
    EventRepository,
    MemoryRepository,
)

DEMO_TEXT = "Merke dir: PiGenus ist der Zellkern."
DEFAULT_CONTEXT = Context().as_event_context()


@dataclass(frozen=True)
class DemoResult:
    """Result returned by the deterministic Phase 1 demo flow."""

    final_response: str
    memory_id: str
    events_stored: int


class SimpleOrchestrator:
    """Runs a small local cell pipeline without external services."""

    def __init__(self, db_path: str | Path = "pigenus.sqlite3") -> None:
        self.database = Database(db_path)
        self.database.initialize()

        self.events = EventRepository(self.database)
        self.memory = MemoryRepository(self.database)
        self.cells = CellRepository(self.database)
        self.audit = AuditRepository(self.database)

        self.event_bus = EventBus(self.events)
        self.audit_logger = AuditLogger(self.audit)
        self.registry = CellRegistry(self.cells)
        self.permission_engine = PermissionEngine()
        self.context_boundary = ContextBoundaryEngine()

        self.input_cell = InputCell()
        self.rule_guard = RuleGuardCell(self.permission_engine, self.audit_logger)
        self.memory_proposer = MemoryProposerCell()
        self.memory_writer = MemoryWriterCell(self.memory, self.audit_logger)
        self.explain_cell = ExplainCell()

        for cell in (
            self.input_cell,
            self.rule_guard,
            self.memory_proposer,
            self.memory_writer,
            self.explain_cell,
        ):
            self.registry.register(cell.spec)

    def _mark_cell_used(self, spec: CellSpec) -> None:
        self.registry.mark_used(spec.cell_id)

    def run_demo(self, text: str = DEMO_TEXT, context: dict[str, Any] | None = None) -> DemoResult:
        starting_event_count = self.event_bus.count()
        event_context = Context.model_validate(context or DEFAULT_CONTEXT).as_event_context()

        self.context_boundary.require_allowed(cell=self.input_cell.spec, context=event_context)
        task_event = self.input_cell.create_task_request(text, event_context)
        self._mark_cell_used(self.input_cell.spec)
        self.event_bus.publish(task_event)

        self.context_boundary.require_allowed(cell=self.memory_proposer.spec, context=task_event.context)
        proposal_event = self.memory_proposer.propose(task_event)
        self._mark_cell_used(self.memory_proposer.spec)
        self.event_bus.publish(proposal_event)

        self.context_boundary.require_allowed(cell=self.rule_guard.spec, context=proposal_event.context)
        guard_event = self.rule_guard.check(proposal_event)
        self._mark_cell_used(self.rule_guard.spec)
        self.event_bus.publish(guard_event)

        self.context_boundary.require_allowed(cell=self.memory_writer.spec, context=proposal_event.context)
        memory, stored_event = self.memory_writer.write(proposal_event, guard_event)
        self._mark_cell_used(self.memory_writer.spec)
        self.event_bus.publish(stored_event)

        self.context_boundary.require_allowed(cell=self.explain_cell.spec, context=memory.context)
        final_response, response_event = self.explain_cell.explain(memory)
        self._mark_cell_used(self.explain_cell.spec)
        self.event_bus.publish(response_event)

        return DemoResult(
            final_response=final_response,
            memory_id=memory.memory_id,
            events_stored=self.event_bus.count() - starting_event_count,
        )

    def close(self) -> None:
        self.database.close()
