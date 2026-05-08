from __future__ import annotations

from pigenus.cells.base import BaseCell
from pigenus.core.audit import AuditLogger
from pigenus.core.permissions import PermissionEngine
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.events import Event


class RuleGuardCell(BaseCell):
    """Checks local permissions and emits a structured guard decision."""

    def __init__(self, permission_engine: PermissionEngine, audit_logger: AuditLogger) -> None:
        self.permission_engine = permission_engine
        self.audit_logger = audit_logger

    @property
    def spec(self) -> CellSpec:
        return CellSpec(
            name="rule_guard",
            version="0.1.0",
            input_event_types=["TaskRequest", "MemoryProposal"],
            output_event_types=["GuardDecision"],
            permissions=[],
            description="Checks requested actions against local permissions.",
        )

    def check(self, task_event: Event) -> Event:
        action = str(task_event.payload.get("action") or "")
        context_name = str(task_event.context.get("name") or "developer/default")
        decision = self.permission_engine.check(context=context_name, action=action)
        self.audit_logger.log(
            actor=self.spec.cell_id,
            action="permission_check",
            context=task_event.context,
            details={
                "requested_action": action,
                "allowed": decision.allowed,
                "reason": decision.reason,
                "blocking_cell": self.spec.cell_id if not decision.allowed else "",
                "source_event_id": task_event.event_id,
            },
        )
        return Event(
            object_type="GuardDecision",
            context=task_event.context,
            created_by_cell=self.spec.cell_id,
            payload={
                "action": action,
                "allowed": decision.allowed,
                "reason": decision.reason,
                "blocking_cell": self.spec.cell_id if not decision.allowed else "",
                "source_event_id": task_event.event_id,
                "allowed_permissions": list(decision.allowed_permissions),
                "denied_permissions": list(decision.denied_permissions),
            },
        )
