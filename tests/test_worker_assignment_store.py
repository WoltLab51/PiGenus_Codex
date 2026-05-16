from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

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
    DecisionRepository,
    WorkerAssignmentRepository,
    WorkerRepository,
)


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-store-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(worker_id: str) -> WorkerProfile:
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


def decision(decision_id: str) -> DecisionRecord:
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
    assignment_id: str,
    *,
    worker_id: str = "worker_local",
    governance_decision_id: str = "dec_preflight",
    capability: str = "meaning_ingester",
    room_id: str = "room_developer",
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.PENDING,
    created_at: datetime = datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
) -> WorkerAssignment:
    return WorkerAssignment(
        id=assignment_id,
        worker_id=worker_id,
        capability=capability,
        room_id=room_id,
        governance_decision_id=governance_decision_id,
        created_by_actor_id="agent_scheduler_preview",
        status=status,
        required_runtime="python",
        sensitivity=Sensitivity.PRIVATE,
        reason="preflight_allowed",
        created_at=created_at,
        updated_at=created_at,
    )


def prepare_repository(
    database: Database,
    *,
    worker_id: str = "worker_local",
    decision_id: str = "dec_preflight",
) -> WorkerAssignmentRepository:
    WorkerRepository(database).add_profile(worker_profile(worker_id))
    DecisionRepository(database).add(decision(decision_id))
    return WorkerAssignmentRepository(database)


def test_worker_assignment_repository_adds_and_gets_assignment():
    database = Database(db_path("roundtrip"))
    database.initialize()
    repository = prepare_repository(database)
    original = assignment("wasg_roundtrip")

    repository.add(original)
    stored = repository.get("wasg_roundtrip")

    assert stored == original
    assert stored is not None
    assert stored.governance_decision_id == "dec_preflight"
    assert stored.sensitivity == Sensitivity.PRIVATE
    assert repository.count() == 1
    data = stored.model_dump(mode="json")
    assert "started_at" not in data
    assert "completed_at" not in data
    assert "execution_result" not in data
    database.close()


def test_worker_assignment_repository_lists_with_filters_in_created_order():
    database = Database(db_path("filters"))
    database.initialize()
    repository = prepare_repository(database)
    WorkerRepository(database).add_profile(worker_profile("worker_other"))
    DecisionRepository(database).add(decision("dec_other"))

    repository.add(
        assignment(
            "wasg_second",
            capability="log_reader",
            room_id="room_private",
            status=WorkerAssignmentStatus.ASSIGNED,
            created_at=datetime(2026, 5, 16, 9, 0, tzinfo=timezone.utc),
        )
    )
    repository.add(
        assignment(
            "wasg_first",
            worker_id="worker_other",
            governance_decision_id="dec_other",
            capability="meaning_ingester",
            room_id="room_developer",
            created_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        )
    )

    assert [item.id for item in repository.list()] == ["wasg_first", "wasg_second"]
    assert [item.id for item in repository.list(worker_id="worker_other")] == ["wasg_first"]
    assert [item.id for item in repository.list(status="assigned")] == ["wasg_second"]
    assert [item.id for item in repository.list(room_id="room_private")] == ["wasg_second"]
    assert [item.id for item in repository.list(capability="meaning_ingester")] == [
        "wasg_first"
    ]
    assert [item.id for item in repository.list(governance_decision_id="dec_other")] == [
        "wasg_first"
    ]
    database.close()


def test_worker_assignment_repository_rejects_unknown_worker():
    database = Database(db_path("unknown-worker"))
    database.initialize()
    DecisionRepository(database).add(decision("dec_preflight"))
    repository = WorkerAssignmentRepository(database)

    try:
        repository.add(assignment("wasg_unknown_worker"))
    except ValueError as exc:
        assert "Unknown worker_id" in str(exc)
    else:
        raise AssertionError("Expected assignment for unknown worker to fail.")
    database.close()


def test_worker_assignment_repository_rejects_unknown_governance_decision():
    database = Database(db_path("unknown-decision"))
    database.initialize()
    WorkerRepository(database).add_profile(worker_profile("worker_local"))
    repository = WorkerAssignmentRepository(database)

    try:
        repository.add(assignment("wasg_unknown_decision"))
    except ValueError as exc:
        assert "Unknown governance_decision_id" in str(exc)
    else:
        raise AssertionError("Expected assignment without governance evidence to fail.")
    database.close()


def test_worker_assignment_repository_returns_none_for_missing_assignment():
    database = Database(db_path("missing"))
    database.initialize()
    repository = WorkerAssignmentRepository(database)

    assert repository.get("wasg_missing") is None
    assert repository.list() == []
    assert repository.count() == 0
    database.close()
