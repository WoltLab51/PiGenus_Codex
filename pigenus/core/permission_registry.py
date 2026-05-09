from __future__ import annotations

from dataclasses import dataclass

from pigenus.core.permissions import PermissionEngine


@dataclass(frozen=True)
class PermissionRule:
    """Inspectable permission rule metadata."""

    context: str
    action: str
    source: str


class PermissionRegistry:
    """Read-only registry for built-in permission defaults."""

    def __init__(self, engine: PermissionEngine | None = None) -> None:
        self.engine = engine or PermissionEngine()

    def list_default_rules(self) -> list[PermissionRule]:
        rules: list[PermissionRule] = []
        for context, actions in sorted(self.engine.default_allowed.items()):
            for action in sorted(actions):
                rules.append(PermissionRule(context=context, action=action, source="default"))
        return rules
