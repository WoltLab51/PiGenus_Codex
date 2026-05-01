from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from pigenus.core.config import Settings
from pigenus.core.time import utcnow
from pigenus.db.orm import EventActorType, Job, JobStatus, Worker, WorkerStatus
from pigenus.services.audit import audit
from pigenus.services.jobs import requeue_stuck_jobs, submit_job


def create_sqlite_backup(settings: Settings) -> str | None:
    source = settings.sqlite_path
    if source is None or settings.database_url == "sqlite://" or not source.exists():
        return None
    backup_dir = Path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = utcnow().strftime("%Y%m%dT%H%M%SZ")
    target = backup_dir / f"pigenus-{stamp}.sqlite3"
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    return str(target)


def restore_sqlite_backup(settings: Settings, backup_path: str) -> None:
    target = settings.sqlite_path
    if target is None or settings.database_url == "sqlite://":
        raise ValueError("restore requires a file-backed SQLite database")
    source = Path(backup_path)
    if not source.exists():
        raise FileNotFoundError(backup_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def mark_stale_workers_offline(session: Session, settings: Settings) -> int:
    cutoff = utcnow().timestamp() - settings.worker_stale_seconds
    workers = session.scalars(select(Worker).where(Worker.status == WorkerStatus.online)).all()
    changed = 0
    for worker in workers:
        if worker.last_seen_at is None:
            continue
        if worker.last_seen_at.timestamp() < cutoff:
            worker.status = WorkerStatus.offline
            changed += 1
            audit(
                session,
                action="worker.marked_offline",
                actor_type=EventActorType.system,
                target_type="worker",
                target_id=str(worker.id),
                details={"reason": "stale heartbeat"},
            )
    session.commit()
    return changed


def create_nightly_maintenance_jobs(session: Session) -> int:
    job_specs = [
        ("maintenance.rotate_logs", {}),
        ("maintenance.backup", {}),
        ("maintenance.summarize_sessions", {}),
        ("maintenance.compress_memory", {}),
        ("maintenance.daily_briefing", {}),
        ("maintenance.check_worker_availability", {}),
    ]
    created = 0
    for job_type, payload in job_specs:
        existing = session.scalar(
            select(Job).where(Job.job_type == job_type, Job.status.in_([JobStatus.queued, JobStatus.leased]))
        )
        if existing is not None:
            continue
        submit_job(
            session,
            job_type=job_type,
            payload=payload,
            required_capabilities=["maintenance"],
            priority=900,
            max_attempts=3,
            submitted_by="system",
        )
        created += 1
    return created


def run_maintenance(session: Session, settings: Settings) -> dict[str, int | str | None]:
    requeued = requeue_stuck_jobs(session)
    stale = mark_stale_workers_offline(session, settings)
    backup_path = create_sqlite_backup(settings)
    maintenance_jobs = create_nightly_maintenance_jobs(session)
    audit(
        session,
        action="maintenance.completed",
        actor_type=EventActorType.system,
        details={
            "requeued_stuck_jobs": requeued,
            "stale_workers_marked_offline": stale,
            "backup_path": backup_path,
            "maintenance_jobs_created": maintenance_jobs,
        },
    )
    session.commit()
    return {
        "requeued_stuck_jobs": requeued,
        "stale_workers_marked_offline": stale,
        "backup_path": backup_path,
        "maintenance_jobs_created": maintenance_jobs,
    }
