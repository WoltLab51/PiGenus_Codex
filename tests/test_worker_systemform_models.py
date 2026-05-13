from __future__ import annotations

from pydantic import ValidationError

from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)


def test_worker_profile_models_execution_host_without_authorization():
    worker = WorkerProfile(
        worker_type=WorkerType.RASPBERRY_PI,
        display_name="Pi worker kitchen shelf",
        status=WorkerStatus.ACTIVE,
        owner_actor_id="human_ronny",
        home_room_id="room_developer",
        supported_runtimes=["python", "python", "sqlite"],
        available_cells=["log_reader", "meaning_ingester", "log_reader"],
        available_tools=["sqlite3"],
        capability_limits={"max_parallel_tasks": 1},
        cost_profile={"energy_class": "low"},
        privacy_profile={"local_only": True},
        failure_semantics={"timeout_seconds": 30, "retry": "none"},
        max_sensitivity=Sensitivity.PRIVATE,
        network_access=False,
    )

    data = worker.model_dump(mode="json")

    assert worker.id.startswith("worker_")
    assert data["worker_type"] == "raspberry_pi"
    assert data["status"] == "active"
    assert data["supported_runtimes"] == ["python", "sqlite"]
    assert data["available_cells"] == ["log_reader", "meaning_ingester"]
    assert data["max_sensitivity"] == "private"
    assert data["network_access"] is False


def test_worker_profile_requires_type_and_display_name():
    try:
        WorkerProfile(worker_type=WorkerType.LOCAL_PROCESS, display_name="")
    except ValidationError as exc:
        assert "display_name" in str(exc)
    else:
        raise AssertionError("Expected empty display_name to fail validation.")


def test_worker_heartbeat_models_liveness_without_execution():
    heartbeat = WorkerHeartbeat(
        worker_id="worker_pi_001",
        status=WorkerStatus.DEGRADED,
        runtime_version="0.4-preview",
        health_summary={"storage": "ok", "temperature": "warm"},
        degraded_reasons=["temperature", "temperature", "low_memory"],
    )

    data = heartbeat.model_dump(mode="json")

    assert heartbeat.id.startswith("whb_")
    assert data["worker_id"] == "worker_pi_001"
    assert data["status"] == "degraded"
    assert data["degraded_reasons"] == ["temperature", "low_memory"]
    assert data["seen_at"]


def test_worker_heartbeat_requires_worker_id():
    try:
        WorkerHeartbeat(worker_id="", status=WorkerStatus.ACTIVE)
    except ValidationError as exc:
        assert "worker_id" in str(exc)
    else:
        raise AssertionError("Expected empty worker_id to fail validation.")
