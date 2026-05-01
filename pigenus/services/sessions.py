from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from pigenus.core.time import utcnow
from pigenus.db.orm import Device, EventActorType, Message, SessionRecord, User
from pigenus.services.audit import audit


def create_session_record(
    session: Session,
    *,
    user_id: int | None,
    device_id: int | None,
    title: str | None,
    metadata: dict,
) -> SessionRecord:
    if user_id is not None and session.get(User, user_id) is None:
        raise LookupError("user not found")
    if device_id is not None and session.get(Device, device_id) is None:
        raise LookupError("device not found")
    record = SessionRecord(user_id=user_id, device_id=device_id, title=title)
    session.add(record)
    session.flush()
    audit(
        session,
        action="session.created",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="session",
        target_id=str(record.id),
        details={"user_id": user_id, "device_id": device_id, "metadata": metadata},
    )
    session.commit()
    session.refresh(record)
    return record


def list_session_records(session: Session, *, limit: int = 100) -> list[SessionRecord]:
    return list(
        session.scalars(
            select(SessionRecord)
            .order_by(SessionRecord.updated_at.desc(), SessionRecord.id.desc())
            .limit(limit)
        ).all()
    )


def get_session_record(session: Session, session_id: int) -> SessionRecord:
    record = session.get(SessionRecord, session_id)
    if record is None:
        raise LookupError("session not found")
    return record


def update_session_record(
    session: Session,
    *,
    session_id: int,
    title: str | None,
    status: str | None,
    summary: str | None,
) -> SessionRecord:
    record = get_session_record(session, session_id)
    if title is not None:
        record.title = title
    if status is not None:
        record.status = status
    if summary is not None:
        record.summary = summary
    record.updated_at = utcnow()
    audit(
        session,
        action="session.updated",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="session",
        target_id=str(record.id),
        details={"status": record.status},
    )
    session.commit()
    session.refresh(record)
    return record


def add_message(
    session: Session,
    *,
    session_id: int,
    role: str,
    content: str,
    metadata: dict,
) -> Message:
    record = get_session_record(session, session_id)
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        metadata_json=metadata,
    )
    record.updated_at = utcnow()
    session.add(message)
    session.flush()
    audit(
        session,
        action="message.created",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="message",
        target_id=str(message.id),
        details={"session_id": session_id, "role": role},
    )
    session.commit()
    session.refresh(message)
    return message


def list_messages(session: Session, *, session_id: int) -> list[Message]:
    get_session_record(session, session_id)
    return list(
        session.scalars(
            select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
        ).all()
    )
