from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.health import HealthChecker
from pigenus.storage.database import Database


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase211-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_health_check(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "health-check",
            "--db",
            str(path),
        ],
        capture_output=True,
        text=True,
    )


def test_health_checker_reports_initialized_database_as_healthy():
    path = db_path("healthy")
    database = Database(path)
    database.initialize()
    database.close()

    result = HealthChecker(path).check()

    assert result.ok is True
    assert "required_tables_present" in result.checks
    assert "migrations_current" in result.checks
    assert result.failures == ()


def test_health_check_cli_returns_zero_for_healthy_database():
    path = db_path("healthy-cli")
    database = Database(path)
    database.initialize()
    database.close()

    result = run_health_check(path)

    assert result.returncode == 0
    assert "OK: required_tables_present" in result.stdout
    assert "OK: migrations_current" in result.stdout
    assert "Status: healthy" in result.stdout


def test_health_check_cli_returns_nonzero_for_missing_database_without_creating_it():
    path = db_path("missing")

    result = run_health_check(path)

    assert result.returncode == 1
    assert "FAIL: database_missing:" in result.stdout
    assert "Status: unhealthy" in result.stdout
    assert not path.exists()


def test_health_check_cli_returns_nonzero_for_missing_tables():
    path = db_path("missing-tables")
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

    result = run_health_check(path)

    assert result.returncode == 1
    assert "FAIL: missing_tables:" in result.stdout
    assert "events" in result.stdout


def test_health_check_cli_returns_nonzero_for_missing_migrations():
    path = db_path("missing-migrations")
    database = Database(path)
    database.initialize()
    database.execute("DELETE FROM schema_migrations WHERE version = ?", ("0003_cell_lifecycle",))
    database.close()

    result = run_health_check(path)

    assert result.returncode == 1
    assert "FAIL: missing_migrations: 0003_cell_lifecycle" in result.stdout
    assert "Status: unhealthy" in result.stdout
