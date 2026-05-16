from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.core.audit import AuditLogger
from pigenus.core.worker_assignment_creator import WorkerAssignmentCreator
from pigenus.core.worker_assignment_validator import WorkerAssignmentValidator
from pigenus.core.worker_execution_preflight import (
    WorkerExecutionPreflightLogger,
    WorkerExecutionPreflightRequest,
    WorkerExecutionPreflightService,
)
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
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
from pigenus.storage.repositories import AuditRepository, DecisionRepository, WorkerRepository
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-creator-tests"
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


def log_preflight_decision(
    database: Database,
    *,
    worker_id: str = "worker_local",
    capability: str = "meaning_ingester",
    room_id: str = "room_developer",
) -> str:
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
            network_required=True,
        )
    )
    record = WorkerExecutionPreflightLogger(DecisionRepository(database)).add(
        result,
        actor_id="agent_preflight",
        room_id=room_id,
        event_id="evt_preflight",
    )
    return record.decision_id


def creator(database: Database) -> WorkerAssignmentCreator:
    return WorkerAssignmentCreator(
        validator=WorkerAssignmentValidator(
            workers=WorkerRepository(database),
            decisions=DecisionRepository(database),
        ),
        assignments=WorkerAssignmentRepository(database),
        audit_logger=AuditLogger(AuditRepository(database)),
    )


def test_worker_assignment_creator_writes_assignment_and_audit_for_valid_intent():
    database = prepare_database()
    decision_id = log_preflight_decision(database)

    result = creator(database).create(assignment(decision_id))

    assignments = WorkerAssignmentRepository(database).list()
    audits = AuditRepository(database).list()
    assert result.created is True
    assert result.audit_id is not None
    assert result.assignment is not None
    assert result.validation.valid is True
    assert len(assignments) == 1
    assert assignments[0].id == "wasg_candidate"
    assert assignments[0].status == WorkerAssignmentStatus.PENDING
    assert len(audits) == 1
    assert audits[0]["audit_id"] == result.audit_id
    assert audits[0]["actor"] == "agent_scheduler_preview"
    assert audits[0]["action"] == "worker_assignment_created"
    assert audits[0]["context"] == {"name": "developer/default"}
    assert audits[0]["details"] == {
        "assignment_id": "wasg_candidate",
        "worker_id": "worker_local",
        "capability": "meaning_ingester",
        "room_id": "room_developer",
        "governance_decision_id": decision_id,
        "status": "pending",
    }
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_creator_does_not_write_on_validation_failure():
    database = prepare_database(cells=["log_reader"])
    decision_id = log_preflight_decision(database)

    result = creator(database).create(assignment(decision_id))

    assert result.created is False
    assert result.assignment is None
    assert result.audit_id is None
    assert "evidence_decision_not_allow" in result.validation.reasons
    assert WorkerAssignmentRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_creator_does_not_write_for_non_pending_status():
    database = prepare_database()
    decision_id = log_preflight_decision(database)

    result = creator(database).create(
        assignment(decision_id, status=WorkerAssignmentStatus.ASSIGNED)
    )

    assert result.created is False
    assert "assignment_status_must_be_pending" in result.validation.reasons
    assert WorkerAssignmentRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 1
    database.close()
