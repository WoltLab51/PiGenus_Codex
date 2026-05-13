from __future__ import annotations

from datetime import timedelta

from pydantic import ValidationError

from pigenus.core.worker_registry import WorkerRegistry
from pigenus.schemas.base import utc_now
from pigenus.schemas.systemform import (
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)


def worker_profile(
    worker_id: str,
    *,
    worker_type: WorkerType = WorkerType.LOCAL_PROCESS,
    status: WorkerStatus = WorkerStatus.ACTIVE,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=worker_type,
        display_name=worker_id,
        status=status,
    )


def test_worker_registry_registers_and_gets_profiles_without_storage():
    registry = WorkerRegistry()
    profile = worker_profile("worker_local_001")

    assert registry.register(profile) == profile
    assert registry.get("worker_local_001") == profile
    assert registry.get("missing") is None


def test_worker_registry_lists_profiles_deterministically_with_filters():
    registry = WorkerRegistry()
    registry.register(worker_profile("worker_server_002", worker_type=WorkerType.SERVER))
    registry.register(worker_profile("worker_local_001", worker_type=WorkerType.LOCAL_PROCESS))
    registry.register(
        worker_profile(
            "worker_pi_003",
            worker_type=WorkerType.RASPBERRY_PI,
            status=WorkerStatus.SUSPENDED,
        )
    )

    assert [profile.id for profile in registry.list()] == [
        "worker_local_001",
        "worker_pi_003",
        "worker_server_002",
    ]
    assert [profile.id for profile in registry.list(status=WorkerStatus.ACTIVE)] == [
        "worker_local_001",
        "worker_server_002",
    ]
    assert [profile.id for profile in registry.list(worker_type=WorkerType.SERVER)] == [
        "worker_server_002"
    ]


def test_worker_registry_records_latest_known_worker_heartbeat():
    registry = WorkerRegistry()
    registry.register(worker_profile("worker_local_001"))
    earlier = utc_now()
    later = earlier + timedelta(seconds=5)

    first = WorkerHeartbeat(
        worker_id="worker_local_001",
        status=WorkerStatus.ACTIVE,
        seen_at=later,
    )
    stale = WorkerHeartbeat(
        worker_id="worker_local_001",
        status=WorkerStatus.DEGRADED,
        seen_at=earlier,
    )

    assert registry.record_heartbeat(first) == first
    assert registry.record_heartbeat(stale) == first
    assert registry.latest_heartbeat("worker_local_001") == first


def test_worker_registry_rejects_unknown_worker_heartbeat():
    registry = WorkerRegistry()
    heartbeat = WorkerHeartbeat(worker_id="missing_worker", status=WorkerStatus.ACTIVE)

    try:
        registry.record_heartbeat(heartbeat)
    except ValueError as exc:
        assert "Unknown worker_id" in str(exc)
    else:
        raise AssertionError("Expected heartbeat for unknown worker to fail.")


def test_worker_registry_lists_heartbeats_with_status_filter():
    registry = WorkerRegistry()
    registry.register(worker_profile("worker_a"))
    registry.register(worker_profile("worker_b"))
    registry.record_heartbeat(WorkerHeartbeat(worker_id="worker_b", status=WorkerStatus.DEGRADED))
    registry.record_heartbeat(WorkerHeartbeat(worker_id="worker_a", status=WorkerStatus.ACTIVE))

    assert [heartbeat.worker_id for heartbeat in registry.list_heartbeats()] == [
        "worker_a",
        "worker_b",
    ]
    assert [
        heartbeat.worker_id
        for heartbeat in registry.list_heartbeats(status=WorkerStatus.DEGRADED)
    ] == ["worker_b"]


def test_worker_registry_considerable_requires_active_profile_and_heartbeat():
    registry = WorkerRegistry()
    registry.register(worker_profile("worker_active"))
    registry.register(worker_profile("worker_degraded"))
    registry.register(worker_profile("worker_suspended", status=WorkerStatus.SUSPENDED))

    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_active", status=WorkerStatus.ACTIVE)
    )
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_degraded", status=WorkerStatus.DEGRADED)
    )
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_suspended", status=WorkerStatus.ACTIVE)
    )

    assert registry.is_considerable("worker_active") is True
    assert registry.is_considerable("worker_degraded") is False
    assert registry.is_considerable("worker_suspended") is False
    assert registry.is_considerable("missing") is False


def test_worker_registry_does_not_turn_profile_inventory_into_authorization():
    try:
        WorkerProfile(
            id="worker_bad",
            worker_type=WorkerType.LOCAL_PROCESS,
            display_name="bad worker",
            status=WorkerStatus.ACTIVE,
            available_cells=["memory_writer"],
            capability_limits={},
        )
    except ValidationError:
        raise AssertionError("Capability inventory should not require permission fields.")
