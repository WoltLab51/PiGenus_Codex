from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.worker_execution_preflight import (
    WorkerExecutionPreflightLogger,
    WorkerExecutionPreflightRequest,
    WorkerExecutionPreflightService,
)
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, DecisionRepository, WorkerRepository
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-create-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_assignment_create(
    path: Path,
    worker_id: str,
    capability: str,
    decision_id: str,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-assignment-create",
            worker_id,
            capability,
            decision_id,
            "--db",
            str(path),
            *args,
        ],
        capture_output=True,
        text=True,
    )


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


def prepare_database(
    *,
    cells: list[str] | None = None,
    network_access: bool = True,
) -> Database:
    database = Database(db_path("create"))
    database.initialize()
    workers = WorkerRepository(database)
    workers.add_profile(
        worker_profile(
            "worker_local",
            cells=cells,
            network_access=network_access,
        )
    )
    workers.record_heartbeat(WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.ACTIVE))
    return database


def log_preflight_decision(database: Database) -> str:
    registry = WorkerRegistry()
    workers = WorkerRepository(database)
    for profile in workers.list_profiles():
        registry.register(profile)
    for heartbeat in workers.list_heartbeats():
        registry.record_heartbeat(heartbeat)
    result = WorkerExecutionPreflightService(WorkerInspectionService(registry)).check(
        WorkerExecutionPreflightRequest(
            worker_id="worker_local",
            capability="meaning_ingester",
            required_runtime="python",
            sensitivity=Sensitivity.PRIVATE,
            network_required=True,
        )
    )
    record = WorkerExecutionPreflightLogger(DecisionRepository(database)).add(
        result,
        actor_id="agent_preflight",
        room_id="room_developer",
        event_id="evt_preflight",
    )
    return record.decision_id


def test_worker_assignment_create_cli_writes_pending_assignment_and_audit():
    database = prepare_database()
    decision_id = log_preflight_decision(database)
    database.close()

    result = run_assignment_create(
        Path(database.path),
        "worker_local",
        "meaning_ingester",
        decision_id,
        "--assignment-id",
        "wasg_cli",
        "--room",
        "room_developer",
        "--actor",
        "agent_scheduler_preview",
        "--runtime",
        "python",
        "--sensitivity",
        "private",
        "--network-required",
    )

    database = Database(database.path)
    database.initialize()
    assignments = WorkerAssignmentRepository(database).list()
    audits = AuditRepository(database).list()
    assert result.returncode == 0
    assert "Worker Assignment Created" in result.stdout
    assert "Assignment: wasg_cli" in result.stdout
    assert "Audit: aud_" in result.stdout
    assert len(assignments) == 1
    assert assignments[0].id == "wasg_cli"
    assert assignments[0].status.value == "pending"
    assert len(audits) == 1
    assert audits[0]["action"] == "worker_assignment_created"
    assert audits[0]["details"]["assignment_id"] == "wasg_cli"
    assert DecisionRepository(database).count() == 1
    database.close()


def test_worker_assignment_create_cli_rejects_invalid_evidence_without_writes():
    database = prepare_database(cells=["log_reader"])
    decision_id = log_preflight_decision(database)
    database.close()

    result = run_assignment_create(
        Path(database.path),
        "worker_local",
        "meaning_ingester",
        decision_id,
        "--assignment-id",
        "wasg_rejected",
        "--room",
        "room_developer",
        "--actor",
        "agent_scheduler_preview",
        "--runtime",
        "python",
        "--sensitivity",
        "private",
        "--network-required",
    )

    database = Database(database.path)
    database.initialize()
    assert result.returncode == 1
    assert "Worker Assignment Rejected" in result.stdout
    assert "evidence_decision_not_allow" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 1
    database.close()
