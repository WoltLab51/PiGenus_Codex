from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
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
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerHeartbeat,
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
    root = Path(".testdata") / "worker-assignment-scheduling-eligibility-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_assignment_scheduling_eligibility(
    path: Path,
    assignment_id: str,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "pigenus.cli.main",
        "worker-assignment-scheduling-eligibility",
        assignment_id,
        "--db",
        str(path),
    ]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
    )


def worker_profile(
    worker_id: str = "worker_local",
    *,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    network_access: bool = True,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=status,
        home_room_id="room_developer",
        available_cells=["meaning_ingester"],
        supported_runtimes=["python"],
        max_sensitivity=Sensitivity.PRIVATE,
        network_access=network_access,
    )


def assignment(
    decision_id: str,
    *,
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.ASSIGNED,
) -> WorkerAssignment:
    return WorkerAssignment(
        id="wasg_eligibility_cli",
        worker_id="worker_local",
        capability="meaning_ingester",
        room_id="room_developer",
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
    assignment_status: WorkerAssignmentStatus = WorkerAssignmentStatus.ASSIGNED,
) -> Database:
    database = Database(db_path(assignment_status.value))
    database.initialize()
    workers = WorkerRepository(database)
    workers.add_profile(worker_profile())
    workers.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.ACTIVE)
    )
    decision = log_preflight_decision(database)
    WorkerAssignmentRepository(database).add(
        assignment(decision.decision_id, status=assignment_status)
    )
    return database


def log_preflight_decision(database: Database):
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
    return WorkerExecutionPreflightLogger(DecisionRepository(database)).add(
        result,
        actor_id="agent_preflight",
        room_id="room_developer",
        event_id="evt_preflight",
    )


def test_worker_assignment_scheduling_eligibility_cli_allows_without_writes():
    database = prepare_database()
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(path, "wasg_eligibility_cli")

    database = Database(path)
    database.initialize()
    assert result.returncode == 0
    assert "Worker Assignment Scheduling Eligibility" in result.stdout
    assert "Assignment: wasg_eligibility_cli" in result.stdout
    assert "Outcome: allow_scheduling" in result.stdout
    assert "Eligible: yes" in result.stdout
    assert "Reasons: assignment_scheduling_eligible" in result.stdout
    assert "Worker: worker_local" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_reports_not_considered():
    database = prepare_database(assignment_status=WorkerAssignmentStatus.PENDING)
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(path, "wasg_eligibility_cli")

    database = Database(path)
    database.initialize()
    stored = WorkerAssignmentRepository(database).get("wasg_eligibility_cli")
    assert result.returncode == 0
    assert "Outcome: not_considered" in result.stdout
    assert "Eligible: no" in result.stdout
    assert "Reasons: assignment_status_not_assigned" in result.stdout
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.PENDING
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_reports_review_without_writes():
    database = prepare_database()
    WorkerRepository(database).record_heartbeat(
        WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.DEGRADED)
    )
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(path, "wasg_eligibility_cli")

    database = Database(path)
    database.initialize()
    assert result.returncode == 0
    assert "Outcome: require_review" in result.stdout
    assert "Eligible: no" in result.stdout
    assert "Reasons: worker_degraded" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_reports_missing_assignment():
    path = db_path("missing")

    result = run_assignment_scheduling_eligibility(path, "wasg_missing")

    database = Database(path)
    database.initialize()
    assert result.returncode == 0
    assert "Outcome: not_considered" in result.stdout
    assert "Reasons: assignment_unknown" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_logs_allow_decision():
    database = prepare_database()
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(
        path,
        "wasg_eligibility_cli",
        ["--log", "--actor", "operator_cli", "--event-id", "evt_eligibility"],
    )

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()
    assert result.returncode == 0
    assert "Outcome: allow_scheduling" in result.stdout
    assert "Logged decision: dec_" in result.stdout
    assert len(decisions) == 2
    logged = decisions[-1]
    assert logged.subject_id == "wasg_eligibility_cli"
    assert logged.actor == "operator_cli"
    assert logged.source == "worker_assignment_scheduling_eligibility"
    assert logged.details["decision"] == "allow"
    assert logged.details["family"] == "worker_assignment_scheduling_eligibility"
    assert logged.details["room_id"] == "room_developer"
    assert WorkerAssignmentRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_logs_deny_decision():
    database = prepare_database()
    WorkerRepository(database).add_profile(worker_profile(network_access=False))
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(
        path,
        "wasg_eligibility_cli",
        ["--log"],
    )

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()
    assert result.returncode == 0
    assert "Outcome: deny_scheduling" in result.stdout
    assert "Reasons: network_not_allowed" in result.stdout
    assert "Logged decision: dec_" in result.stdout
    assert len(decisions) == 2
    logged = decisions[-1]
    assert logged.source == "worker_assignment_scheduling_eligibility"
    assert logged.details["decision"] == "block"
    assert logged.details["family"] == "worker_assignment_scheduling_eligibility"
    assert WorkerAssignmentRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_logs_review_decision():
    database = prepare_database()
    WorkerRepository(database).record_heartbeat(
        WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.DEGRADED)
    )
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(
        path,
        "wasg_eligibility_cli",
        ["--log"],
    )

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()
    assert result.returncode == 0
    assert "Outcome: require_review" in result.stdout
    assert "Logged decision: dec_" in result.stdout
    assert len(decisions) == 2
    logged = decisions[-1]
    assert logged.source == "worker_assignment_scheduling_eligibility"
    assert logged.details["decision"] == "escalate"
    assert logged.details["requires_human"] is True
    assert WorkerAssignmentRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_skips_not_considered_log():
    database = prepare_database(assignment_status=WorkerAssignmentStatus.PENDING)
    path = Path(database.path)
    database.close()

    result = run_assignment_scheduling_eligibility(
        path,
        "wasg_eligibility_cli",
        ["--log"],
    )

    database = Database(path)
    database.initialize()
    stored = WorkerAssignmentRepository(database).get("wasg_eligibility_cli")
    assert result.returncode == 0
    assert "Outcome: not_considered" in result.stdout
    assert "Logged decision: skipped" in result.stdout
    assert stored is not None
    assert stored.status == WorkerAssignmentStatus.PENDING
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_cli_skips_missing_assignment_log():
    path = db_path("missing-log")

    result = run_assignment_scheduling_eligibility(
        path,
        "wasg_missing",
        ["--log"],
    )

    database = Database(path)
    database.initialize()
    assert result.returncode == 0
    assert "Outcome: not_considered" in result.stdout
    assert "Reasons: assignment_unknown" in result.stdout
    assert "Logged decision: skipped" in result.stdout
    assert WorkerAssignmentRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()
