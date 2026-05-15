from __future__ import annotations

from pigenus.core.governance_decision_log import governance_decision_to_record
from pigenus.core.worker_execution_preflight import (
    WorkerExecutionPreflightRequest,
    WorkerExecutionPreflightService,
)
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
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
    max_sensitivity: Sensitivity = Sensitivity.PRIVATE,
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


def preflight_service() -> WorkerExecutionPreflightService:
    registry = WorkerRegistry()
    registry.register(profile("worker_good", network_access=True))
    registry.register(profile("worker_missing_capability", cells=["log_reader"]))
    registry.register(profile("worker_missing_runtime", runtimes=["node"]))
    registry.register(profile("worker_no_heartbeat"))
    registry.register(profile("worker_suspended", status=WorkerStatus.SUSPENDED))
    for worker_id in (
        "worker_good",
        "worker_missing_capability",
        "worker_missing_runtime",
        "worker_suspended",
    ):
        registry.record_heartbeat(
            WorkerHeartbeat(worker_id=worker_id, status=WorkerStatus.ACTIVE)
        )
    return WorkerExecutionPreflightService(WorkerInspectionService(registry))


def test_worker_execution_preflight_allows_known_suitable_worker():
    result = preflight_service().check(
        WorkerExecutionPreflightRequest(
            worker_id="worker_good",
            capability="meaning_ingester",
            required_runtime="python",
            sensitivity=Sensitivity.PRIVATE,
            network_required=True,
        )
    )

    assert result.allowed is True
    assert result.reason == "worker_execution_preflight_passed"
    assert [check.name for check in result.checks] == [
        "worker_considerable",
        "capability_available",
        "runtime_supported",
        "sensitivity_allowed",
        "network_allowed",
    ]


def test_worker_execution_preflight_blocks_unknown_worker():
    result = preflight_service().check(
        WorkerExecutionPreflightRequest(
            worker_id="missing_worker",
            capability="meaning_ingester",
        )
    )

    assert result.allowed is False
    assert result.reason == "worker_unknown"
    assert result.checks[0].name == "worker_known"
    assert result.checks[0].details["worker_id"] == "missing_worker"


def test_worker_execution_preflight_blocks_not_considerable_worker():
    result = preflight_service().check(
        WorkerExecutionPreflightRequest(
            worker_id="worker_no_heartbeat",
            capability="meaning_ingester",
        )
    )

    assert result.allowed is False
    assert result.reason == "worker_not_considerable"
    assert result.checks[0].decision.value == "block"


def test_worker_execution_preflight_reports_multiple_ordered_block_reasons():
    result = preflight_service().check(
        WorkerExecutionPreflightRequest(
            worker_id="worker_missing_capability",
            capability="meaning_ingester",
            required_runtime="node",
            sensitivity=Sensitivity.SECRET,
            network_required=True,
        )
    )

    assert result.allowed is False
    assert [check.reason for check in result.checks] == [
        "worker_considerable",
        "capability_missing",
        "runtime_missing",
        "sensitivity_exceeds_worker_limit",
        "network_unavailable",
    ]
    assert result.reason == "capability_missing"


def test_worker_execution_preflight_converts_to_log_compatible_governance_decision():
    result = preflight_service().check(
        WorkerExecutionPreflightRequest(
            worker_id="worker_good",
            capability="meaning_ingester",
            required_runtime="python",
        )
    )

    decision = result.to_governance_decision(
        actor_id="agent_preflight",
        room_id="room_developer",
        event_id="evt_preflight",
    )
    record = governance_decision_to_record(
        decision,
        source="worker_execution_preflight",
    )

    assert decision.decision.value == "allow"
    assert decision.details["family"] == "worker_execution_preflight"
    assert decision.details["worker_id"] == "worker_good"
    assert decision.details["trace"][0]["name"] == "worker_considerable"
    assert record.decision_type == "governance_decision"
    assert record.source == "worker_execution_preflight"
    assert record.details["family"] == "worker_execution_preflight"
