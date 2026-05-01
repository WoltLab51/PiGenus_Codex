from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pigenus.db.orm import JobStatus, WorkerStatus


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

