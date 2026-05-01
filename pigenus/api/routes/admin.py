from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from pigenus.db.session import get_session
from pigenus.models.schemas import (
    AdminStatusResponse,
    AuditLogResponse,
    DeviceCreateRequest,
    DeviceResponse,
    MaintenanceRunResponse,
    UserCreateRequest,
    UserResponse,
)
from pigenus.monitoring.status import collect_admin_status
from pigenus.security.auth import require_admin
from pigenus.services.admin import (
    create_device,
    create_user,
    list_audit_events,
    list_devices,
    list_users,
)
from pigenus.services.maintenance import run_maintenance

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status", response_model=AdminStatusResponse)
def admin_status(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
) -> AdminStatusResponse:
    return collect_admin_status(session)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_user(
    payload: UserCreateRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    try:
        return create_user(
            session,
            username=payload.username,
            display_name=payload.display_name,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/users", response_model=list[UserResponse])
def get_users(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return list_users(session)


def to_device_response(device) -> DeviceResponse:
    return DeviceResponse(
        id=device.id,
        name=device.name,
        owner_user_id=device.owner_user_id,
        device_type=device.device_type,
        public_key=device.public_key,
        metadata=device.metadata_json,
        created_at=device.created_at,
    )


@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def add_device(
    payload: DeviceCreateRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    try:
        device = create_device(
            session,
            name=payload.name,
            owner_user_id=payload.owner_user_id,
            device_type=payload.device_type,
            public_key=payload.public_key,
            metadata=payload.metadata,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return to_device_response(device)


@router.get("/devices", response_model=list[DeviceResponse])
def get_devices(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return [to_device_response(device) for device in list_devices(session)]


def to_audit_response(event) -> AuditLogResponse:
    return AuditLogResponse(
        id=event.id,
        action=event.action,
        actor_type=event.actor_type,
        actor_id=event.actor_id,
        target_type=event.target_type,
        target_id=event.target_id,
        details=event.details,
        created_at=event.created_at,
    )


@router.get("/audit", response_model=list[AuditLogResponse])
def get_audit(
    limit: int = 100,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return [to_audit_response(event) for event in list_audit_events(session, limit=min(limit, 500))]


@router.post("/maintenance/run", response_model=MaintenanceRunResponse)
def run_maintenance_now(
    request: Request,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    result = run_maintenance(session, request.app.state.settings)
    return MaintenanceRunResponse(**result)
