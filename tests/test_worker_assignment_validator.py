from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.core.worker_assignment_validator import WorkerAssignmentValidator
from pigenus.core.worker_execution_preflight import (
    WorkerExecutionPreflightLogger,
    WorkerExecutionPreflightRequest,
    WorkerExecutionPreflightService,
)
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.core.worker_scheduling_preview import (
    WorkerSchedulingPreviewLogger,
    WorkerSchedulingPreviewService,
    WorkerSchedulingRequest,
)
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import DecisionRepository, WorkerRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-validator-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(
    worker_id: str,
    *,
    cells: list[str] | None = None,
    network_access: bool = True,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=WorkerStatus.ACTIVE,
        home_room_id="room_developer",
        available_cells=cells or ["meaning_ingester"],
        supported_runtimes=["python"],
        max_sensitivity=Sensitivity.PRIVATE,
        network_access=network_access,
    )


def assignment(
    decision_id: str,
    *,
    assignment_id: str = "wasg_candidate",
    worker_id: str = "worker_local",
    capability: str = "meaning_ingester",
    room_id: str = "room_developer",
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.PENDING,
) -> WorkerAssignment:
    return WorkerAssignment(
        id=assignment_id,
        worker_id=worker_id,
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


def prepare_database(
    *,
    worker_id: str = "worker_local",
    cells: list[str] | None = None,
    network_access: bool = True,
) -> Database:
    database = Database(db_path(worker_id))
    database.initialize()
    worker_repository = WorkerRepository(database)
    worker_repository.add_profile(
        worker_profile(
            worker_id,
            cells=cells,
            network_access=network_access,
        )
    )
    worker_repository.record_heartbeat(
        WorkerHeartbeat(worker_id=worker_id, status=WorkerStatus.ACTIVE)
    )
    return database


def add_worker(database: Database, worker_id: str) -> None:
    repository = WorkerRepository(database)
    repository.add_profile(worker_profile(worker_id))
    repository.record_heartbeat(WorkerHeartbeat(worker_id=worker_id, status=WorkerStatus.ACTIVE))


def log_preflight_decision(
    database: Database,
    *,
    worker_id: str = "worker_local",
    capability: str = "meaning_ingester",
    room_id: str = "room_developer",
    network_required: bool = True,
) -> DecisionRecord:
    registry = WorkerRegistry()
    workers = WorkerRepository(database)
    for profile in workers.list_profiles():
        registry.register(profile)
    for heartbeat in workers.list_heartbeats():
        registry.record_heartbeat(heartbeat)
    result = WorkerExecutionPreflightService(WorkerInspectionService(registry)).check(
        WorkerExecutionPreflightRequest(
            worker_id=worker_id,
            capability=capability,
            required_runtime="python",
            sensitivity=Sensitivity.PRIVATE,
            network_required=network_required,
        )
    )
    return WorkerExecutionPreflightLogger(DecisionRepository(database)).add(
        result,
        actor_id="agent_preflight",
        room_id=room_id,
        event_id="evt_preflight",
    )


def validator(database: Database) -> WorkerAssignmentValidator:
    return WorkerAssignmentValidator(
        workers=WorkerRepository(database),
        decisions=DecisionRepository(database),
    )


def test_worker_assignment_validator_allows_matching_preflight_allow_evidence():
    database = prepare_database()
    decision = log_preflight_decision(database)

    result = validator(database).validate(assignment(decision.decision_id))

    assert result.valid is True
    assert result.reasons == ("worker_assignment_valid",)
    assert WorkerRepository(database).count_profiles() == 1
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_validator_rejects_block_preflight_evidence():
    database = prepare_database(cells=["log_reader"])
    decision = log_preflight_decision(database)

    result = validator(database).validate(assignment(decision.decision_id))

    assert result.valid is False
    assert "evidence_decision_not_allow" in result.reasons
    database.close()


def test_worker_assignment_validator_rejects_scheduling_preview_evidence():
    database = prepare_database()
    registry = WorkerRegistry()
    registry.register(WorkerRepository(database).get_profile("worker_local"))
    registry.record_heartbeat(WorkerRepository(database).get_heartbeat("worker_local"))
    preview = WorkerSchedulingPreviewService(WorkerInspectionService(registry)).preview(
        WorkerSchedulingRequest(
            capability="meaning_ingester",
            required_runtime="python",
            sensitivity=Sensitivity.PRIVATE,
            network_required=True,
        )
    )
    decision = WorkerSchedulingPreviewLogger(DecisionRepository(database)).add(
        preview,
        actor_id="agent_preview",
        room_id="room_developer",
    )

    result = validator(database).validate(assignment(decision.decision_id))

    assert result.valid is False
    assert "evidence_source_invalid" in result.reasons
    assert "evidence_family_invalid" in result.reasons
    database.close()


def test_worker_assignment_validator_rejects_wrong_worker():
    database = prepare_database()
    add_worker(database, "worker_other")
    decision = log_preflight_decision(database)

    result = validator(database).validate(
        assignment(decision.decision_id, worker_id="worker_other")
    )

    assert result.valid is False
    assert "worker_mismatch" in result.reasons
    database.close()


def test_worker_assignment_validator_rejects_wrong_capability():
    database = prepare_database()
    decision = log_preflight_decision(database)

    result = validator(database).validate(
        assignment(decision.decision_id, capability="log_reader")
    )

    assert result.valid is False
    assert "capability_mismatch" in result.reasons
    database.close()


def test_worker_assignment_validator_rejects_wrong_room():
    database = prepare_database()
    decision = log_preflight_decision(database)

    result = validator(database).validate(
        assignment(decision.decision_id, room_id="room_private")
    )

    assert result.valid is False
    assert "room_mismatch" in result.reasons
    database.close()


def test_worker_assignment_validator_rejects_non_pending_status():
    database = prepare_database()
    decision = log_preflight_decision(database)

    result = validator(database).validate(
        assignment(decision.decision_id, status=WorkerAssignmentStatus.ASSIGNED)
    )

    assert result.valid is False
    assert "assignment_status_must_be_pending" in result.reasons
    database.close()


def test_worker_assignment_validator_rejects_unknown_worker_and_decision():
    database = Database(db_path("missing"))
    database.initialize()

    result = validator(database).validate(
        assignment("dec_missing", worker_id="worker_missing")
    )

    assert result.valid is False
    assert "worker_unknown" in result.reasons
    assert "governance_decision_unknown" in result.reasons
    database.close()
