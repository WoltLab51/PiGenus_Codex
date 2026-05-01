from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from pigenus.core.config import Settings
from pigenus.core.time import utcnow
from pigenus.db.orm import EventActorType, Worker, WorkerStatus
from pigenus.security.tokens import hash_token, new_token
from pigenus.services.audit import audit


def register_worker(
    session: Session,
    settings: Settings,
    *,
    name: str,
    capabilities: list[str],
    metadata: dict,
) -> tuple[Worker, str]:
    existing = session.scalar(select(Worker).where(Worker.name == name))
    if existing is not None:
        raise ValueError("worker name already exists")

    token = new_token()
    worker = Worker(
        name=name,
        token_hash=hash_token(token, settings.token_pepper),
        capabilities=sorted(set(capabilities)),
        metadata_json=metadata,
        status=WorkerStatus.registered,
    )
    session.add(worker)
    session.flush()
    audit(
        session,
        action="worker.registered",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="worker",
        target_id=str(worker.id),
        details={"name": name, "capabilities": worker.capabilities},
    )
    session.commit()
    session.refresh(worker)
    return worker, token


def heartbeat_worker(
    session: Session,
    *,
    worker: Worker,
    status: WorkerStatus,
    capabilities: list[str] | None,
    metadata: dict,
) -> Worker:
    worker.status = status
    worker.last_seen_at = utcnow()
    if capabilities is not None:
        worker.capabilities = sorted(set(capabilities))
    if metadata:
        worker.metadata_json = {**worker.metadata_json, **metadata}
    audit(
        session,
        action="worker.heartbeat",
        actor_type=EventActorType.worker,
        actor_id=str(worker.id),
        target_type="worker",
        target_id=str(worker.id),
        details={"status": status.value, "capabilities": worker.capabilities},
    )
    session.commit()
    session.refresh(worker)
    return worker

