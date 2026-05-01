from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from pigenus.core.config import Settings
from pigenus.core.time import utcnow
from pigenus.db.orm import (
    EventActorType,
    Job,
    JobStatus,
    MemoryItem,
    Message,
    SessionRecord,
    Worker,
    WorkerStatus,
)
from pigenus.memory.store import remember
from pigenus.services.audit import audit
from pigenus.services.maintenance import create_sqlite_backup, mark_stale_workers_offline


SUPPORTED_MAINTENANCE_JOBS = {
    "maintenance.rotate_logs",
    "maintenance.summarize_sessions",
    "maintenance.compress_memory",
    "maintenance.daily_briefing",
    "maintenance.check_worker_availability",
    "maintenance.backup",
}


def run_maintenance_task(
    session: Session,
    settings: Settings,
    *,
    job_type: str,
    payload: dict,
) -> dict:
    if job_type == "maintenance.rotate_logs":
        return rotate_logs(session)
    if job_type == "maintenance.summarize_sessions":
        return summarize_sessions(session, limit=int(payload.get("limit", 50)))
    if job_type == "maintenance.compress_memory":
        return compress_memory(session)
    if job_type == "maintenance.daily_briefing":
        return prepare_daily_briefing(session)
    if job_type == "maintenance.check_worker_availability":
        return check_worker_availability(session, settings)
    if job_type == "maintenance.backup":
        return {"backup_path": create_sqlite_backup(settings)}
    raise ValueError(f"unsupported maintenance job type: {job_type}")


def rotate_logs(session: Session) -> dict:
    audit(
        session,
        action="maintenance.rotate_logs.checked",
        actor_type=EventActorType.system,
        details={"strategy": "systemd-journald-or-external-logrotate"},
    )
    session.commit()
    return {"status": "checked", "strategy": "systemd-journald-or-external-logrotate"}


def summarize_sessions(session: Session, *, limit: int = 50) -> dict:
    records = session.scalars(
        select(SessionRecord)
        .where(SessionRecord.status != "archived")
        .order_by(SessionRecord.updated_at.desc())
        .limit(limit)
    ).all()
    updated = 0
    for record in records:
        messages = session.scalars(
            select(Message).where(Message.session_id == record.id).order_by(Message.created_at.asc())
        ).all()
        if not messages:
            continue
        summary = _session_summary(messages)
        if record.summary == summary:
            continue
        record.summary = summary
        updated += 1
    if updated:
        audit(
            session,
            action="maintenance.sessions_summarized",
            actor_type=EventActorType.system,
            details={"updated": updated},
        )
    session.commit()
    return {"sessions_summarized": updated}


def compress_memory(session: Session) -> dict:
    duplicate_keys = session.execute(
        select(MemoryItem.namespace, MemoryItem.key, func.count(MemoryItem.id))
        .group_by(MemoryItem.namespace, MemoryItem.key)
        .having(func.count(MemoryItem.id) > 1)
    ).all()
    removed = 0
    compacted_groups = 0
    for namespace, key, _count in duplicate_keys:
        items = session.scalars(
            select(MemoryItem)
            .where(MemoryItem.namespace == namespace, MemoryItem.key == key)
            .order_by(MemoryItem.importance.desc(), MemoryItem.updated_at.desc(), MemoryItem.id.desc())
        ).all()
        keeper = items[0]
        duplicates = items[1:]
        duplicate_ids = [item.id for item in duplicates]
        if duplicate_ids:
            keeper.metadata_json = {
                **keeper.metadata_json,
                "compacted_duplicate_ids": duplicate_ids,
                "compacted_duplicate_count": len(duplicate_ids),
            }
            keeper.importance = max(item.importance for item in items)
            for item in duplicates:
                session.delete(item)
                removed += 1
            compacted_groups += 1
    if removed:
        audit(
            session,
            action="maintenance.memory_compressed",
            actor_type=EventActorType.system,
            details={"removed_duplicates": removed, "compacted_groups": compacted_groups},
        )
    session.commit()
    return {"removed_duplicates": removed, "compacted_groups": compacted_groups}


def prepare_daily_briefing(session: Session) -> dict:
    today_key = utcnow().date().isoformat()
    jobs_queued = (
        session.scalar(select(func.count()).select_from(Job).where(Job.status == JobStatus.queued))
        or 0
    )
    jobs_leased = (
        session.scalar(select(func.count()).select_from(Job).where(Job.status == JobStatus.leased))
        or 0
    )
    jobs_failed = (
        session.scalar(select(func.count()).select_from(Job).where(Job.status == JobStatus.failed))
        or 0
    )
    workers_online = (
        session.scalar(select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.online))
        or 0
    )
    open_sessions = (
        session.scalar(select(func.count()).select_from(SessionRecord).where(SessionRecord.status == "open"))
        or 0
    )
    briefing = (
        f"PiGenus daily briefing {today_key}: "
        f"{workers_online} workers online, {jobs_queued} queued jobs, "
        f"{jobs_leased} leased jobs, {jobs_failed} failed jobs, {open_sessions} open sessions."
    )
    existing = session.scalar(
        select(MemoryItem).where(MemoryItem.namespace == "briefing", MemoryItem.key == today_key)
    )
    if existing is None:
        remember(
            session,
            namespace="briefing",
            key=today_key,
            value=briefing,
            importance=70,
            metadata={"generated_by": "maintenance.daily_briefing"},
        )
    else:
        existing.value = briefing
        existing.metadata_json = {
            **existing.metadata_json,
            "generated_by": "maintenance.daily_briefing",
        }
        session.commit()
    return {"briefing_key": today_key, "briefing": briefing}


def check_worker_availability(session: Session, settings: Settings) -> dict:
    stale = mark_stale_workers_offline(session, settings)
    online = (
        session.scalar(select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.online))
        or 0
    )
    return {"stale_workers_marked_offline": stale, "workers_online": online}


def _session_summary(messages: list[Message]) -> str:
    first = _shorten(messages[0].content)
    last = _shorten(messages[-1].content)
    roles = sorted({message.role for message in messages})
    return f"{len(messages)} messages; roles={','.join(roles)}; first={first}; last={last}"


def _shorten(value: str, limit: int = 160) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
