from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from pigenus.db.orm import Worker
from pigenus.db.session import get_session
from pigenus.security.tokens import verify_token

bearer = HTTPBearer(auto_error=False)


def _extract_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )
    return credentials.credentials


def require_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str:
    token = _extract_token(credentials)
    admin_token = request.app.state.settings.admin_token
    if not secrets.compare_digest(token, admin_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid admin token")
    return "admin"


def require_worker(
    worker_id: int,
    request: Request,
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Worker:
    token = _extract_token(credentials)
    worker = session.get(Worker, worker_id)
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="worker not found")
    if not verify_token(token, worker.token_hash, request.app.state.settings.token_pepper):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid worker token")
    return worker

