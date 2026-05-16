from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.core.audit import AuditLogger
from pigenus.core.worker_assignment_status_transition import (
    WorkerAssignmentStatusTransitionService,
)
from pigenus.core.worker_assignment_status_transition_validator import (
    WorkerAssignmentStatusTransitionValidator,
)
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
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
    root = Path(".testdata") / "worker-assignment-status-transition-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(worker_id: str = "worker_local") -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=WorkerStatus.ACTIVE,
        home_room_id="room_developer",
        available_cells=["meaning_ingester"],
        supported_runtimes=["python"],
        max_sensitivity=Sensitivity.PRIVATE,
    )


def decision(decision_id: str = "dec_preflight") -> DecisionRecord:
    return DecisionRecord(
        decision_id=decision_id,
        decision_type="governance_decision",
        context={"name": "developer/default"},
        subject_id="worker_assignment_candidate",
        actor="worker_execution_preflight_cli",
        reason="worker_execution_preflight_passed",
        source="worker_execution_preflight",
        details={"decision": "allow"},
    )


def assignment(
    assignment_id: str = "wasg_transition",
    *,
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.PENDING,
) -> WorkerAssignment:
    return WorkerAssignment(
        id=assignment_id,
        worker_id="worker_local",
        capability="meaning_ingester",
        room_id="room_developer",
        governance_decision_id="dec_preflight",
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
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.PENDING,
) -> Database:
    database = Database(db_path(status.value))
    database.initialize()
    WorkerRepository(database).add_profile(worker_profile())
    DecisionRepository(database).add(decision())
    WorkerAssignmentRepository(database).add(assignment(status=status))
    return database


def service(database: Database) -> WorkerAssignmentStatusTransitionService:
    return WorkerAssignmentStatusTransitionService(
        validator=WorkerAssignmentStatusTransitionValidator(),
        assignments=WorkerAssignmentRepository(database),
        audit_logger=AuditLogger(AuditRepository(database)),
    )


def test_worker_assignment_status_transition_service_updates_status_and_audit():
    database = prepare_database()

    result = service(database).transition(
        "wasg_transition",
        WorkerAssignmentStatus.ASSIGNED,
        actor_id="agent_operator",
        reason="manual_activation_preview",
    )

    stored = WorkerAssignmentRepository(database).get("wasg_transition")
    audits = AuditRepository(database).list()
    assert result.transitioned is True
    assert result.audit_id is not None
    assert result.assignment is not None
    assert result.validation.valid is True
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.ASSIGNED
    assert stored.created_at == datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc)
    assert stored.updated_at > stored.created_at
    assert len(audits) == 1
    assert audits[0]["audit_id"] == result.audit_id
    assert audits[0]["actor"] == "agent_operator"
    assert audits[0]["action"] == "worker_assignment_status_changed"
    assert audits[0]["context"] == {"name": "developer/default"}
    assert audits[0]["details"] == {
        "assignment_id": "wasg_transition",
        "worker_id": "worker_local",
        "capability": "meaning_ingester",
        "room_id": "room_developer",
        "old_status": "pending",
        "new_status": "assigned",
        "actor_id": "agent_operator",
        "reason": "manual_activation_preview",
    }
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_status_transition_service_rejects_invalid_transition_without_writes():
    database = prepare_database(status=WorkerAssignmentStatus.ASSIGNED)

    result = service(database).transition(
        "wasg_transition",
        WorkerAssignmentStatus.REJECTED,
        actor_id="agent_operator",
        reason="late_rejection",
    )

    stored = WorkerAssignmentRepository(database).get("wasg_transition")
    assert result.transitioned is False
    assert result.assignment is None
    assert result.audit_id is None
    assert "status_transition_not_allowed" in result.validation.reasons
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.ASSIGNED
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_status_transition_service_rejects_missing_assignment():
    database = prepare_database()

    result = service(database).transition(
        "wasg_missing",
        WorkerAssignmentStatus.CANCELLED,
        actor_id="agent_operator",
    )

    assert result.transitioned is False
    assert result.assignment is None
    assert result.audit_id is None
    assert result.validation.reasons == ("assignment_unknown",)
    assert WorkerAssignmentRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_status_transition_service_rejects_unknown_target_without_writes():
    database = prepare_database()

    result = service(database).transition(
        "wasg_transition",
        "running",
        actor_id="agent_operator",
    )

    stored = WorkerAssignmentRepository(database).get("wasg_transition")
    assert result.transitioned is False
    assert result.assignment is None
    assert result.audit_id is None
    assert result.validation.reasons == ("target_status_unknown",)
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.PENDING
    assert AuditRepository(database).count() == 0
    database.close()
