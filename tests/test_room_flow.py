from __future__ import annotations

from pigenus.core.room_flow import RoomFlowDecisionType, RoomFlowRules
from pigenus.schemas.systemform import (
    MeaningObject,
    Room,
    RoomProtectionLevel,
    Sensitivity,
    TruthStatus,
)


def room(room_id: str, name: str | None = None) -> Room:
    return Room(
        id=room_id,
        name=name or room_id.removeprefix("room_"),
        protection_level=RoomProtectionLevel.MEDIUM,
    )


def meaning(
    *,
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
    truth_status: TruthStatus = TruthStatus.VERIFIED,
    room_id: str = "room_developer",
) -> MeaningObject:
    return MeaningObject(
        type="fact",
        content={"text": "Room flow test meaning."},
        room_id=room_id,
        truth_status=truth_status,
        sensitivity=sensitivity,
        created_by="test",
    )


def test_room_flow_allows_same_room():
    decision = RoomFlowRules().decide(
        source_room=room("room_private"),
        target_room=room("room_private"),
        meaning=meaning(sensitivity=Sensitivity.PRIVATE, room_id="room_private"),
    )

    assert decision.decision == RoomFlowDecisionType.ALLOW
    assert decision.reason == "same_room"
    assert decision.requires_human is False


def test_room_flow_reviews_private_to_family():
    decision = RoomFlowRules().decide(
        source_room=room("room_private"),
        target_room=room("room_family"),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW
    assert decision.reason == "matrix_review"
    assert decision.requires_human is True


def test_room_flow_blocks_private_to_public():
    decision = RoomFlowRules().decide(
        source_room=room("room_private"),
        target_room=room("room_public"),
        meaning=meaning(sensitivity=Sensitivity.PRIVATE, room_id="room_private"),
    )

    assert decision.decision == RoomFlowDecisionType.BLOCK
    assert decision.reason == "sensitive_meaning_public_export_blocked"


def test_room_flow_blocks_family_to_public():
    decision = RoomFlowRules().decide(
        source_room=room("room_family"),
        target_room=room("room_public"),
        meaning=meaning(sensitivity=Sensitivity.FAMILY, room_id="room_family"),
    )

    assert decision.decision == RoomFlowDecisionType.BLOCK


def test_room_flow_reviews_family_to_external():
    decision = RoomFlowRules().decide(
        source_room=room("room_family"),
        target_room=room("room_external"),
        meaning=meaning(sensitivity=Sensitivity.INTERNAL, room_id="room_family"),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW
    assert decision.reason == "matrix_review"


def test_room_flow_blocks_trading_to_public():
    decision = RoomFlowRules().decide(
        source_room=room("room_trading"),
        target_room=room("room_public"),
        meaning=meaning(sensitivity=Sensitivity.FINANCIAL, room_id="room_trading"),
    )

    assert decision.decision == RoomFlowDecisionType.BLOCK


def test_room_flow_reviews_trading_to_external():
    decision = RoomFlowRules().decide(
        source_room=room("room_trading"),
        target_room=room("room_external"),
        meaning=meaning(sensitivity=Sensitivity.INTERNAL, room_id="room_trading"),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW


def test_room_flow_allows_developer_to_sandbox_for_internal_verified_meaning():
    decision = RoomFlowRules().decide(
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(sensitivity=Sensitivity.INTERNAL),
    )

    assert decision.decision == RoomFlowDecisionType.ALLOW
    assert decision.reason == "matrix_allow"


def test_room_flow_reviews_sandbox_to_developer():
    decision = RoomFlowRules().decide(
        source_room=room("room_sandbox"),
        target_room=room("room_developer"),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW


def test_room_flow_blocks_sandbox_to_production():
    decision = RoomFlowRules().decide(
        source_room=room("room_sandbox"),
        target_room=room("room_production"),
    )

    assert decision.decision == RoomFlowDecisionType.BLOCK
    assert decision.reason == "matrix_block"


def test_room_flow_allows_read_from_public_to_private():
    decision = RoomFlowRules().decide(
        source_room=room("room_public"),
        target_room=room("room_private"),
        meaning=meaning(sensitivity=Sensitivity.PUBLIC, room_id="room_public"),
    )

    assert decision.decision == RoomFlowDecisionType.ALLOW_READ
    assert decision.reason == "matrix_allow_read"


def test_room_flow_reviews_public_to_family():
    decision = RoomFlowRules().decide(
        source_room=room("room_public"),
        target_room=room("room_family"),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW


def test_room_flow_reviews_unknown_pair_by_default():
    decision = RoomFlowRules().decide(
        source_room=room("room_developer"),
        target_room=room("room_private"),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW
    assert decision.reason == "flow_not_in_matrix"


def test_room_flow_blocks_secret_cross_room_even_when_matrix_allows():
    decision = RoomFlowRules().decide(
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(sensitivity=Sensitivity.SECRET),
    )

    assert decision.decision == RoomFlowDecisionType.BLOCK
    assert decision.reason == "secret_meaning_cross_room_blocked"


def test_room_flow_blocks_unsafe_meaning():
    decision = RoomFlowRules().decide(
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(truth_status=TruthStatus.UNSAFE),
    )

    assert decision.decision == RoomFlowDecisionType.BLOCK
    assert decision.reason == "unsafe_meaning_blocked"


def test_room_flow_reviews_contested_meaning_even_when_matrix_allows():
    decision = RoomFlowRules().decide(
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(truth_status=TruthStatus.CONTESTED),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW
    assert decision.reason == "truth_status_requires_review"


def test_room_flow_reviews_high_sensitivity_even_when_matrix_allows():
    decision = RoomFlowRules().decide(
        source_room=room("room_developer"),
        target_room=room("room_sandbox"),
        meaning=meaning(sensitivity=Sensitivity.CHILD_RELATED),
    )

    assert decision.decision == RoomFlowDecisionType.REVIEW
    assert decision.reason == "sensitivity_requires_review"
