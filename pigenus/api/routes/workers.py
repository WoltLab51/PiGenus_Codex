from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from pigenus.db.orm import Worker
from pigenus.db.session import get_session
from pigenus.models.schemas import (
    WorkerHeartbeatRequest,
    WorkerRegisterRequest,
    WorkerRegisterResponse,
    WorkerResponse,
)
from pigenus.security.auth import require_admin, require_worker
from pigenus.services.workers import heartbeat_worker, register_worker

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/register", response_model=WorkerRegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: WorkerRegisterRequest,
    request: Request,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
) -> WorkerRegisterResponse:
    try:
        worker, token = register_worker(
            session,
            request.app.state.settings,
            name=payload.name,
            capabilities=payload.capabilities,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return WorkerRegisterResponse(
        worker_id=worker.id,
        name=worker.name,
        token=token,
        status=worker.status,
    )


@router.post("/{worker_id}/heartbeat", response_model=WorkerResponse)
def heartbeat(
    payload: WorkerHeartbeatRequest,
    worker: Worker = Depends(require_worker),
    session: Session = Depends(get_session),
) -> Worker:
    return heartbeat_worker(
        session,
        worker=worker,
        status=payload.status,
        capabilities=payload.capabilities,
        metadata=payload.metadata,
    )

