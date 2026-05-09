from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from pigenus.storage.migrations import MigrationRunner


class Database:
    """Small SQLite connection wrapper for the PiGenus runtime."""

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
        MigrationRunner(self.connection).apply()

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
