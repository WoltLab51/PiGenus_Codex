from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pigenus.db.orm import EventActorType, JobStatus, WorkerStatus


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str


class WorkerRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    capabilities: list[str] = Field(default_factory=list, max_length=32)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerRegisterResponse(BaseModel):
    worker_id: int
    name: str
    token: str
    status: WorkerStatus


class WorkerHeartbeatRequest(BaseModel):
    status: WorkerStatus = WorkerStatus.online
    capabilities: list[str] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    capabilities: list[str]
    status: WorkerStatus
    last_seen_at: datetime | None


class JobSubmitRequest(BaseModel):
    job_type: str = Field(min_length=2, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)
    required_capabilities: list[str] = Field(default_factory=list, max_length=32)
    priority: int = Field(default=100, ge=0, le=1000)
    max_attempts: int = Field(default=3, ge=1, le=10)


class JobResponse(BaseModel):
    id: int
    job_type: str
    status: JobStatus
    priority: int
    payload: dict[str, Any]
    required_capabilities: list[str]
    result: dict[str, Any] | None
    error: str | None
    leased_by_worker_id: int | None
    lease_expires_at: datetime | None
    attempts: int
    max_attempts: int
    created_at: datetime
    updated_at: datetime


class JobLeaseRequest(BaseModel):
    max_jobs: int = Field(default=1, ge=1, le=10)


class JobLeaseResponse(BaseModel):
    jobs: list[JobResponse]


class JobAckRequest(BaseModel):
    result: dict[str, Any] = Field(default_factory=dict)


class JobFailRequest(BaseModel):
    error: str = Field(min_length=1, max_length=4000)
    retry: bool = True


class AdminStatusResponse(BaseModel):
    workers_total: int
    workers_online: int
    jobs_queued: int
    jobs_leased: int
    jobs_succeeded: int
    jobs_failed: int
    audit_events: int


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=2, max_length=120)
    display_name: str | None = Field(default=None, max_length=200)
    role: str = Field(default="user", min_length=2, max_length=40)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str | None
    role: str
    created_at: datetime


class DeviceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    owner_user_id: int | None = None
    device_type: str = Field(default="client", min_length=2, max_length=80)
    public_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeviceResponse(BaseModel):
    id: int
    name: str
    owner_user_id: int | None
    device_type: str
    public_key: str | None
    metadata: dict[str, Any]
    created_at: datetime


class SessionCreateRequest(BaseModel):
    user_id: int | None = None
    device_id: int | None = None
    title: str | None = Field(default=None, max_length=240)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=240)
    status: str | None = Field(default=None, max_length=40)
    summary: str | None = None


class SessionResponse(BaseModel):
    id: int
    user_id: int | None
    device_id: int | None
    title: str | None
    status: str
    summary: str | None
    created_at: datetime
    updated_at: datetime


class MessageCreateRequest(BaseModel):
    role: str = Field(min_length=2, max_length=40)
    content: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime


class SessionDetailResponse(SessionResponse):
    messages: list[MessageResponse]


class MemoryCreateRequest(BaseModel):
    namespace: str = Field(min_length=2, max_length=120)
    key: str = Field(min_length=1, max_length=240)
    value: str = Field(min_length=1)
    importance: int = Field(default=50, ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryUpdateRequest(BaseModel):
    value: str | None = Field(default=None, min_length=1)
    importance: int | None = Field(default=None, ge=0, le=100)
    metadata: dict[str, Any] | None = None


class MemoryResponse(BaseModel):
    id: int
    namespace: str
    key: str
    value: str
    importance: int
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AuditLogResponse(BaseModel):
    id: int
    action: str
    actor_type: EventActorType
    actor_id: str | None
    target_type: str | None
    target_id: str | None
    details: dict[str, Any]
    created_at: datetime


class MaintenanceRunResponse(BaseModel):
    requeued_stuck_jobs: int
    stale_workers_marked_offline: int
    backup_path: str | None
    maintenance_jobs_created: int
