from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
from sqlite3 import Connection

from pigenus.schemas.base import utc_now


@dataclass(frozen=True)
class Migration:
    """A forward-only SQLite schema migration."""

    version: str
    sql: str


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version="0001_initial_schema",
        sql="""
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
        """,
    ),
    Migration(
        version="0002_decision_logs",
        sql="""
        CREATE TABLE IF NOT EXISTS decision_logs (
            decision_id TEXT PRIMARY KEY,
            decision_type TEXT NOT NULL,
            context TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            actor TEXT NOT NULL,
            reason TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL,
            details TEXT NOT NULL,
            data TEXT NOT NULL
        );
        """,
    ),
    Migration(
        version="0003_cell_lifecycle",
        sql="""
        ALTER TABLE cells ADD COLUMN status TEXT NOT NULL DEFAULT 'active';
        ALTER TABLE cells ADD COLUMN fitness REAL NOT NULL DEFAULT 0.0;
        ALTER TABLE cells ADD COLUMN created_at TEXT;
        ALTER TABLE cells ADD COLUMN last_used_at TEXT;
        """,
    ),
    Migration(
        version="0004_meaning_objects",
        sql="""
        CREATE TABLE IF NOT EXISTS meaning_objects (
            meaning_id TEXT PRIMARY KEY,
            meaning_type TEXT NOT NULL,
            room_id TEXT NOT NULL,
            truth_status TEXT NOT NULL,
            sensitivity TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            data TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_meaning_objects_room_id
            ON meaning_objects(room_id);
        CREATE INDEX IF NOT EXISTS idx_meaning_objects_type
            ON meaning_objects(meaning_type);
        CREATE INDEX IF NOT EXISTS idx_meaning_objects_truth_status
            ON meaning_objects(truth_status);
        CREATE INDEX IF NOT EXISTS idx_meaning_objects_sensitivity
            ON meaning_objects(sensitivity);
        """,
    ),
)


class MigrationRunner:
    """Applies recorded SQLite migrations once."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def initialize(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def applied_versions(self) -> set[str]:
        self.initialize()
        rows = self.connection.execute("SELECT version FROM schema_migrations").fetchall()
        return {str(row["version"]) for row in rows}

    def apply(self) -> list[str]:
        self.initialize()
        applied = self.applied_versions()
        newly_applied: list[str] = []

        for migration in MIGRATIONS:
            if migration.version in applied:
                continue
            with self.connection:
                self.connection.executescript(migration.sql)
                self.connection.execute(
                    """
                    INSERT INTO schema_migrations (version, applied_at)
                    VALUES (?, ?)
                    """,
                    (
                        migration.version,
                        utc_now().astimezone(timezone.utc).isoformat(),
                    ),
                )
            newly_applied.append(migration.version)
        return newly_applied
