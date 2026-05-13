from __future__ import annotations

from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.core.worker_scheduling_preview import (
    WorkerSchedulingPreviewService,
    WorkerSchedulingRequest,
)
from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)


def profile(
    worker_id: str,
    *,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    cells: list[str] | None = None,
    runtimes: list[str] | None = None,
    max_sensitivity: Sensitivity = Sensitivity.INTERNAL,
    network_access: bool = False,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=worker_id,
        status=status,
        available_cells=cells or ["meaning_ingester"],
        supported_runtimes=runtimes or ["python"],
        max_sensitivity=max_sensitivity,
        network_access=network_access,
    )


def preview_service() -> WorkerSchedulingPreviewService:
    registry = WorkerRegistry()
    registry.register(profile("worker_good"))
    registry.register(profile("worker_missing_capability", cells=["log_reader"]))
    registry.register(profile("worker_missing_runtime", runtimes=["node"]))
    registry.register(profile("worker_no_heartbeat"))
    registry.register(profile("worker_degraded"))
    registry.record_heartbeat(WorkerHeartbeat(worker_id="worker_good", status=WorkerStatus.ACTIVE))
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_missing_capability", status=WorkerStatus.ACTIVE)
    )
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_missing_runtime", status=WorkerStatus.ACTIVE)
    )
    registry.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_degraded", status=WorkerStatus.DEGRADED)
    )
    return WorkerSchedulingPreviewService(WorkerInspectionService(registry))


def test_worker_scheduling_preview_selects_suitable_workers_first():
    result = preview_service().preview(
        WorkerSchedulingRequest(capability="meaning_ingester", required_runtime="python")
    )

    assert result.suitable_workers == ("worker_good",)
    assert [candidate.worker_id for candidate in result.candidates][0] == "worker_good"
    assert result.candidates[0].reasons == ("preview_suitable",)


def test_worker_scheduling_preview_explains_unsuitable_workers():
    result = preview_service().preview(
        WorkerSchedulingRequest(capability="meaning_ingester", required_runtime="python")
    )
    reasons = {candidate.worker_id: candidate.reasons for candidate in result.candidates}

    assert reasons["worker_missing_capability"] == ("capability_missing",)
    assert reasons["worker_missing_runtime"] == ("runtime_missing",)
    assert reasons["worker_no_heartbeat"] == ("worker_not_considerable",)
    assert reasons["worker_degraded"] == ("worker_not_considerable",)


def test_worker_scheduling_preview_can_require_network_access():
    result = preview_service().preview(
        WorkerSchedulingRequest(
            capability="meaning_ingester",
            required_runtime="python",
            network_required=True,
        )
    )

    assert result.suitable_workers == ()
    reasons = {candidate.worker_id: candidate.reasons for candidate in result.candidates}
    assert reasons["worker_good"] == ("network_unavailable",)


def test_worker_scheduling_preview_checks_sensitivity_limit():
    result = preview_service().preview(
        WorkerSchedulingRequest(
            capability="meaning_ingester",
            required_runtime="python",
            sensitivity=Sensitivity.SECRET,
        )
    )

    assert result.suitable_workers == ()
    reasons = {candidate.worker_id: candidate.reasons for candidate in result.candidates}
    assert reasons["worker_good"] == ("sensitivity_exceeds_worker_limit",)


def test_worker_scheduling_preview_does_not_mutate_registry():
    service = preview_service()

    before = service.inspection.list_workers()
    service.preview(WorkerSchedulingRequest(capability="meaning_ingester"))
    after = service.inspection.list_workers()

    assert after == before
