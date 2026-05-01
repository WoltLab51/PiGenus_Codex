from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pigenus.db.session import get_session
from pigenus.memory.store import list_memory, remember, update_memory
from pigenus.models.schemas import MemoryCreateRequest, MemoryResponse, MemoryUpdateRequest
from pigenus.security.auth import require_admin

router = APIRouter(prefix="/memory", tags=["memory"])


def to_memory_response(item) -> MemoryResponse:
    return MemoryResponse(
        id=item.id,
        namespace=item.namespace,
        key=item.key,
        value=item.value,
        importance=item.importance,
        metadata=item.metadata_json,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    payload: MemoryCreateRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    item = remember(
        session,
        namespace=payload.namespace,
        key=payload.key,
        value=payload.value,
        importance=payload.importance,
        metadata=payload.metadata,
    )
    return to_memory_response(item)


@router.get("", response_model=list[MemoryResponse])
def get_memory(
    namespace: str | None = None,
    query: str | None = None,
    limit: int = 100,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return [
        to_memory_response(item)
        for item in list_memory(session, namespace=namespace, query=query, limit=min(limit, 500))
    ]


@router.patch("/{item_id}", response_model=MemoryResponse)
def patch_memory(
    item_id: int,
    payload: MemoryUpdateRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    try:
        item = update_memory(
            session,
            item_id=item_id,
            value=payload.value,
            importance=payload.importance,
            metadata=payload.metadata,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return to_memory_response(item)
