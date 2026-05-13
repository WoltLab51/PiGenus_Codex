from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pigenus.core.worker_registry import WorkerRegistry
from pigenus.schemas.systemform import Sensitivity, WorkerStatus, WorkerType


@dataclass(frozen=True)
class WorkerInspection:
    """Read-only operator row for a known worker profile."""

    worker_id: str
    display_name: str
    worker_type: WorkerType
    profile_status: WorkerStatus
    heartbeat_status: WorkerStatus | None
    last_seen_at: datetime | None
    considerable: bool
    available_cells: tuple[str, ...]
    supported_runtimes: tuple[str, ...]
    max_sensitivity: Sensitivity
    network_access: bool


class WorkerInspectionService:
    """Builds read-only worker inspection rows from a storage-free registry."""

    def __init__(self, registry: WorkerRegistry) -> None:
        self.registry = registry

    def list_workers(
        self,
        *,
        status: WorkerStatus | None = None,
        worker_type: WorkerType | None = None,
        considerable: bool | None = None,
    ) -> list[WorkerInspection]:
        rows: list[WorkerInspection] = []
        for profile in self.registry.list(status=status, worker_type=worker_type):
            heartbeat = self.registry.latest_heartbeat(profile.id)
            row = WorkerInspection(
                worker_id=profile.id,
                display_name=profile.display_name,
                worker_type=profile.worker_type,
                profile_status=profile.status,
                heartbeat_status=heartbeat.status if heartbeat is not None else None,
                last_seen_at=heartbeat.seen_at if heartbeat is not None else None,
                considerable=self.registry.is_considerable(profile.id),
                available_cells=tuple(profile.available_cells),
                supported_runtimes=tuple(profile.supported_runtimes),
                max_sensitivity=profile.max_sensitivity,
                network_access=profile.network_access,
            )
            if considerable is not None and row.considerable is not considerable:
                continue
            rows.append(row)
        return rows

    def show_worker(self, worker_id: str) -> WorkerInspection | None:
        rows = self.list_workers()
        for row in rows:
            if row.worker_id == worker_id:
                return row
        return None
