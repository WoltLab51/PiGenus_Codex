from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.systemform import (
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, WorkerRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-cli-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_worker_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def run_worker_show(path: Path, worker_id: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "worker-show",
            worker_id,
            "--db",
            str(path),
        ],
        capture_output=True,
        text=True,
    )


def worker_profile(
    worker_id: str,
    *,
    worker_type: WorkerType = WorkerType.LOCAL_PROCESS,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    owner_actor_id: str = "human_ronny",
    home_room_id: str = "room_developer",
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=worker_type,
        display_name=f"{worker_id} display",
        status=status,
        owner_actor_id=owner_actor_id,
        home_room_id=home_room_id,
        supported_runtimes=["python"],
        available_cells=["meaning_ingester"],
        created_at=datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc),
    )


def seed_workers(path: Path) -> None:
    database = Database(path)
    database.initialize()
    repository = WorkerRepository(database)
    repository.add_profile(worker_profile("worker_active"))
    repository.add_profile(
        worker_profile(
            "worker_server",
            worker_type=WorkerType.SERVER,
            owner_actor_id="human_anna",
            home_room_id="room_family",
        )
    )
    repository.add_profile(worker_profile("worker_suspended", status=WorkerStatus.SUSPENDED))
    repository.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_active", status=WorkerStatus.ACTIVE)
    )
    repository.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_server", status=WorkerStatus.DEGRADED)
    )
    repository.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_suspended", status=WorkerStatus.ACTIVE)
    )
    database.close()


def test_worker_list_reports_empty_database():
    path = db_path("empty")

    result = run_worker_list(path)

    assert result.returncode == 0
    assert "No workers found." in result.stdout


def test_worker_list_prints_rows_without_modifying_data():
    path = db_path("rows")
    seed_workers(path)

    result = run_worker_list(path, "--considerable", "yes")

    database = Database(path)
    database.initialize()
    assert "worker_active | local_process | active | heartbeat=active" in result.stdout
    assert "considerable=yes" in result.stdout
    assert "worker_server" not in result.stdout
    assert WorkerRepository(database).count_profiles() == 3
    assert WorkerRepository(database).count_heartbeats() == 3
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_list_filters_by_status_type_owner_and_room():
    path = db_path("filters")
    seed_workers(path)

    result = run_worker_list(
        path,
        "--status",
        "active",
        "--type",
        "server",
        "--owner",
        "human_anna",
        "--room",
        "room_family",
    )

    assert "worker_server | server | active | heartbeat=degraded" in result.stdout
    assert "considerable=no" in result.stdout
    assert "worker_active" not in result.stdout
    assert "worker_suspended" not in result.stdout


def test_worker_show_prints_one_worker_as_stable_json():
    path = db_path("show")
    seed_workers(path)

    result = run_worker_show(path, "worker_active")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["profile"]["id"] == "worker_active"
    assert payload["profile"]["worker_type"] == "local_process"
    assert payload["heartbeat"]["status"] == "active"
    assert payload["considerable"] is True


def test_worker_show_returns_clean_error_for_unknown_id():
    result = run_worker_show(db_path("missing-show"), "missing_worker")

    assert result.returncode == 1
    assert "Worker not found: missing_worker" in result.stdout
    assert result.stderr == ""
