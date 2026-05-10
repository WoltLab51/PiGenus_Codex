from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class SnapshotBackupResult:
    """Result of a local SQLite runtime snapshot."""

    source_path: Path
    backup_path: Path
    size_bytes: int
    integrity_check: str
    created_at: datetime


class SnapshotBackupService:
    """Creates boring, local SQLite snapshots without migrating or repairing storage."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def create(
        self,
        *,
        output_dir: str | Path = "backups",
        name: str | None = None,
        created_at: datetime | None = None,
    ) -> SnapshotBackupResult:
        source_path = self.db_path
        if not source_path.exists():
            raise FileNotFoundError(f"database_missing: {source_path}")

        timestamp = created_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        backup_name = name or self._default_name(source_path, timestamp)
        backup_path = target_dir / backup_name
        if backup_path.exists():
            raise FileExistsError(f"backup_exists: {backup_path}")

        source_uri = source_path.resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(source_uri, uri=True) as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)

        integrity_check = self._integrity_check(backup_path)
        if integrity_check != "ok":
            raise RuntimeError(f"backup_integrity_failed: {integrity_check}")

        return SnapshotBackupResult(
            source_path=source_path,
            backup_path=backup_path,
            size_bytes=backup_path.stat().st_size,
            integrity_check=integrity_check,
            created_at=timestamp.astimezone(timezone.utc),
        )

    @staticmethod
    def _default_name(source_path: Path, created_at: datetime) -> str:
        stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", source_path.stem).strip("-") or "pigenus"
        stamp = created_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{stem}-snapshot-{stamp}.sqlite3"

    @staticmethod
    def _integrity_check(path: Path) -> str:
        with sqlite3.connect(path) as connection:
            row = connection.execute("PRAGMA integrity_check").fetchone()
        return str(row[0]) if row else "missing_integrity_result"
