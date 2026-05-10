from __future__ import annotations

import re
from typing import Any

from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import Context
from pigenus.schemas.memory import MemoryObject, MemoryStatus
from pigenus.schemas.systemform import (
    CellContract,
    ContractStatus,
    MeaningObject,
    Room,
    RoomProtectionLevel,
    Sensitivity,
    TruthStatus,
)


CONTEXT_TO_ROOM_ID: dict[str, str] = {
    "developer/default": "room_developer",
    "private/default": "room_private",
    "family/default": "room_family",
    "trading/default": "room_trading",
}

CONTEXT_TO_PROTECTION_LEVEL: dict[str, RoomProtectionLevel] = {
    "developer/default": RoomProtectionLevel.MEDIUM,
    "private/default": RoomProtectionLevel.HIGH,
    "family/default": RoomProtectionLevel.HIGH,
    "trading/default": RoomProtectionLevel.VERY_HIGH,
}

CONTEXT_TO_SENSITIVITY: dict[str, Sensitivity] = {
    "developer/default": Sensitivity.INTERNAL,
    "private/default": Sensitivity.PRIVATE,
    "family/default": Sensitivity.FAMILY,
    "trading/default": Sensitivity.FINANCIAL,
}

MEMORY_STATUS_TO_TRUTH_STATUS: dict[MemoryStatus, TruthStatus] = {
    "fresh": TruthStatus.BELIEVED,
    "active": TruthStatus.BELIEVED,
    "watch": TruthStatus.BELIEVED,
    "stale": TruthStatus.DEPRECATED,
    "dormant": TruthStatus.DEPRECATED,
    "dead": TruthStatus.DEPRECATED,
    "fossil": TruthStatus.HISTORICAL,
    "canonical": TruthStatus.VERIFIED,
}


def context_to_room(context: Context | dict[str, Any]) -> Room:
    """Map the current lightweight context contract to an explicit Systemform room."""

    validated = Context.model_validate(context)
    room_id = CONTEXT_TO_ROOM_ID[validated.name]
    return Room(
        id=room_id,
        name=validated.name,
        protection_level=CONTEXT_TO_PROTECTION_LEVEL[validated.name],
        default_policy_id=f"policy_{_slug(validated.name)}",
        description=f"Systemform room adapter for {validated.name}.",
    )


def memory_to_meaning_object(
    memory: MemoryObject,
    *,
    created_by: str = "systemform_adapter",
) -> MeaningObject:
    """Map durable prototype memory to a primary Systemform meaning object."""

    context = Context.model_validate(memory.context)
    return MeaningObject(
        id=f"bo_from_{memory.memory_id}",
        type=memory.memory_type,
        content=dict(memory.content),
        source=f"memory:{memory.memory_id}",
        provenance=[
            {
                "adapter": "memory_to_meaning_object",
                "source_model": "MemoryObject",
                "source_id": memory.memory_id,
            }
        ],
        room_id=CONTEXT_TO_ROOM_ID[context.name],
        truth_status=MEMORY_STATUS_TO_TRUTH_STATUS[memory.status],
        confidence=memory.confidence,
        sensitivity=CONTEXT_TO_SENSITIVITY[context.name],
        valid_from=memory.created_at,
        valid_until=memory.expires_at,
        created_by=created_by,
        created_at=memory.created_at,
    )


def cell_spec_to_contract(
    spec: CellSpec,
    *,
    governance_policy_id: str = "policy_runtime_default",
) -> CellContract:
    """Map the current executable cell spec to an explicit Systemform cell contract."""

    room_scope = [_context_name_to_room_id(context) for context in spec.allowed_contexts]
    permissions = {permission: True for permission in spec.permissions}
    if not permissions:
        permissions = {"execute": True}

    return CellContract(
        id=f"contract_{_slug(spec.cell_id)}",
        actor_id=cell_spec_actor_id(spec),
        version=spec.version,
        status=ContractStatus.ACTIVE if spec.status == "active" else ContractStatus.DRAFT,
        room_scope=room_scope,
        capabilities=[
            *(f"consume.{event_type}" for event_type in spec.input_event_types),
            *(f"emit.{event_type}" for event_type in spec.output_event_types),
        ],
        permissions=permissions,
        obligations=["respect_context_boundary"],
        resource_limits={},
        risk_profile={"runtime_status": spec.status, "fitness": spec.fitness},
        governance_policy_id=governance_policy_id,
        created_at=spec.created_at,
    )


def cell_spec_actor_id(spec: CellSpec) -> str:
    """Return the stable Systemform actor ID derived from a prototype cell spec."""

    return f"cell_{_slug(spec.cell_id)}"


def _context_name_to_room_id(context_name: str) -> str:
    if context_name == "*":
        return "*"
    return CONTEXT_TO_ROOM_ID.get(context_name, f"room_{_slug(context_name)}")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or "unknown"
