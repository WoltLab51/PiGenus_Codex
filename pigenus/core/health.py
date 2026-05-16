from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from pigenus.storage.migrations import MIGRATIONS


REQUIRED_TABLES: tuple[str, ...] = (
    "schema_migrations",
    "events",
    "memory_objects",
    "cells",
    "cell_states",
    "audit_logs",
    "decision_logs",
    "meaning_objects",
    "worker_profiles",
    "worker_heartbeats",
    "worker_assignments",
)


@dataclass(frozen=True)
class HealthCheckResult:
    """Read-only health-check result for local runtime storage."""

    ok: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...]


class HealthChecker:
    """Checks local SQLite structure without applying repairs or migrations."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def check(self) -> HealthCheckResult:
        checks: list[str] = []
        failures: list[str] = []

        if not self.db_path.exists():
            return HealthCheckResult(
                ok=False,
                checks=(),
                failures=(f"database_missing: {self.db_path}",),
            )

        try:
            connection = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            connection.row_factory = sqlite3.Row
        except sqlite3.Error as exc:
            return HealthCheckResult(
                ok=False,
                checks=(),
                failures=(f"database_open_failed: {exc}",),
            )

        try:
            table_names = self._table_names(connection)
            missing_tables = sorted(set(REQUIRED_TABLES).difference(table_names))
            if missing_tables:
                failures.append(f"missing_tables: {', '.join(missing_tables)}")
            else:
                checks.append("required_tables_present")

            if "schema_migrations" in table_names:
                applied_versions = self._applied_versions(connection)
                expected_versions = {migration.version for migration in MIGRATIONS}
                missing_versions = sorted(expected_versions.difference(applied_versions))
                extra_versions = sorted(applied_versions.difference(expected_versions))
                if missing_versions:
                    failures.append(f"missing_migrations: {', '.join(missing_versions)}")
                if extra_versions:
                    failures.append(f"unknown_migrations: {', '.join(extra_versions)}")
                if not missing_versions and not extra_versions:
                    checks.append("migrations_current")
        except sqlite3.Error as exc:
            failures.append(f"health_check_failed: {exc}")
        finally:
            connection.close()

        return HealthCheckResult(
            ok=not failures,
            checks=tuple(checks),
            failures=tuple(failures),
        )

    @staticmethod
    def _table_names(connection: sqlite3.Connection) -> set[str]:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        return {str(row["name"]) for row in rows}

    @staticmethod
    def _applied_versions(connection: sqlite3.Connection) -> set[str]:
        rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
        return {str(row["version"]) for row in rows}
