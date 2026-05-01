from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from pigenus.db.orm import Worker
from pigenus.db.session import get_session
from pigenus.models.schemas import (
    JobAckRequest,
    JobFailRequest,
    JobLeaseRequest,
    JobLeaseResponse,
    JobResponse,
    JobSubmitRequest,
)
from pigenus.security.auth import require_admin, require_worker
from pigenus.services.jobs import ack_job, fail_job, lease_jobs, submit_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


def to_job_response(job) -> JobResponse:
    return JobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        payload=job.payload,
        required_capabilities=job.required_capabilities,
        result=job.result,
        error=job.error,
        leased_by_worker_id=job.leased_by_worker_id,
        lease_expires_at=job.lease_expires_at,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def submit(
    payload: JobSubmitRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
) -> JobResponse:
    job = submit_job(
        session,
        job_type=payload.job_type,
        payload=payload.payload,
        required_capabilities=payload.required_capabilities,
        priority=payload.priority,
        max_attempts=payload.max_attempts,
        submitted_by="admin",
    )
    return to_job_response(job)


@router.post("/lease/{worker_id}", response_model=JobLeaseResponse)
def lease(
    worker_id: int,
    payload: JobLeaseRequest,
    request: Request,
    worker: Worker = Depends(require_worker),
    session: Session = Depends(get_session),
) -> JobLeaseResponse:
    if worker.id != worker_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="worker mismatch")
    jobs = lease_jobs(session, request.app.state.settings, worker=worker, max_jobs=payload.max_jobs)
    return JobLeaseResponse(jobs=[to_job_response(job) for job in jobs])


@router.post("/{job_id}/ack/{worker_id}", response_model=JobResponse)
def ack(
    job_id: int,
    worker_id: int,
    payload: JobAckRequest,
    worker: Worker = Depends(require_worker),
    session: Session = Depends(get_session),
) -> JobResponse:
    if worker.id != worker_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="worker mismatch")
    try:
        job = ack_job(session, worker=worker, job_id=job_id, result=payload.result)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return to_job_response(job)


@router.post("/{job_id}/fail/{worker_id}", response_model=JobResponse)
def fail(
    job_id: int,
    worker_id: int,
    payload: JobFailRequest,
    worker: Worker = Depends(require_worker),
    session: Session = Depends(get_session),
) -> JobResponse:
    if worker.id != worker_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="worker mismatch")
    try:
        job = fail_job(
            session,
            worker=worker,
            job_id=job_id,
            error=payload.error,
            retry=payload.retry,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return to_job_response(job)

