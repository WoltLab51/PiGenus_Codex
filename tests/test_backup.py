from __future__ import annotations

import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from pigenus.core.backup import SnapshotBackupService
from pigenus.schemas.events import Event
from pigenus.storage.database import Database
from pigenus.storage.repositories import EventRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "backup-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def output_dir(name: str) -> Path:
    root = Path(".testdata") / "backup-tests" / f"{name}-{uuid4().hex}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_backup_create(path: Path, target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "backup-create",
            "--db",
            str(path),
            "--output-dir",
            str(target),
            "--name",
            "manual-snapshot.sqlite3",
        ],
        capture_output=True,
        text=True,
    )


def populate_database(path: Path) -> None:
    database = Database(path)
    database.initialize()
    EventRepository(database).add(
        Event(
            object_type="TaskRequest",
            context={"name": "developer/default"},
            created_by_cell="input_cell@0.1.0",
            payload={
                "raw_text": "Merke dir: PiGenus ist der Zellkern.",
                "action": "memory_write",
            },
        )
    )
    database.close()


def event_count(path: Path) -> int:
    with sqlite3.connect(path) as connection:
        row = connection.execute("SELECT COUNT(*) FROM events").fetchone()
    return int(row[0])


def test_snapshot_backup_creates_consistent_sqlite_copy():
    path = db_path("source")
    target = output_dir("target")
    populate_database(path)

    result = SnapshotBackupService(path).create(
        output_dir=target,
        created_at=datetime(2026, 5, 10, 22, 30, tzinfo=timezone.utc),
    )

    assert result.backup_path == target / f"{path.stem}-snapshot-20260510T223000Z.sqlite3"
    assert result.size_bytes > 0
    assert result.integrity_check == "ok"
    assert event_count(result.backup_path) == 1


def test_snapshot_backup_does_not_create_missing_source_database():
    path = db_path("missing")
    target = output_dir("missing-target")

    with pytest.raises(FileNotFoundError, match="database_missing"):
        SnapshotBackupService(path).create(output_dir=target)

    assert not path.exists()
    assert list(target.iterdir()) == []


def test_snapshot_backup_refuses_to_overwrite_existing_backup():
    path = db_path("overwrite")
    target = output_dir("overwrite-target")
    populate_database(path)
    existing = target / "snapshot.sqlite3"
    existing.write_text("already here", encoding="utf-8")

    with pytest.raises(FileExistsError, match="backup_exists"):
        SnapshotBackupService(path).create(output_dir=target, name="snapshot.sqlite3")

    assert existing.read_text(encoding="utf-8") == "already here"


def test_backup_create_cli_writes_snapshot_and_reports_integrity():
    path = db_path("cli")
    target = output_dir("cli-target")
    populate_database(path)

    result = run_backup_create(path, target)

    backup = target / "manual-snapshot.sqlite3"
    assert result.returncode == 0
    assert "PiGenus Backup" in result.stdout
    assert f"Backup: {backup}" in result.stdout
    assert "Integrity: ok" in result.stdout
    assert event_count(backup) == 1


def test_backup_create_cli_returns_nonzero_for_missing_database():
    path = db_path("cli-missing")
    target = output_dir("cli-missing-target")

    result = run_backup_create(path, target)

    assert result.returncode == 1
    assert "Backup failed: database_missing:" in result.stdout
    assert not path.exists()
