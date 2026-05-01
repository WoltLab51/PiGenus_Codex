from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from pigenus.core.config import Settings
from pigenus.core.time import utcnow
from pigenus.db.orm import EventActorType, Job, JobEvent, JobStatus, Worker
from pigenus.services.audit import audit


def _job_event(
    session: Session,
    *,
    job: Job,
    event_type: str,
    actor_type: EventActorType,
    actor_id: str | None = None,
    details: dict | None = None,
) -> None:
    session.add(
        JobEvent(
            job_id=job.id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            details=details or {},
        )
    )


def _worker_can_run(worker: Worker, required: list[str]) -> bool:
    return set(required).issubset(set(worker.capabilities))


def submit_job(
    session: Session,
    *,
    job_type: str,
    payload: dict,
    required_capabilities: list[str],
    priority: int,
    max_attempts: int,
    submitted_by: str,
) -> Job:
    job = Job(
        job_type=job_type,
        payload=payload,
        required_capabilities=sorted(set(required_capabilities)),
        priority=priority,
        max_attempts=max_attempts,
        submitted_by=submitted_by,
        status=JobStatus.queued,
    )
    session.add(job)
    session.flush()
    _job_event(
        session,
        job=job,
        event_type="submitted",
        actor_type=EventActorType.client,
        actor_id=submitted_by,
        details={"job_type": job_type},
    )
    audit(
        session,
        action="job.submitted",
        actor_type=EventActorType.client,
        actor_id=submitted_by,
        target_type="job",
        target_id=str(job.id),
        details={"job_type": job_type, "required_capabilities": job.required_capabilities},
    )
    session.commit()
    session.refresh(job)
    return job


def lease_jobs(
    session: Session,
    settings: Settings,
    *,
    worker: Worker,
    max_jobs: int,
) -> list[Job]:
    now = utcnow()
    candidates = session.scalars(
        select(Job)
        .where(Job.status == JobStatus.queued)
        .order_by(Job.priority.asc(), Job.created_at.asc())
        .limit(50)
    ).all()
    leased: list[Job] = []
    for job in candidates:
        if len(leased) >= max_jobs:
            break
        if not _worker_can_run(worker, job.required_capabilities):
            continue
        job.status = JobStatus.leased
        job.leased_by_worker_id = worker.id
        job.lease_expires_at = now + timedelta(seconds=settings.worker_lease_seconds)
        job.attempts += 1
        _job_event(
            session,
            job=job,
            event_type="leased",
            actor_type=EventActorType.worker,
            actor_id=str(worker.id),
            details={"lease_expires_at": job.lease_expires_at.isoformat()},
        )
        leased.append(job)
    if leased:
        audit(
            session,
            action="job.leased",
            actor_type=EventActorType.worker,
            actor_id=str(worker.id),
            target_type="job_batch",
            target_id=",".join(str(job.id) for job in leased),
            details={"count": len(leased)},
        )
    session.commit()
    for job in leased:
        session.refresh(job)
    return leased


def ack_job(session: Session, *, worker: Worker, job_id: int, result: dict) -> Job:
    job = session.get(Job, job_id)
    if job is None:
        raise LookupError("job not found")
    if job.status != JobStatus.leased or job.leased_by_worker_id != worker.id:
        raise PermissionError("job is not leased by this worker")
    job.status = JobStatus.succeeded
    job.result = result
    job.error = None
    job.lease_expires_at = None
    _job_event(
        session,
        job=job,
        event_type="succeeded",
        actor_type=EventActorType.worker,
        actor_id=str(worker.id),
    )
    audit(
        session,
        action="job.succeeded",
        actor_type=EventActorType.worker,
        actor_id=str(worker.id),
        target_type="job",
        target_id=str(job.id),
    )
    session.commit()
    session.refresh(job)
    return job


def fail_job(session: Session, *, worker: Worker, job_id: int, error: str, retry: bool) -> Job:
    job = session.get(Job, job_id)
    if job is None:
        raise LookupError("job not found")
    if job.status != JobStatus.leased or job.leased_by_worker_id != worker.id:
        raise PermissionError("job is not leased by this worker")
    job.error = error
    job.lease_expires_at = None
    job.leased_by_worker_id = None
    if retry and job.attempts < job.max_attempts:
        job.status = JobStatus.queued
        event_type = "requeued"
    else:
        job.status = JobStatus.failed
        event_type = "failed"
    _job_event(
        session,
        job=job,
        event_type=event_type,
        actor_type=EventActorType.worker,
        actor_id=str(worker.id),
        details={"error": error, "retry": retry},
    )
    audit(
        session,
        action=f"job.{event_type}",
        actor_type=EventActorType.worker,
        actor_id=str(worker.id),
        target_type="job",
        target_id=str(job.id),
        details={"error": error},
    )
    session.commit()
    session.refresh(job)
    return job


def requeue_stuck_jobs(session: Session) -> int:
    now = utcnow()
    jobs = session.scalars(
        select(Job).where(Job.status == JobStatus.leased, Job.lease_expires_at < now)
    ).all()
    for job in jobs:
        job.status = JobStatus.queued if job.attempts < job.max_attempts else JobStatus.failed
        job.leased_by_worker_id = None
        job.lease_expires_at = None
        _job_event(
            session,
            job=job,
            event_type="lease_expired",
            actor_type=EventActorType.system,
            details={"new_status": job.status.value},
        )
    if jobs:
        audit(
            session,
            action="maintenance.requeue_stuck_jobs",
            actor_type=EventActorType.system,
            details={"count": len(jobs)},
        )
    session.commit()
    return len(jobs)

