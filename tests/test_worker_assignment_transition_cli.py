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
    WorkerRepository,
)
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-transition-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_assignment_transition(
    path: Path,
    assignment_id: str,
    target_status: str,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-assignment-transition",
            assignment_id,
            target_status,
            "--db",
            str(path),
            *args,
        ],
        capture_output=True,
        text=True,
    )


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
    *,
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.PENDING,
) -> WorkerAssignment:
    return WorkerAssignment(
        id="wasg_transition_cli",
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


def test_worker_assignment_transition_cli_updates_status_and_audit():
    database = prepare_database()
    database.close()

    result = run_assignment_transition(
        Path(database.path),
        "wasg_transition_cli",
        "assigned",
        "--actor",
        "agent_operator",
        "--reason",
        "operator_ready",
    )

    database = Database(database.path)
    database.initialize()
    stored = WorkerAssignmentRepository(database).get("wasg_transition_cli")
    audits = AuditRepository(database).list()
    assert result.returncode == 0
    assert "Worker Assignment Transitioned" in result.stdout
    assert "Assignment: wasg_transition_cli" in result.stdout
    assert "Previous status: pending" in result.stdout
    assert "Status: assigned" in result.stdout
    assert "Audit: aud_" in result.stdout
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.ASSIGNED
    assert len(audits) == 1
    assert audits[0]["actor"] == "agent_operator"
    assert audits[0]["action"] == "worker_assignment_status_changed"
    assert audits[0]["details"]["old_status"] == "pending"
    assert audits[0]["details"]["new_status"] == "assigned"
    assert audits[0]["details"]["reason"] == "operator_ready"
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_transition_cli_rejects_invalid_transition_without_writes():
    database = prepare_database(status=WorkerAssignmentStatus.ASSIGNED)
    database.close()

    result = run_assignment_transition(
        Path(database.path),
        "wasg_transition_cli",
        "rejected",
        "--actor",
        "agent_operator",
        "--reason",
        "too_late",
    )

    database = Database(database.path)
    database.initialize()
    stored = WorkerAssignmentRepository(database).get("wasg_transition_cli")
    assert result.returncode == 1
    assert "Worker Assignment Transition Rejected" in result.stdout
    assert "status_transition_not_allowed" in result.stdout
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.ASSIGNED
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_transition_cli_rejects_missing_assignment_without_writes():
    path = db_path("missing")

    result = run_assignment_transition(
        path,
        "wasg_missing",
        "cancelled",
        "--actor",
        "agent_operator",
    )

    database = Database(path)
    database.initialize()
    assert result.returncode == 1
    assert "Worker Assignment Transition Rejected" in result.stdout
    assert "assignment_unknown" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    database.close()
