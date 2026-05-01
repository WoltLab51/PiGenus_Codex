from __future__ import annotations

from sqlalchemy.orm import Session

from pigenus.db.orm import AuditLog, EventActorType


def audit(
    session: Session,
    *,
    action: str,
    actor_type: EventActorType,
    actor_id: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    details: dict | None = None,
) -> AuditLog:
    event = AuditLog(
        action=action,
        actor_type=actor_type,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        details=details or {},
    )
    session.add(event)
    return event

