from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from pigenus.storage.database import Database
from pigenus.storage.migrations import MIGRATIONS, MigrationRunner


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase22-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def migration_versions(database: Database) -> list[str]:
    rows = database.fetchall("SELECT version FROM schema_migrations ORDER BY version")
    return [str(row["version"]) for row in rows]


def table_names(database: Database) -> set[str]:
    rows = database.fetchall("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {str(row["name"]) for row in rows}


def column_names(database: Database, table_name: str) -> set[str]:
    rows = database.fetchall(f"PRAGMA table_info({table_name})")
    return {str(row["name"]) for row in rows}


def test_initialize_creates_schema_migrations_and_runtime_tables():
    database = Database(db_path("fresh"))
    database.initialize()

    assert "schema_migrations" in table_names(database)
    assert "memory_objects" in table_names(database)
    assert "decision_logs" in table_names(database)
    assert {"status", "fitness", "created_at", "last_used_at"} <= column_names(database, "cells")
    assert migration_versions(database) == [migration.version for migration in MIGRATIONS]
    database.close()


def test_initialize_is_idempotent():
    database = Database(db_path("idempotent"))
    database.initialize()
    first_versions = migration_versions(database)

    database.initialize()

    assert migration_versions(database) == first_versions
    assert len(migration_versions(database)) == len(MIGRATIONS)
    database.close()


def test_runner_records_initial_schema_for_existing_database():
    path = db_path("existing")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE memory_objects (
            memory_id TEXT PRIMARY KEY,
            memory_type TEXT NOT NULL,
            context TEXT NOT NULL,
            status TEXT NOT NULL,
            content TEXT NOT NULL,
            human_summary TEXT NOT NULL,
            importance REAL NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            last_used_at TEXT,
            last_validated_at TEXT,
            review_due_at TEXT,
            expires_at TEXT,
            data TEXT NOT NULL
        )
        """
    )
    connection.commit()

    applied = MigrationRunner(connection).apply()
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()

    assert applied == [migration.version for migration in MIGRATIONS]
    assert [str(row["version"]) for row in rows] == [migration.version for migration in MIGRATIONS]
    connection.close()
