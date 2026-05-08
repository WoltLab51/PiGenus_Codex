from __future__ import annotations

import json
from typing import Any

from pigenus.schemas.base import new_id, utc_now
from pigenus.schemas.cells import CellSpec, CellState
from pigenus.schemas.events import Event
from pigenus.schemas.memory import MemoryObject
from pigenus.storage.database import Database


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


class EventRepository:
    """Persistence adapter for structured events."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, event: Event) -> None:
        data = event.model_dump(mode="json")
        self.database.execute(
            """
            INSERT INTO events (
                event_id, object_type, schema_version, context, created_at,
                created_by_cell, payload, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.object_type,
                event.schema_version,
                _json(data["context"]),
                str(data["created_at"]),
                event.created_by_cell,
                _json(data["payload"]),
                _json(data),
            ),
        )

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM events")
        return int(row["count"]) if row else 0

    def list(self) -> list[Event]:
        rows = self.database.fetchall("SELECT data FROM events ORDER BY created_at, event_id")
        return [Event.model_validate(json.loads(row["data"])) for row in rows]


class MemoryRepository:
    """Persistence adapter for memory objects."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, memory: MemoryObject) -> None:
        data = memory.model_dump(mode="json")
        self.database.execute(
            """
            INSERT INTO memory_objects (
                memory_id, memory_type, context, status, content, human_summary,
                importance, confidence, created_at, last_used_at, last_validated_at,
                review_due_at, expires_at, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.memory_id,
                memory.memory_type,
                _json(data["context"]),
                memory.status,
                _json(data["content"]),
                memory.human_summary,
                memory.importance,
                memory.confidence,
                str(data["created_at"]),
                data["last_used_at"],
                data["last_validated_at"],
                data["review_due_at"],
                data["expires_at"],
                _json(data),
            ),
        )

    def get(self, memory_id: str) -> MemoryObject | None:
        row = self.database.fetchone("SELECT data FROM memory_objects WHERE memory_id = ?", (memory_id,))
        if row is None:
            return None
        return MemoryObject.model_validate(json.loads(row["data"]))

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM memory_objects")
        return int(row["count"]) if row else 0


class CellRepository:
    """Persistence adapter for cell specs."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, spec: CellSpec) -> None:
        data = spec.model_dump(mode="json")
        self.database.execute(
            """
            INSERT OR REPLACE INTO cells (
                cell_id, name, version, input_event_types, output_event_types,
                permissions, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec.cell_id,
                spec.name,
                spec.version,
                _json(spec.input_event_types),
                _json(spec.output_event_types),
                _json(spec.permissions),
                _json(data),
            ),
        )

    def get(self, cell_id: str) -> CellSpec | None:
        row = self.database.fetchone("SELECT data FROM cells WHERE cell_id = ?", (cell_id,))
        if row is None:
            return None
        return CellSpec.model_validate(json.loads(row["data"]))

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM cells")
        return int(row["count"]) if row else 0


class CellStateRepository:
    """Persistence adapter for operational cell state."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def set(self, state: CellState) -> None:
        data = state.model_dump(mode="json")
        self.database.execute(
            """
            INSERT OR REPLACE INTO cell_states (
                cell_id, updated_at, state, data
            ) VALUES (?, ?, ?, ?)
            """,
            (
                state.cell_id,
                str(data["updated_at"]),
                _json(data["state"]),
                _json(data),
            ),
        )

    def get(self, cell_id: str) -> CellState | None:
        row = self.database.fetchone("SELECT data FROM cell_states WHERE cell_id = ?", (cell_id,))
        if row is None:
            return None
        return CellState.model_validate(json.loads(row["data"]))

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM cell_states")
        return int(row["count"]) if row else 0


class AuditRepository:
    """Persistence adapter for audit log rows."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(
        self,
        *,
        actor: str,
        action: str,
        context: dict[str, Any],
        details: dict[str, Any],
    ) -> str:
        audit_id = new_id("aud")
        created_at = utc_now().isoformat()
        self.database.execute(
            """
            INSERT INTO audit_logs (
                audit_id, created_at, actor, action, context, details
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (audit_id, created_at, actor, action, _json(context), _json(details)),
        )
        return audit_id

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM audit_logs")
        return int(row["count"]) if row else 0
