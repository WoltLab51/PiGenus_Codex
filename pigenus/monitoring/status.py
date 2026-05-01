from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from pigenus.db.orm import AuditLog, Job, JobStatus, Worker, WorkerStatus
from pigenus.models.schemas import AdminStatusResponse


def collect_admin_status(session: Session) -> AdminStatusResponse:
    def count_jobs(status: JobStatus) -> int:
        return session.scalar(select(func.count()).select_from(Job).where(Job.status == status)) or 0

    workers_total = session.scalar(select(func.count()).select_from(Worker)) or 0
    workers_online = (
        session.scalar(select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.online))
        or 0
    )
    audit_events = session.scalar(select(func.count()).select_from(AuditLog)) or 0
    return AdminStatusResponse(
        workers_total=workers_total,
        workers_online=workers_online,
        jobs_queued=count_jobs(JobStatus.queued),
        jobs_leased=count_jobs(JobStatus.leased),
        jobs_succeeded=count_jobs(JobStatus.succeeded),
        jobs_failed=count_jobs(JobStatus.failed),
        audit_events=audit_events,
    )

