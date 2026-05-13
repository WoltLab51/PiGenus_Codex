from __future__ import annotations

from pigenus.schemas.systemform import (
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)


class WorkerRegistry:
    """Storage-free registry for known worker profiles and latest heartbeats."""

    def __init__(self) -> None:
        self._profiles: dict[str, WorkerProfile] = {}
        self._heartbeats: dict[str, WorkerHeartbeat] = {}

    def register(self, profile: WorkerProfile) -> WorkerProfile:
        self._profiles[profile.id] = profile
        return profile

    def get(self, worker_id: str) -> WorkerProfile | None:
        return self._profiles.get(worker_id)

    def list(
        self,
        *,
        status: WorkerStatus | None = None,
        worker_type: WorkerType | None = None,
    ) -> list[WorkerProfile]:
        profiles = sorted(self._profiles.values(), key=lambda profile: profile.id)
        if status is not None:
            profiles = [profile for profile in profiles if profile.status == status]
        if worker_type is not None:
            profiles = [profile for profile in profiles if profile.worker_type == worker_type]
        return profiles

    def record_heartbeat(self, heartbeat: WorkerHeartbeat) -> WorkerHeartbeat:
        if heartbeat.worker_id not in self._profiles:
            raise ValueError(f"Unknown worker_id: {heartbeat.worker_id}")
        current = self._heartbeats.get(heartbeat.worker_id)
        if current is None or heartbeat.seen_at >= current.seen_at:
            self._heartbeats[heartbeat.worker_id] = heartbeat
        return self._heartbeats[heartbeat.worker_id]

    def latest_heartbeat(self, worker_id: str) -> WorkerHeartbeat | None:
        return self._heartbeats.get(worker_id)

    def list_heartbeats(self, *, status: WorkerStatus | None = None) -> list[WorkerHeartbeat]:
        heartbeats = sorted(self._heartbeats.values(), key=lambda heartbeat: heartbeat.worker_id)
        if status is not None:
            heartbeats = [heartbeat for heartbeat in heartbeats if heartbeat.status == status]
        return heartbeats

    def is_considerable(self, worker_id: str) -> bool:
        profile = self.get(worker_id)
        heartbeat = self.latest_heartbeat(worker_id)
        if profile is None or heartbeat is None:
            return False
        return profile.status == WorkerStatus.ACTIVE and heartbeat.status == WorkerStatus.ACTIVE
