from __future__ import annotations

import json
from typing import Any

from pigenus.schemas.base import new_id, utc_now
from pigenus.schemas.cells import CellSpec, CellState
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.events import Event
from pigenus.schemas.memory import MemoryObject, MemoryStatus
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

    def list(self) -> list[MemoryObject]:
        rows = self.database.fetchall("SELECT data FROM memory_objects ORDER BY created_at, memory_id")
        return [MemoryObject.model_validate(json.loads(row["data"])) for row in rows]

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM memory_objects")
        return int(row["count"]) if row else 0

    def list_due_for_lifecycle(self, now: str) -> list[MemoryObject]:
        rows = self.database.fetchall(
            """
            SELECT data FROM memory_objects
            WHERE (review_due_at IS NOT NULL AND review_due_at <= ?)
               OR (expires_at IS NOT NULL AND expires_at <= ?)
            ORDER BY created_at, memory_id
            """,
            (now, now),
        )
        return [MemoryObject.model_validate(json.loads(row["data"])) for row in rows]

    def update_lifecycle(
        self,
        memory: MemoryObject,
        *,
        status: MemoryStatus,
        last_validated_at: str | None = None,
        last_used_at: str | None = None,
    ) -> MemoryObject:
        data = memory.model_dump(mode="json")
        data["status"] = status
        if last_validated_at is not None:
            data["last_validated_at"] = last_validated_at
        if last_used_at is not None:
            data["last_used_at"] = last_used_at

        updated = MemoryObject.model_validate(data)
        updated_data = updated.model_dump(mode="json")
        self.database.execute(
            """
            UPDATE memory_objects
            SET status = ?, last_validated_at = ?, last_used_at = ?, data = ?
            WHERE memory_id = ?
            """,
            (
                updated.status,
                updated_data["last_validated_at"],
                updated_data["last_used_at"],
                _json(updated_data),
                updated.memory_id,
            ),
        )
        return updated


class CellRepository:
    """Persistence adapter for cell specs."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, spec: CellSpec) -> None:
        existing = self.get(spec.cell_id)
        if existing is not None:
            data = spec.model_dump(mode="json")
            existing_data = existing.model_dump(mode="json")
            data["status"] = existing.status
            data["fitness"] = existing.fitness
            data["created_at"] = existing_data["created_at"]
            data["last_used_at"] = existing_data["last_used_at"]
            spec = CellSpec.model_validate(data)

        data = spec.model_dump(mode="json")
        self.database.execute(
            """
            INSERT OR REPLACE INTO cells (
                cell_id, name, version, input_event_types, output_event_types,
                permissions, status, fitness, created_at, last_used_at, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec.cell_id,
                spec.name,
                spec.version,
                _json(spec.input_event_types),
                _json(spec.output_event_types),
                _json(spec.permissions),
                spec.status,
                spec.fitness,
                str(data["created_at"]),
                data["last_used_at"],
                _json(data),
            ),
        )

    def get(self, cell_id: str) -> CellSpec | None:
        row = self.database.fetchone("SELECT data FROM cells WHERE cell_id = ?", (cell_id,))
        if row is None:
            return None
        return CellSpec.model_validate(json.loads(row["data"]))

    def list(self) -> list[CellSpec]:
        rows = self.database.fetchall("SELECT data FROM cells ORDER BY name, version")
        return [CellSpec.model_validate(json.loads(row["data"])) for row in rows]

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM cells")
        return int(row["count"]) if row else 0

    def touch(self, cell_id: str, used_at: str | None = None) -> CellSpec | None:
        spec = self.get(cell_id)
        if spec is None:
            return None

        data = spec.model_dump(mode="json")
        data["last_used_at"] = used_at or utc_now().isoformat()
        updated = CellSpec.model_validate(data)
        updated_data = updated.model_dump(mode="json")
        self.database.execute(
            """
            UPDATE cells
            SET status = ?, fitness = ?, created_at = ?, last_used_at = ?, data = ?
            WHERE cell_id = ?
            """,
            (
                updated.status,
                updated.fitness,
                str(updated_data["created_at"]),
                updated_data["last_used_at"],
                _json(updated_data),
                updated.cell_id,
            ),
        )
        return updated


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

    def list(self) -> list[dict[str, Any]]:
        rows = self.database.fetchall("SELECT * FROM audit_logs ORDER BY created_at, audit_id")
        return [
            {
                "audit_id": row["audit_id"],
                "created_at": row["created_at"],
                "actor": row["actor"],
                "action": row["action"],
                "context": json.loads(row["context"]),
                "details": json.loads(row["details"]),
            }
            for row in rows
        ]


class DecisionRepository:
    """Persistence adapter for durable decision records."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, decision: DecisionRecord) -> None:
        data = decision.model_dump(mode="json")
        self.database.execute(
            """
            INSERT INTO decision_logs (
                decision_id, decision_type, context, subject_id, actor,
                reason, source, created_at, details, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.decision_id,
                decision.decision_type,
                _json(data["context"]),
                decision.subject_id,
                decision.actor,
                decision.reason,
                decision.source,
                str(data["created_at"]),
                _json(data["details"]),
                _json(data),
            ),
        )

    def list(self) -> list[DecisionRecord]:
        rows = self.database.fetchall("SELECT data FROM decision_logs ORDER BY created_at, decision_id")
        return [DecisionRecord.model_validate(json.loads(row["data"])) for row in rows]

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM decision_logs")
        return int(row["count"]) if row else 0
