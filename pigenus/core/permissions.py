from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionDecision:
    """Decision returned by the local permission engine."""

    context: str
    action: str
    allowed: bool
    reason: str
    allowed_permissions: tuple[str, ...]
    denied_permissions: tuple[str, ...]


class PermissionEngine:
    """Small allow/deny engine for Phase 1 actions."""

    default_allowed = {"developer/default": {"memory_write"}}

    def check(
        self,
        *,
        context: str,
        action: str,
        allowed_permissions: set[str] | None = None,
        denied_permissions: set[str] | None = None,
    ) -> PermissionDecision:
        allowed_permissions = allowed_permissions or set()
        denied_permissions = denied_permissions or set()

        if action in denied_permissions:
            return self._decision(
                context,
                action,
                False,
                "explicitly_denied",
                allowed_permissions,
                denied_permissions,
            )

        if action in allowed_permissions:
            return self._decision(
                context,
                action,
                True,
                "explicitly_allowed",
                allowed_permissions,
                denied_permissions,
            )

        if action in self.default_allowed.get(context, set()):
            return self._decision(
                context,
                action,
                True,
                "default_context_allow",
                allowed_permissions,
                denied_permissions,
            )

        return self._decision(context, action, False, "action_not_allowed", allowed_permissions, denied_permissions)

    @staticmethod
    def _decision(
        context: str,
        action: str,
        allowed: bool,
        reason: str,
        allowed_permissions: set[str],
        denied_permissions: set[str],
    ) -> PermissionDecision:
        return PermissionDecision(
            context=context,
            action=action,
            allowed=allowed,
            reason=reason,
            allowed_permissions=tuple(sorted(allowed_permissions)),
            denied_permissions=tuple(sorted(denied_permissions)),
        )
