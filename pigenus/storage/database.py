from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class Database:
    """Small SQLite connection wrapper for the Phase 1 runtime."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            if self.path != ":memory:":
                Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def initialize(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                object_type TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                context TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by_cell TEXT NOT NULL,
                payload TEXT NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS memory_objects (
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
            );

            CREATE TABLE IF NOT EXISTS cells (
                cell_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                input_event_types TEXT NOT NULL,
                output_event_types TEXT NOT NULL,
                permissions TEXT NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cell_states (
                cell_id TEXT PRIMARY KEY,
                updated_at TEXT NOT NULL,
                state TEXT NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                context TEXT NOT NULL,
                details TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def execute(self, sql: str, parameters: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        cursor = self.connection.execute(sql, parameters)
        self.connection.commit()
        return cursor

    def fetchone(self, sql: str, parameters: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        return self.connection.execute(sql, parameters).fetchone()

    def fetchall(self, sql: str, parameters: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        return list(self.connection.execute(sql, parameters).fetchall())

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
