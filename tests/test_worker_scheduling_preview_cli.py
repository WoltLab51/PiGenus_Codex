from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, DecisionRepository, WorkerRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-scheduling-preview-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_preview(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-scheduling-preview",
            "meaning_ingester",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def worker_profile(
    worker_id: str,
    *,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    cells: list[str] | None = None,
    runtimes: list[str] | None = None,
    max_sensitivity: Sensitivity = Sensitivity.PRIVATE,
    network_access: bool = False,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=status,
        available_cells=cells or ["meaning_ingester"],
        supported_runtimes=runtimes or ["python"],
        max_sensitivity=max_sensitivity,
        network_access=network_access,
        created_at=datetime(2026, 5, 15, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 15, 8, 0, tzinfo=timezone.utc),
    )


def seed_workers(path: Path) -> None:
    database = Database(path)
    database.initialize()
    repository = WorkerRepository(database)
    repository.add_profile(worker_profile("worker_active"))
    repository.add_profile(worker_profile("worker_network", network_access=True))
    repository.add_profile(worker_profile("worker_missing_capability", cells=["log_reader"]))
    repository.add_profile(worker_profile("worker_missing_runtime", runtimes=["node"]))
    repository.add_profile(worker_profile("worker_no_heartbeat"))
    for worker_id in (
        "worker_active",
        "worker_network",
        "worker_missing_capability",
        "worker_missing_runtime",
    ):
        repository.record_heartbeat(
            WorkerHeartbeat(worker_id=worker_id, status=WorkerStatus.ACTIVE)
        )
    database.close()


def test_worker_scheduling_preview_cli_reports_empty_database():
    result = run_preview(db_path("empty"))

    assert "Worker Scheduling Preview" in result.stdout
    assert "Decision: block" in result.stdout
    assert "Reason: no_suitable_worker" in result.stdout
    assert "Recommended worker: -" in result.stdout
    assert "Candidates:\n-" in result.stdout


def test_worker_scheduling_preview_cli_prints_candidate_reasons_without_mutating_storage():
    path = db_path("rows")
    seed_workers(path)

    result = run_preview(path, "--runtime", "python")

    database = Database(path)
    database.initialize()
    assert "Decision: allow" in result.stdout
    assert "Recommended worker: worker_active" in result.stdout
    assert "worker_active | suitable=yes | reasons=preview_suitable" in result.stdout
    assert "worker_missing_capability | suitable=no | reasons=capability_missing" in result.stdout
    assert WorkerRepository(database).count_profiles() == 5
    assert WorkerRepository(database).count_heartbeats() == 4
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_scheduling_preview_cli_logs_decision_only_with_explicit_flag():
    path = db_path("log")
    seed_workers(path)

    result = run_preview(
        path,
        "--runtime",
        "python",
        "--log",
        "--actor",
        "agent_preview",
        "--room",
        "room_private",
        "--event-id",
        "evt_worker_preview",
    )

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()
    assert "Logged decision: dec_" in result.stdout
    assert len(decisions) == 1
    assert decisions[0].decision_type == "governance_decision"
    assert decisions[0].source == "worker_scheduling_preview"
    assert decisions[0].subject_id == "evt_worker_preview"
    assert decisions[0].actor == "agent_preview"
    assert decisions[0].context == {"name": "private/default"}
    assert decisions[0].details["decision"] == "allow"
    assert decisions[0].details["family"] == "worker_scheduling"
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_scheduling_preview_cli_applies_runtime_sensitivity_and_network_constraints():
    path = db_path("constraints")
    seed_workers(path)

    result = run_preview(
        path,
        "--runtime",
        "python",
        "--sensitivity",
        "financial",
        "--network-required",
    )

    assert "Decision: block" in result.stdout
    assert (
        "worker_active | suitable=no | "
        "reasons=sensitivity_exceeds_worker_limit,network_unavailable"
    ) in result.stdout
    assert (
        "worker_network | suitable=no | reasons=sensitivity_exceeds_worker_limit"
    ) in result.stdout
