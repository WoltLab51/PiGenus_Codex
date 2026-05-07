from __future__ import annotations

from typing import Any

from pigenus.storage.repositories import AuditRepository


class AuditLogger:
    """Append-only audit logger for local runtime decisions and writes."""

    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def log(
        self,
        *,
        actor: str,
        action: str,
        context: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        return self.repository.add(
            actor=actor,
            action=action,
            context=context or {},
            details=details or {},
        )

    def count(self) -> int:
        return self.repository.count()
