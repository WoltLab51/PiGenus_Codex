from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pigenus.db.orm import AuditLog, Device, EventActorType, User
from pigenus.services.audit import audit


def create_user(
    session: Session,
    *,
    username: str,
    display_name: str | None,
    role: str,
) -> User:
    user = User(username=username, display_name=display_name, role=role)
    session.add(user)
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        raise ValueError("username already exists") from exc
    audit(
        session,
        action="user.created",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="user",
        target_id=str(user.id),
        details={"username": username, "role": role},
    )
    session.commit()
    session.refresh(user)
    return user


def list_users(session: Session) -> list[User]:
    return list(session.scalars(select(User).order_by(User.created_at.desc(), User.id.desc())).all())


def create_device(
    session: Session,
    *,
    name: str,
    owner_user_id: int | None,
    device_type: str,
    public_key: str | None,
    metadata: dict,
) -> Device:
    if owner_user_id is not None and session.get(User, owner_user_id) is None:
        raise LookupError("owner user not found")
    device = Device(
        name=name,
        owner_user_id=owner_user_id,
        device_type=device_type,
        public_key=public_key,
        metadata_json=metadata,
    )
    session.add(device)
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        raise ValueError("device name already exists") from exc
    audit(
        session,
        action="device.created",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="device",
        target_id=str(device.id),
        details={"name": name, "device_type": device_type, "owner_user_id": owner_user_id},
    )
    session.commit()
    session.refresh(device)
    return device


def list_devices(session: Session) -> list[Device]:
    return list(session.scalars(select(Device).order_by(Device.created_at.desc(), Device.id.desc())).all())


def list_audit_events(session: Session, *, limit: int = 100) -> list[AuditLog]:
    return list(
        session.scalars(
            select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit)
        ).all()
    )
