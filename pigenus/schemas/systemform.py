from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

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
