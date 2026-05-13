from __future__ import annotations

from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.schemas.systemform import (
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)


def profile(
    worker_id: str,
    *,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    worker_type: WorkerType = WorkerType.LOCAL_PROCESS,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=worker_type,
        display_name=worker_id,
        status=status,
        available_cells=["meaning_ingester"],
        supported_runtimes=["python"],
        network_access=False,
    )


def registry_with_workers() -> WorkerRegistry:
    registry = WorkerRegistry()
    registry.register(profile("worker_active"))
    registry.register(profile("worker_degraded"))
    registry.register(profile("worker_suspended", status=WorkerStatus.SUSPENDED))
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_active", status=WorkerStatus.ACTIVE)
    )
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_degraded", status=WorkerStatus.DEGRADED)
    )
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_suspended", status=WorkerStatus.ACTIVE)
    )
    return registry


def test_worker_inspection_lists_registry_rows_without_mutation():
    registry = registry_with_workers()
    service = WorkerInspectionService(registry)

    rows = service.list_workers()

    assert [row.worker_id for row in rows] == [
        "worker_active",
        "worker_degraded",
        "worker_suspended",
    ]
    assert rows[0].heartbeat_status == WorkerStatus.ACTIVE
    assert rows[0].considerable is True
    assert rows[0].available_cells == ("meaning_ingester",)
    assert rows[0].supported_runtimes == ("python",)
    assert rows[0].network_access is False


def test_worker_inspection_filters_by_profile_status_and_type():
    registry = WorkerRegistry()
    registry.register(profile("worker_local"))
    registry.register(profile("worker_server", worker_type=WorkerType.SERVER))
    registry.register(profile("worker_suspended", status=WorkerStatus.SUSPENDED))
    service = WorkerInspectionService(registry)

    assert [row.worker_id for row in service.list_workers(status=WorkerStatus.ACTIVE)] == [
        "worker_local",
        "worker_server",
    ]
    assert [row.worker_id for row in service.list_workers(worker_type=WorkerType.SERVER)] == [
        "worker_server"
    ]


def test_worker_inspection_filters_by_considerable_state():
    service = WorkerInspectionService(registry_with_workers())

    assert [row.worker_id for row in service.list_workers(considerable=True)] == [
        "worker_active"
    ]
    assert [row.worker_id for row in service.list_workers(considerable=False)] == [
        "worker_degraded",
        "worker_suspended",
    ]


def test_worker_inspection_show_worker_returns_one_row_or_none():
    service = WorkerInspectionService(registry_with_workers())

    row = service.show_worker("worker_degraded")

    assert row is not None
    assert row.worker_id == "worker_degraded"
    assert row.heartbeat_status == WorkerStatus.DEGRADED
    assert service.show_worker("missing") is None


def test_worker_inspection_handles_missing_heartbeat_as_not_considerable():
    registry = WorkerRegistry()
    registry.register(profile("worker_unseen"))
    service = WorkerInspectionService(registry)

    row = service.show_worker("worker_unseen")

    assert row is not None
    assert row.heartbeat_status is None
    assert row.last_seen_at is None
    assert row.considerable is False
