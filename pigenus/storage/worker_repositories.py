from __future__ import annotations

import json
from typing import Any

from pigenus.schemas.systemform import (
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


class WorkerRepository:
    """Persistence adapter for Worker Runtime profiles and current heartbeats."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add_profile(self, profile: WorkerProfile) -> None:
        data = profile.model_dump(mode="json")
        self.database.execute(
            """
            INSERT OR REPLACE INTO worker_profiles (
                worker_id, worker_type, display_name, status, owner_actor_id,
                home_room_id, max_sensitivity, network_access, created_at,
                updated_at, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile.id,
                profile.worker_type.value,
                profile.display_name,
                profile.status.value,
                profile.owner_actor_id,
                profile.home_room_id,
                profile.max_sensitivity.value,
                1 if profile.network_access else 0,
                str(data["created_at"]),
                str(data["updated_at"]),
                _json(data),
            ),
        )

    def get_profile(self, worker_id: str) -> WorkerProfile | None:
        row = self.database.fetchone(
            "SELECT data FROM worker_profiles WHERE worker_id = ?",
            (worker_id,),
        )
        if row is None:
            return None
        return WorkerProfile.model_validate(json.loads(row["data"]))

    def list_profiles(
        self,
        *,
        status: WorkerStatus | str | None = None,
        worker_type: WorkerType | str | None = None,
        owner_actor_id: str | None = None,
        home_room_id: str | None = None,
    ) -> list[WorkerProfile]:
        clauses: list[str] = []
        parameters: list[str] = []

        if status is not None:
            clauses.append("status = ?")
            parameters.append(self._enum_value(status))
        if worker_type is not None:
            clauses.append("worker_type = ?")
            parameters.append(self._enum_value(worker_type))
        if owner_actor_id is not None:
            clauses.append("owner_actor_id = ?")
            parameters.append(owner_actor_id)
        if home_room_id is not None:
            clauses.append("home_room_id = ?")
            parameters.append(home_room_id)

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.database.fetchall(
            f"SELECT data FROM worker_profiles{where} ORDER BY created_at, worker_id",
            tuple(parameters),
        )
        return [WorkerProfile.model_validate(json.loads(row["data"])) for row in rows]

    def count_profiles(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM worker_profiles")
        return int(row["count"]) if row else 0

    def record_heartbeat(self, heartbeat: WorkerHeartbeat) -> None:
        if self.get_profile(heartbeat.worker_id) is None:
            raise ValueError(f"Unknown worker_id: {heartbeat.worker_id}")

        current = self.get_heartbeat(heartbeat.worker_id)
        if current is not None and current.seen_at > heartbeat.seen_at:
            return

        data = heartbeat.model_dump(mode="json")
        self.database.execute(
            """
            INSERT OR REPLACE INTO worker_heartbeats (
                worker_id, heartbeat_id, status, seen_at, runtime_version, data
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                heartbeat.worker_id,
                heartbeat.id,
                heartbeat.status.value,
                str(data["seen_at"]),
                heartbeat.runtime_version,
                _json(data),
            ),
        )

    def get_heartbeat(self, worker_id: str) -> WorkerHeartbeat | None:
        row = self.database.fetchone(
            "SELECT data FROM worker_heartbeats WHERE worker_id = ?",
            (worker_id,),
        )
        if row is None:
            return None
        return WorkerHeartbeat.model_validate(json.loads(row["data"]))

    def list_heartbeats(
        self,
        *,
        status: WorkerStatus | str | None = None,
    ) -> list[WorkerHeartbeat]:
        clauses: list[str] = []
        parameters: list[str] = []

        if status is not None:
            clauses.append("status = ?")
            parameters.append(self._enum_value(status))

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.database.fetchall(
            f"SELECT data FROM worker_heartbeats{where} ORDER BY seen_at, worker_id",
            tuple(parameters),
        )
        return [WorkerHeartbeat.model_validate(json.loads(row["data"])) for row in rows]

    def count_heartbeats(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM worker_heartbeats")
        return int(row["count"]) if row else 0

    @staticmethod
    def _enum_value(value: WorkerStatus | WorkerType | str) -> str:
        if isinstance(value, WorkerStatus | WorkerType):
            return value.value
        return value


class WorkerAssignmentRepository:
    """Persistence adapter for governed worker assignment intent."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, assignment: WorkerAssignment) -> None:
        self._require_known_worker(assignment.worker_id)
        self._require_governance_decision(assignment.governance_decision_id)

        data = assignment.model_dump(mode="json")
        self.database.execute(
            """
            INSERT INTO worker_assignments (
                assignment_id, worker_id, capability, room_id, status,
                governance_decision_id, created_by_actor_id, event_id,
                context_stack_id, required_runtime, sensitivity, network_required,
                created_at, updated_at, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assignment.id,
                assignment.worker_id,
                assignment.capability,
                assignment.room_id,
                assignment.status.value,
                assignment.governance_decision_id,
                assignment.created_by_actor_id,
                assignment.event_id,
                assignment.context_stack_id,
                assignment.required_runtime,
                assignment.sensitivity.value if assignment.sensitivity else None,
                1 if assignment.network_required else 0,
                str(data["created_at"]),
                str(data["updated_at"]),
                _json(data),
            ),
        )

    def get(self, assignment_id: str) -> WorkerAssignment | None:
        row = self.database.fetchone(
            "SELECT data FROM worker_assignments WHERE assignment_id = ?",
            (assignment_id,),
        )
        if row is None:
            return None
        return WorkerAssignment.model_validate(json.loads(row["data"]))

    def list(
        self,
        *,
        worker_id: str | None = None,
        status: WorkerAssignmentStatus | str | None = None,
        room_id: str | None = None,
        capability: str | None = None,
        governance_decision_id: str | None = None,
    ) -> list[WorkerAssignment]:
        clauses: list[str] = []
        parameters: list[str] = []

        if worker_id is not None:
            clauses.append("worker_id = ?")
            parameters.append(worker_id)
        if status is not None:
            clauses.append("status = ?")
            parameters.append(self._enum_value(status))
        if room_id is not None:
            clauses.append("room_id = ?")
            parameters.append(room_id)
        if capability is not None:
            clauses.append("capability = ?")
            parameters.append(capability)
        if governance_decision_id is not None:
            clauses.append("governance_decision_id = ?")
            parameters.append(governance_decision_id)

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.database.fetchall(
            f"SELECT data FROM worker_assignments{where} ORDER BY created_at, assignment_id",
            tuple(parameters),
        )
        return [WorkerAssignment.model_validate(json.loads(row["data"])) for row in rows]

    def count(self) -> int:
        row = self.database.fetchone("SELECT COUNT(*) AS count FROM worker_assignments")
        return int(row["count"]) if row else 0

    def _require_known_worker(self, worker_id: str) -> None:
        row = self.database.fetchone(
            "SELECT 1 FROM worker_profiles WHERE worker_id = ?",
            (worker_id,),
        )
        if row is None:
            raise ValueError(f"Unknown worker_id: {worker_id}")

    def _require_governance_decision(self, decision_id: str) -> None:
        row = self.database.fetchone(
            "SELECT 1 FROM decision_logs WHERE decision_id = ?",
            (decision_id,),
        )
        if row is None:
            raise ValueError(f"Unknown governance_decision_id: {decision_id}")

    @staticmethod
    def _enum_value(value: WorkerAssignmentStatus | str) -> str:
        if isinstance(value, WorkerAssignmentStatus):
            return value.value
        return value
