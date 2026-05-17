from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.core.worker_assignment_room_context_recheck import (
    WorkerAssignmentRoomContextRecheckOutcome,
    WorkerAssignmentRoomContextRecheckValidator,
)
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    ContextFrame,
    ContextFrameType,
    ContextStack,
    Sensitivity,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    DecisionRepository,
    WorkerRepository,
)
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-room-context-recheck-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(
    worker_id: str = "worker_local",
    *,
    home_room_id: str | None = "room_developer",
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=WorkerStatus.ACTIVE,
        home_room_id=home_room_id,
        available_cells=["meaning_ingester"],
        supported_runtimes=["python"],
        max_sensitivity=Sensitivity.PRIVATE,
        network_access=True,
    )


def preflight_decision(
    *,
    decision_id: str = "dec_preflight",
    room_id: str = "room_developer",
) -> DecisionRecord:
    return DecisionRecord(
        decision_id=decision_id,
        decision_type="governance_decision",
        context={"name": "developer/default"},
        subject_id="evt_preflight",
        actor="agent_preflight",
        reason="worker_execution_preflight_passed",
        source="worker_execution_preflight",
        created_at=datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc),
        details={
            "decision": "allow",
            "family": "worker_execution_preflight",
            "room_id": room_id,
            "governance_decision": {
                "room_id": room_id,
                "details": {
                    "worker_id": "worker_local",
                    "request": {
                        "worker_id": "worker_local",
                        "capability": "meaning_ingester",
                        "required_runtime": "python",
                        "sensitivity": "private",
                        "network_required": True,
                    },
                },
            },
        },
    )


def assignment(
    *,
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.ASSIGNED,
    decision_id: str = "dec_preflight",
    room_id: str = "room_developer",
    capability: str = "meaning_ingester",
) -> WorkerAssignment:
    return WorkerAssignment(
        id="wasg_room_context",
        worker_id="worker_local",
        capability=capability,
        room_id=room_id,
        governance_decision_id=decision_id,
        created_by_actor_id="agent_scheduler_preview",
        status=status,
        required_runtime="python",
        sensitivity=Sensitivity.PRIVATE,
        network_required=True,
        reason="preflight_allowed",
        created_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
    )


def context_frame(
    *,
    frame_id: str = "cf_developer",
    room_id: str = "room_developer",
    allowed_capabilities: list[str] | None = None,
    denied_capabilities: list[str] | None = None,
) -> ContextFrame:
    return ContextFrame(
        id=frame_id,
        type=ContextFrameType.GOVERNANCE,
        name=frame_id,
        room_id=room_id,
        allowed_capabilities=allowed_capabilities or [],
        denied_capabilities=denied_capabilities or [],
    )


def context_stack(*, frame_ids: list[str] | None = None) -> ContextStack:
    return ContextStack(
        id="cstack_developer",
        name="developer context",
        frame_ids=frame_ids or ["cf_developer"],
    )


def prepare_database(
    *,
    profile: WorkerProfile | None = None,
    decision: DecisionRecord | None = None,
    item: WorkerAssignment | None = None,
) -> Database:
    database = Database(db_path("room-context"))
    database.initialize()
    WorkerRepository(database).add_profile(profile or worker_profile())
    DecisionRepository(database).add(decision or preflight_decision())
    WorkerAssignmentRepository(database).add(item or assignment())
    return database


def validator(database: Database) -> WorkerAssignmentRoomContextRecheckValidator:
    return WorkerAssignmentRoomContextRecheckValidator(
        assignments=WorkerAssignmentRepository(database),
        workers=WorkerRepository(database),
        decisions=DecisionRepository(database),
    )


def assert_no_writes(database: Database) -> None:
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0


def test_room_context_recheck_allows_matching_room_and_context():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame(allowed_capabilities=["meaning_ingester"])],
    )

    assert result.context_compatible is True
    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.ALLOW
    assert result.reasons == ("room_context_recheck_passed",)
    assert result.details["worker_home_room_id"] == "room_developer"
    assert result.details["evidence_room_id"] == "room_developer"
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_skips_unknown_assignment():
    database = Database(db_path("room-context-missing"))
    database.initialize()

    result = validator(database).validate("wasg_missing")

    assert result.context_compatible is False
    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.NOT_CONSIDERED
    assert result.reasons == ("assignment_unknown",)
    assert WorkerAssignmentRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_room_context_recheck_skips_non_assigned_status():
    database = prepare_database(
        item=assignment(status=WorkerAssignmentStatus.PENDING),
    )

    result = validator(database).validate("wasg_room_context")

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.NOT_CONSIDERED
    assert result.reasons == ("assignment_status_not_considered",)
    assert WorkerAssignmentRepository(database).get("wasg_room_context").status == (
        WorkerAssignmentStatus.PENDING
    )
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_denies_mismatched_evidence_room():
    database = prepare_database(
        decision=preflight_decision(room_id="room_private"),
    )

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame()],
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.DENY
    assert result.reasons == ("room_evidence_mismatch",)
    assert result.details["evidence_room_id"] == "room_private"
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_reviews_worker_home_room_mismatch():
    database = prepare_database(profile=worker_profile(home_room_id="room_private"))

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame()],
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.REQUIRE_REVIEW
    assert result.reasons == ("worker_home_room_mismatch",)
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_denies_unknown_worker_after_assignment_exists():
    database = prepare_database()
    database.execute("DELETE FROM worker_profiles WHERE worker_id = ?", ("worker_local",))

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame()],
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.DENY
    assert result.reasons == ("worker_unknown",)
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_reviews_missing_context_stack():
    database = prepare_database()

    result = validator(database).validate("wasg_room_context")

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.REQUIRE_REVIEW
    assert result.reasons == ("context_stack_not_evaluated",)
    assert result.details["context_frame_ids"] == []
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_denies_context_room_mismatch():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame(room_id="room_private")],
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.DENY
    assert result.reasons == ("context_room_mismatch",)
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_denies_context_policy_mismatch():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame(denied_capabilities=["meaning_ingester"])],
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.DENY
    assert result.reasons == ("context_policy_mismatch",)
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_carries_room_flow_review():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame()],
        source_room_id="room_private",
        target_room_id="room_family",
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.REQUIRE_REVIEW
    assert result.reasons == ("room_flow_review_required",)
    assert result.details["room_flow"]["decision"] == "review"
    assert_no_writes(database)
    database.close()


def test_room_context_recheck_carries_room_flow_block():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_room_context",
        context_stack=context_stack(),
        context_frames=[context_frame()],
        source_room_id="room_private",
        target_room_id="room_public",
    )

    assert result.outcome == WorkerAssignmentRoomContextRecheckOutcome.DENY
    assert result.reasons == ("room_flow_blocked",)
    assert result.details["room_flow"]["decision"] == "block"
    assert_no_writes(database)
    database.close()
