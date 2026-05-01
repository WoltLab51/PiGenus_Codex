from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pigenus.core.time import utcnow
from pigenus.db.session import Base


class WorkerStatus(str, enum.Enum):
    registered = "registered"
    online = "online"
    offline = "offline"
    disabled = "disabled"


class JobStatus(str, enum.Enum):
    queued = "queued"
    leased = "leased"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"


class EventActorType(str, enum.Enum):
    system = "system"
    admin = "admin"
    worker = "worker"
    client = "client"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    role: Mapped[str] = mapped_column(String(40), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    device_type: Mapped[str] = mapped_column(String(80), default="client")
    public_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="open")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    messages: Mapped[list["Message"]] = relationship(back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session: Mapped[SessionRecord] = relationship(back_populates="messages")


class Worker(Base):
    __tablename__ = "workers"
    __table_args__ = (UniqueConstraint("name", name="uq_workers_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    token_hash: Mapped[str] = mapped_column(String(160))
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[WorkerStatus] = mapped_column(Enum(WorkerStatus), default=WorkerStatus.registered)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_type: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    required_capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    leased_by_worker_id: Mapped[int | None] = mapped_column(ForeignKey("workers.id"), nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    events: Mapped[list["JobEvent"]] = relationship(back_populates="job")


class JobEvent(Base):
    __tablename__ = "job_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    actor_type: Mapped[EventActorType] = mapped_column(Enum(EventActorType), default=EventActorType.system)
    actor_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    job: Mapped[Job] = relationship(back_populates="events")


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace: Mapped[str] = mapped_column(String(120), index=True)
    key: Mapped[str] = mapped_column(String(240), index=True)
    value: Mapped[str] = mapped_column(Text)
    importance: Mapped[int] = mapped_column(Integer, default=50)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    actor_type: Mapped[EventActorType] = mapped_column(Enum(EventActorType), default=EventActorType.system)
    actor_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

