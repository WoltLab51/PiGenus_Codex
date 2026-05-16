from __future__ import annotations

import subprocess
import sys
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
    AuditRepository,
    DecisionRepository,
    WorkerAssignmentRepository,
    WorkerRepository,
)


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_assignment_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-assignment-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


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


def seed_assignments(path: Path) -> None:
    database = Database(path)
    database.initialize()
    WorkerRepository(database).add_profile(worker_profile("worker_local"))
    WorkerRepository(database).add_profile(worker_profile("worker_other"))
    DecisionRepository(database).add(decision("dec_preflight"))
    DecisionRepository(database).add(decision("dec_other"))
    repository = WorkerAssignmentRepository(database)
    repository.add(
        assignment(
            "wasg_first",
            created_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        )
    )
    repository.add(
        assignment(
            "wasg_second",
            worker_id="worker_other",
            governance_decision_id="dec_other",
            capability="log_reader",
            room_id="room_private",
            status=WorkerAssignmentStatus.ASSIGNED,
            created_at=datetime(2026, 5, 16, 9, 0, tzinfo=timezone.utc),
        )
    )
    database.close()


def test_worker_assignment_list_reports_empty_database():
    path = db_path("empty")

    result = run_assignment_list(path)

    assert result.returncode == 0
    assert "No worker assignments found." in result.stdout


def test_worker_assignment_list_prints_rows_without_modifying_data():
    path = db_path("rows")
    seed_assignments(path)

    result = run_assignment_list(path)

    database = Database(path)
    database.initialize()
    assert "wasg_first | worker=worker_local | status=pending" in result.stdout
    assert "capability=meaning_ingester" in result.stdout
    assert "decision=dec_preflight" in result.stdout
    assert "wasg_second | worker=worker_other | status=assigned" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 2
    assert DecisionRepository(database).count() == 2
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_list_filters_by_worker_status_room_capability_and_decision():
    path = db_path("filters")
    seed_assignments(path)

    result = run_assignment_list(
        path,
        "--worker",
        "worker_other",
        "--status",
        "assigned",
        "--room",
        "room_private",
        "--capability",
        "log_reader",
        "--governance-decision",
        "dec_other",
    )

    assert "wasg_second | worker=worker_other | status=assigned" in result.stdout
    assert "room=room_private" in result.stdout
    assert "capability=log_reader" in result.stdout
    assert "wasg_first" not in result.stdout
