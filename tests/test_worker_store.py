from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerHeartbeat,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import WorkerRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-store-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(
    worker_id: str,
    *,
    worker_type: WorkerType = WorkerType.LOCAL_PROCESS,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    owner_actor_id: str | None = "human_ronny",
    home_room_id: str | None = "room_developer",
    created_at: datetime = datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc),
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=worker_type,
        display_name=f"{worker_id} display",
        status=status,
        owner_actor_id=owner_actor_id,
        home_room_id=home_room_id,
        supported_runtimes=["python"],
        available_cells=["meaning_ingester"],
        cost_profile={"class": "low"},
        privacy_profile={"local_only": True},
        failure_semantics={"timeout_seconds": 30},
        max_sensitivity=Sensitivity.PRIVATE,
        network_access=False,
        created_at=created_at,
        updated_at=created_at,
    )


def heartbeat(
    worker_id: str,
    *,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    seen_at: datetime = datetime(2026, 5, 14, 8, 5, tzinfo=timezone.utc),
) -> WorkerHeartbeat:
    return WorkerHeartbeat(
        worker_id=worker_id,
        status=status,
        seen_at=seen_at,
        runtime_version="0.4-preview",
        health_summary={"storage": "ok"},
    )


def test_worker_repository_adds_and_gets_profile():
    database = Database(db_path("profile-roundtrip"))
    database.initialize()
    repository = WorkerRepository(database)
    original = worker_profile("worker_roundtrip")

    repository.add_profile(original)
    stored = repository.get_profile("worker_roundtrip")

    assert stored == original
    assert stored is not None
    assert stored.available_cells == ["meaning_ingester"]
    assert repository.count_profiles() == 1
    database.close()


def test_worker_repository_lists_profiles_with_filters_in_created_order():
    database = Database(db_path("profile-filters"))
    database.initialize()
    repository = WorkerRepository(database)

    repository.add_profile(
        worker_profile(
            "worker_second",
            worker_type=WorkerType.SERVER,
            owner_actor_id="human_ronny",
            created_at=datetime(2026, 5, 14, 9, 0, tzinfo=timezone.utc),
        )
    )
    repository.add_profile(
        worker_profile(
            "worker_first",
            worker_type=WorkerType.RASPBERRY_PI,
            owner_actor_id="human_anna",
            home_room_id="room_family",
            created_at=datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc),
        )
    )
    repository.add_profile(
        worker_profile(
            "worker_suspended",
            status=WorkerStatus.SUSPENDED,
            created_at=datetime(2026, 5, 14, 10, 0, tzinfo=timezone.utc),
        )
    )

    assert [profile.id for profile in repository.list_profiles()] == [
        "worker_first",
        "worker_second",
        "worker_suspended",
    ]
    assert [profile.id for profile in repository.list_profiles(status=WorkerStatus.ACTIVE)] == [
        "worker_first",
        "worker_second",
    ]
    assert [profile.id for profile in repository.list_profiles(worker_type="server")] == [
        "worker_second"
    ]
    assert [profile.id for profile in repository.list_profiles(owner_actor_id="human_anna")] == [
        "worker_first"
    ]
    assert [profile.id for profile in repository.list_profiles(home_room_id="room_family")] == [
        "worker_first"
    ]
    database.close()


def test_worker_repository_records_current_heartbeat_for_known_worker():
    database = Database(db_path("heartbeat-current"))
    database.initialize()
    repository = WorkerRepository(database)
    repository.add_profile(worker_profile("worker_local"))
    earlier = datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc)
    later = earlier + timedelta(seconds=30)
    stale = heartbeat("worker_local", status=WorkerStatus.DEGRADED, seen_at=earlier)
    fresh = heartbeat("worker_local", status=WorkerStatus.ACTIVE, seen_at=later)

    repository.record_heartbeat(fresh)
    repository.record_heartbeat(stale)

    stored = repository.get_heartbeat("worker_local")
    assert stored == fresh
    assert repository.count_heartbeats() == 1
    database.close()


def test_worker_repository_rejects_heartbeat_for_unknown_worker():
    database = Database(db_path("heartbeat-unknown"))
    database.initialize()
    repository = WorkerRepository(database)

    try:
        repository.record_heartbeat(heartbeat("missing_worker"))
    except ValueError as exc:
        assert "Unknown worker_id" in str(exc)
    else:
        raise AssertionError("Expected heartbeat for unknown worker to fail.")
    database.close()


def test_worker_repository_lists_heartbeats_with_status_filter():
    database = Database(db_path("heartbeat-filter"))
    database.initialize()
    repository = WorkerRepository(database)
    repository.add_profile(worker_profile("worker_a"))
    repository.add_profile(worker_profile("worker_b"))
    repository.record_heartbeat(heartbeat("worker_b", status=WorkerStatus.DEGRADED))
    repository.record_heartbeat(heartbeat("worker_a", status=WorkerStatus.ACTIVE))

    assert [item.worker_id for item in repository.list_heartbeats()] == ["worker_a", "worker_b"]
    assert [item.worker_id for item in repository.list_heartbeats(status="degraded")] == [
        "worker_b"
    ]
    database.close()


def test_worker_repository_returns_none_for_missing_profile_and_heartbeat():
    database = Database(db_path("missing"))
    database.initialize()
    repository = WorkerRepository(database)

    assert repository.get_profile("missing") is None
    assert repository.get_heartbeat("missing") is None
    database.close()
