from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from pigenus.schemas.systemform import MeaningObject, Room, Sensitivity, TruthStatus


class RoomFlowDecisionType(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"
    ALLOW_READ = "allow_read"


class RoomFlowDecision(BaseModel):
    """Deterministic decision for information flow between two rooms."""

    decision: RoomFlowDecisionType
    reason: str
    source_room_id: str
    target_room_id: str
    requires_human: bool = False


ROOM_FLOW_MATRIX: dict[tuple[str, str], RoomFlowDecisionType] = {
    ("room_private", "room_family"): RoomFlowDecisionType.REVIEW,
    ("room_private", "room_public"): RoomFlowDecisionType.BLOCK,
    ("room_private", "room_external"): RoomFlowDecisionType.BLOCK,
    ("room_family", "room_public"): RoomFlowDecisionType.BLOCK,
    ("room_family", "room_external"): RoomFlowDecisionType.REVIEW,
    ("room_trading", "room_public"): RoomFlowDecisionType.BLOCK,
    ("room_trading", "room_external"): RoomFlowDecisionType.REVIEW,
    ("room_developer", "room_sandbox"): RoomFlowDecisionType.ALLOW,
    ("room_sandbox", "room_developer"): RoomFlowDecisionType.REVIEW,
    ("room_sandbox", "room_production"): RoomFlowDecisionType.BLOCK,
    ("room_public", "room_private"): RoomFlowDecisionType.ALLOW_READ,
    ("room_public", "room_family"): RoomFlowDecisionType.REVIEW,
}

PUBLIC_ROOM_IDS = {"room_public", "room_external"}
HIGH_SENSITIVITY = {
    Sensitivity.PRIVATE,
    Sensitivity.FAMILY,
    Sensitivity.FINANCIAL,
    Sensitivity.CHILD_RELATED,
    Sensitivity.SECRET,
}
PUBLIC_BLOCKED_SENSITIVITY = {
    Sensitivity.PRIVATE,
    Sensitivity.FAMILY,
    Sensitivity.FINANCIAL,
    Sensitivity.CHILD_RELATED,
    Sensitivity.SECRET,
}
REVIEW_TRUTH_STATUS = {
    TruthStatus.CONTESTED,
    TruthStatus.DEPRECATED,
    TruthStatus.SIMULATED,
    TruthStatus.HISTORICAL,
}


class RoomFlowRules:
    """Small storage-free policy for semantic flow between Systemform rooms."""

    def decide(
        self,
        *,
        source_room: Room,
        target_room: Room,
        meaning: MeaningObject | None = None,
    ) -> RoomFlowDecision:
        if source_room.id == target_room.id:
            return self._decision(
                RoomFlowDecisionType.ALLOW,
                "same_room",
                source_room,
                target_room,
            )

        if target_room.id in PUBLIC_ROOM_IDS and meaning is not None:
            if meaning.sensitivity in PUBLIC_BLOCKED_SENSITIVITY:
                return self._decision(
                    RoomFlowDecisionType.BLOCK,
                    "sensitive_meaning_public_export_blocked",
                    source_room,
                    target_room,
                )

        if meaning is not None and meaning.sensitivity == Sensitivity.SECRET:
            return self._decision(
                RoomFlowDecisionType.BLOCK,
                "secret_meaning_cross_room_blocked",
                source_room,
                target_room,
            )

        if meaning is not None and meaning.truth_status == TruthStatus.UNSAFE:
            return self._decision(
                RoomFlowDecisionType.BLOCK,
                "unsafe_meaning_blocked",
                source_room,
                target_room,
            )

        matrix_decision = ROOM_FLOW_MATRIX.get((source_room.id, target_room.id))
        if matrix_decision is None:
            return self._decision(
                RoomFlowDecisionType.REVIEW,
                "flow_not_in_matrix",
                source_room,
                target_room,
            )

        if meaning is not None and meaning.truth_status in REVIEW_TRUTH_STATUS:
            if matrix_decision == RoomFlowDecisionType.ALLOW:
                return self._decision(
                    RoomFlowDecisionType.REVIEW,
                    "truth_status_requires_review",
                    source_room,
                    target_room,
                )

        if meaning is not None and meaning.sensitivity in HIGH_SENSITIVITY:
            if matrix_decision == RoomFlowDecisionType.ALLOW:
                return self._decision(
                    RoomFlowDecisionType.REVIEW,
                    "sensitivity_requires_review",
                    source_room,
                    target_room,
                )

        return self._decision(
            matrix_decision,
            f"matrix_{matrix_decision.value}",
            source_room,
            target_room,
        )

    @staticmethod
    def _decision(
        decision: RoomFlowDecisionType,
        reason: str,
        source_room: Room,
        target_room: Room,
    ) -> RoomFlowDecision:
        return RoomFlowDecision(
            decision=decision,
            reason=reason,
            source_room_id=source_room.id,
            target_room_id=target_room.id,
            requires_human=decision == RoomFlowDecisionType.REVIEW,
        )
