from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from pigenus.db.session import get_session
from pigenus.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(session: Session = Depends(get_session)) -> HealthResponse:
    session.execute(text("select 1"))
    return HealthResponse(status="ok", service="pigenus", database="ok")

