from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from pigenus.schemas.base import utc_now
from pigenus.schemas.systemform import (
    ActorIdentity,
    ActorStatus,
    CellContract,
    ContractStatus,
    GovernanceDecision,
    GuardDecisionType,
    ResourceGrant,
    Room,
)


class ContractValidationResult(BaseModel):
    """Result returned by the storage-free Systemform contract validator."""

    allowed: bool
    decision: GuardDecisionType
    reason: str
    requires_human: bool = False


class ContractValidator:
    """Validates whether a Systemform actor may perform an action in a room."""

    def validate(
        self,
        *,
        actor: ActorIdentity | None,
        room: Room | None,
        contract: CellContract | None,
        action: str,
        capability: str | None = None,
        resource_request: dict[str, int | float] | None = None,
        resource_grant: ResourceGrant | None = None,
        now: datetime | None = None,
    ) -> ContractValidationResult:
        now = now or utc_now()
        resource_request = resource_request or {}

        if actor is None:
            return self._block("actor_missing")
        if actor.status == ActorStatus.REVOKED:
            return self._block("actor_revoked")
        if actor.status == ActorStatus.SUSPENDED:
            return self._block("actor_suspended")
        if actor.status != ActorStatus.ACTIVE:
            return self._block("actor_not_active")

        if room is None:
            return self._block("room_missing")

        if contract is None:
            return self._block("contract_missing")
        if contract.status == ContractStatus.REVOKED:
            return self._block("contract_revoked")
        if contract.status == ContractStatus.EXPIRED:
            return self._block("contract_expired")
        if contract.status != ContractStatus.ACTIVE:
            return self._block("contract_not_active")
        if contract.expires_at is not None and contract.expires_at <= now:
            return self._block("contract_expired")
        if contract.actor_id != actor.id:
            return self._block("actor_contract_mismatch")
        if room.id not in contract.room_scope and "*" not in contract.room_scope:
            return self._block("room_not_allowed")

        if capability is not None and capability not in contract.capabilities:
            return self._block("capability_not_allowed")
        if not self._permission_allowed(contract.permissions, action):
            return self._block("permission_not_allowed")

        resource_result = self._validate_resources(
            actor=actor,
            room=room,
            contract=contract,
            resource_request=resource_request,
            resource_grant=resource_grant,
            now=now,
        )
        if resource_result is not None:
            return resource_result

        if action in contract.human_approval_required:
            return ContractValidationResult(
                allowed=False,
                decision=GuardDecisionType.ESCALATE,
                reason="human_approval_required",
                requires_human=True,
            )

        return ContractValidationResult(
            allowed=True,
            decision=GuardDecisionType.ALLOW,
            reason="allowed",
        )

    def to_governance_decision(
        self,
        result: ContractValidationResult,
        *,
        actor_id: str,
        room_id: str,
        event_id: str | None = None,
        rule_id: str | None = None,
    ) -> GovernanceDecision:
        """Convert a validator result to the explicit Systemform decision model."""

        return GovernanceDecision(
            decision=result.decision,
            reason=result.reason,
            actor_id=actor_id,
            room_id=room_id,
            event_id=event_id,
            rule_id=rule_id,
            requires_human=result.requires_human,
        )

    def _validate_resources(
        self,
        *,
        actor: ActorIdentity,
        room: Room,
        contract: CellContract,
        resource_request: dict[str, int | float],
        resource_grant: ResourceGrant | None,
        now: datetime,
    ) -> ContractValidationResult | None:
        if not resource_request:
            return None
        if resource_grant is None:
            return self._block("resource_grant_missing")
        if resource_grant.actor_id != actor.id:
            return self._block("resource_grant_actor_mismatch")
        if resource_grant.room_id != room.id:
            return self._block("resource_grant_room_mismatch")
        if resource_grant.expires_at is not None and resource_grant.expires_at <= now:
            return self._block("resource_grant_expired")

        for key, requested in resource_request.items():
            contract_limit = contract.resource_limits.get(key)
            if contract_limit is None:
                return self._block("resource_limit_missing")
            if requested > contract_limit:
                return self._block("resource_limit_exceeded")

            grant_limit = resource_grant.limits.get(key)
            if grant_limit is None:
                return self._block("resource_grant_limit_missing")
            if requested > grant_limit:
                return self._block("resource_grant_limit_exceeded")

        return None

    @staticmethod
    def _permission_allowed(permissions: dict[str, Any], action: str) -> bool:
        if action not in permissions:
            return False
        value = permissions[action]
        if isinstance(value, bool):
            return value
        if isinstance(value, dict):
            return value.get("allowed", True) is not False
        return bool(value)

    @staticmethod
    def _block(reason: str) -> ContractValidationResult:
        return ContractValidationResult(
            allowed=False,
            decision=GuardDecisionType.BLOCK,
            reason=reason,
        )
