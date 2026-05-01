from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from pigenus.db.session import get_session
from pigenus.models.schemas import AdminStatusResponse
from pigenus.monitoring.status import collect_admin_status
from pigenus.security.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status", response_model=AdminStatusResponse)
def admin_status(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
) -> AdminStatusResponse:
    return collect_admin_status(session)

