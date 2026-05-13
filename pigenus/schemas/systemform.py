from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from pigenus.schemas.base import new_id, utc_now


class ActorType(str, Enum):
    HUMAN = "human"
    CELL = "cell"
    ORGAN = "organ"
    AGENT = "agent"
    CHARACTER = "character"
    SYSTEM = "system"


class ActorStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    FOSSIL = "fossil"


class TruthStatus(str, Enum):
    VERIFIED = "verified"
    BELIEVED = "believed"
    CONTESTED = "contested"
    DEPRECATED = "deprecated"
    SIMULATED = "simulated"
    UNSAFE = "unsafe"
    HISTORICAL = "historical"


class Sensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    FAMILY = "family"
    FINANCIAL = "financial"
    CHILD_RELATED = "child_related"
    SECRET = "secret"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DEPRECATED = "deprecated"


class GuardDecisionType(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"
    REVOKE = "revoke"
    ARCHIVE = "archive"


class RoomProtectionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    ISOLATED = "isolated"


class ContextFrameType(str, Enum):
    DOMAIN = "domain"
    GOVERNANCE = "governance"
    DATA = "data"
    EXECUTION = "execution"
    LEARNING = "learning"
    CAPABILITY = "capability"
    RESOURCE = "resource"
    TIME = "time"
    AUDIT = "audit"


class WorkerType(str, Enum):
    LOCAL_MACHINE = "local_machine"
    LOCAL_PROCESS = "local_process"
    RASPBERRY_PI = "raspberry_pi"
    SERVER = "server"
    GPU_MACHINE = "gpu_machine"
    EXTERNAL_PROVIDER = "external_provider"


class WorkerStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class ActorIdentity(BaseModel):
    """Stable identity for a human, cell, organ, agent, character, or system actor."""

    id: str = Field(min_length=1)
    actor_type: ActorType
    name: str = Field(min_length=1)
    version: str | None = None
    parent_id: str | None = None
    status: ActorStatus = ActorStatus.DRAFT
    public_key: str | None = None
    reputation_id: str | None = None
    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Room(BaseModel):
    """Governed execution and information boundary."""

    id: str = Field(default_factory=lambda: new_id("room"), min_length=1)
    name: str = Field(min_length=1)
    protection_level: RoomProtectionLevel
    default_policy_id: str | None = None
    description: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ContextFrame(BaseModel):
    """One formal condition around an action."""

    id: str = Field(default_factory=lambda: new_id("cf"), min_length=1)
    type: ContextFrameType
    name: str = Field(min_length=1)
    version: str = Field(default="1", min_length=1)
    description: str | None = None
    room_id: str | None = None
    policy_ref: str | None = None
    allowed_capabilities: list[str] = Field(default_factory=list)
    denied_capabilities: list[str] = Field(default_factory=list)
    allowed_sources: list[str] = Field(default_factory=list)
    denied_sources: list[str] = Field(default_factory=list)
    truth_requirement: TruthStatus | None = None
    sensitivity_level: Sensitivity | None = None
    risk_level: str | None = None
    execution_mode: str | None = None
    learning_mode: str | None = None
    audit_level: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def reject_internal_conflicts(self) -> ContextFrame:
        _reject_overlap(
            self.allowed_capabilities,
            self.denied_capabilities,
            "capabilities",
        )
        _reject_overlap(self.allowed_sources, self.denied_sources, "sources")
        return self


class ContextStack(BaseModel):
    """Concrete operating envelope assembled from context frames."""

    id: str = Field(default_factory=lambda: new_id("cstack"), min_length=1)
    name: str = Field(min_length=1)
    frame_ids: list[str] = Field(min_length=1)
    description: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("frame_ids")
    @classmethod
    def dedupe_frame_ids(cls, frame_ids: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for frame_id in frame_ids:
            if frame_id in seen:
                continue
            seen.add(frame_id)
            deduped.append(frame_id)
        return deduped


class WorkerProfile(BaseModel):
    """Model-only execution host profile for future Worker Runtime."""

    id: str = Field(default_factory=lambda: new_id("worker"), min_length=1)
    worker_type: WorkerType
    display_name: str = Field(min_length=1)
    status: WorkerStatus = WorkerStatus.DRAFT
    owner_actor_id: str | None = None
    home_room_id: str | None = None
    runtime_profile: dict[str, Any] = Field(default_factory=dict)
    hardware_profile: dict[str, Any] = Field(default_factory=dict)
    supported_runtimes: list[str] = Field(default_factory=list)
    available_cells: list[str] = Field(default_factory=list)
    available_tools: list[str] = Field(default_factory=list)
    capability_limits: dict[str, Any] = Field(default_factory=dict)
    cost_profile: dict[str, Any] = Field(default_factory=dict)
    privacy_profile: dict[str, Any] = Field(default_factory=dict)
    failure_semantics: dict[str, Any] = Field(default_factory=dict)
    max_sensitivity: Sensitivity = Sensitivity.INTERNAL
    network_access: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("supported_runtimes", "available_cells", "available_tools")
    @classmethod
    def dedupe_profile_lists(cls, values: list[str]) -> list[str]:
        return _dedupe_ordered(values)


class WorkerHeartbeat(BaseModel):
    """Model-only liveness signal for a known execution host."""

    id: str = Field(default_factory=lambda: new_id("whb"), min_length=1)
    worker_id: str = Field(min_length=1)
    status: WorkerStatus
    seen_at: datetime = Field(default_factory=utc_now)
    runtime_version: str | None = None
    health_summary: dict[str, Any] = Field(default_factory=dict)
    degraded_reasons: list[str] = Field(default_factory=list)

    @field_validator("degraded_reasons")
    @classmethod
    def dedupe_degraded_reasons(cls, values: list[str]) -> list[str]:
        return _dedupe_ordered(values)


class MeaningObject(BaseModel):
    """Primary semantic information object before durable memory."""

    id: str = Field(default_factory=lambda: new_id("bo"), min_length=1)
    type: str = Field(min_length=1)
    content: dict[str, Any]
    source: str | None = None
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    room_id: str = Field(min_length=1)
    truth_status: TruthStatus
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    sensitivity: Sensitivity
    revision: int = Field(default=1, ge=1)
    parent_ids: list[str] = Field(default_factory=list)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    created_by: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=utc_now)


def _reject_overlap(allowed: list[str], denied: list[str], label: str) -> None:
    overlap = set(allowed).intersection(denied)
    if overlap:
        values = ", ".join(sorted(overlap))
        raise ValueError(f"ContextFrame has conflicting {label}: {values}")


def _dedupe_ordered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


class CellContract(BaseModel):
    """Executable contract that defines what a cell actor may do."""

    id: str = Field(default_factory=lambda: new_id("contract"), min_length=1)
    actor_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    status: ContractStatus = ContractStatus.DRAFT
    room_scope: list[str] = Field(min_length=1)
    capabilities: list[str] = Field(default_factory=list)
    permissions: dict[str, Any] = Field(min_length=1)
    obligations: list[str] = Field(default_factory=list)
    resource_limits: dict[str, Any] = Field(default_factory=dict)
    risk_profile: dict[str, Any] = Field(default_factory=dict)
    human_approval_required: list[str] = Field(default_factory=list)
    mutation_policy: dict[str, Any] = Field(default_factory=dict)
    governance_policy_id: str = Field(min_length=1)
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ResourceGrant(BaseModel):
    """Explicit resource budget assigned to an actor in a room."""

    id: str = Field(default_factory=lambda: new_id("rg"), min_length=1)
    actor_id: str = Field(min_length=1)
    room_id: str = Field(min_length=1)
    limits: dict[str, Any] = Field(min_length=1)
    granted_by: str = Field(min_length=1)
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)


class GovernanceDecision(BaseModel):
    """Structured decision produced by governance or guard evaluation."""

    id: str = Field(default_factory=lambda: new_id("gdec"), min_length=1)
    decision: GuardDecisionType
    reason: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    room_id: str = Field(min_length=1)
    event_id: str | None = None
    rule_id: str | None = None
    requires_human: bool = False
    audit_required: bool = True
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
