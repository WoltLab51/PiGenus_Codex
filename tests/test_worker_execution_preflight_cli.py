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
    root = Path(".testdata") / "worker-execution-preflight-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_preflight(path: Path, worker_id: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-execution-preflight",
            worker_id,
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
    repository.add_profile(worker_profile("worker_active", network_access=True))
    repository.add_profile(worker_profile("worker_missing_capability", cells=["log_reader"]))
    repository.add_profile(worker_profile("worker_no_heartbeat"))
    repository.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_active", status=WorkerStatus.ACTIVE)
    )
    repository.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_missing_capability", status=WorkerStatus.ACTIVE)
    )
    database.close()


def test_worker_execution_preflight_cli_allows_suitable_worker_without_mutating_storage():
    path = db_path("allow")
    seed_workers(path)

    result = run_preflight(
        path,
        "worker_active",
        "--runtime",
        "python",
        "--sensitivity",
        "private",
        "--network-required",
    )

    database = Database(path)
    database.initialize()
    assert "Worker Execution Preflight" in result.stdout
    assert "Decision: allow" in result.stdout
    assert "Reason: worker_execution_preflight_passed" in result.stdout
    assert "network_allowed | decision=allow | reason=network_available" in result.stdout
    assert WorkerRepository(database).count_profiles() == 3
    assert WorkerRepository(database).count_heartbeats() == 2
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_execution_preflight_cli_blocks_unknown_worker():
    result = run_preflight(db_path("missing"), "missing_worker")

    assert "Decision: block" in result.stdout
    assert "Reason: worker_unknown" in result.stdout
    assert "worker_known | decision=block | reason=worker_unknown" in result.stdout


def test_worker_execution_preflight_cli_prints_ordered_block_checks():
    path = db_path("block")
    seed_workers(path)

    result = run_preflight(
        path,
        "worker_missing_capability",
        "--runtime",
        "node",
        "--sensitivity",
        "secret",
        "--network-required",
    )

    assert "Decision: block" in result.stdout
    assert "Reason: capability_missing" in result.stdout
    assert "worker_considerable | decision=allow | reason=worker_considerable" in result.stdout
    assert "capability_available | decision=block | reason=capability_missing" in result.stdout
    assert "runtime_supported | decision=block | reason=runtime_missing" in result.stdout
