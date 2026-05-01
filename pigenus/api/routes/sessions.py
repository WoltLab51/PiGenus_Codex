from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pigenus.db.session import get_session
from pigenus.models.schemas import (
    MessageCreateRequest,
    MessageResponse,
    SessionCreateRequest,
    SessionDetailResponse,
    SessionResponse,
    SessionUpdateRequest,
)
from pigenus.security.auth import require_admin
from pigenus.services.sessions import (
    add_message,
    create_session_record,
    get_session_record,
    list_messages,
    list_session_records,
    update_session_record,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def to_session_response(record) -> SessionResponse:
    return SessionResponse(
        id=record.id,
        user_id=record.user_id,
        device_id=record.device_id,
        title=record.title,
        status=record.status,
        summary=record.summary,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def to_message_response(message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        metadata=message.metadata_json,
        created_at=message.created_at,
    )


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreateRequest,
    _: str = Depends(require_admin),
    db: Session = Depends(get_session),
):
    try:
        record = create_session_record(
            db,
            user_id=payload.user_id,
            device_id=payload.device_id,
            title=payload.title,
            metadata=payload.metadata,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return to_session_response(record)


@router.get("", response_model=list[SessionResponse])
def list_sessions(
    limit: int = 100,
    _: str = Depends(require_admin),
    db: Session = Depends(get_session),
):
    return [to_session_response(record) for record in list_session_records(db, limit=min(limit, 500))]


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(
    session_id: int,
    _: str = Depends(require_admin),
    db: Session = Depends(get_session),
):
    try:
        record = get_session_record(db, session_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    messages = list_messages(db, session_id=session_id)
    return SessionDetailResponse(
        **to_session_response(record).model_dump(),
        messages=[to_message_response(message) for message in messages],
    )


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    payload: SessionUpdateRequest,
    _: str = Depends(require_admin),
    db: Session = Depends(get_session),
):
    try:
        record = update_session_record(
            db,
            session_id=session_id,
            title=payload.title,
            status=payload.status,
            summary=payload.summary,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return to_session_response(record)


@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    session_id: int,
    payload: MessageCreateRequest,
    _: str = Depends(require_admin),
    db: Session = Depends(get_session),
):
    try:
        message = add_message(
            db,
            session_id=session_id,
            role=payload.role,
            content=payload.content,
            metadata=payload.metadata,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return to_message_response(message)
