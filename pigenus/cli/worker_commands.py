from __future__ import annotations

import argparse
import json
from pathlib import Path

from pigenus.core.worker_execution_preflight import (
    WorkerExecutionPreflightLogger,
    WorkerExecutionPreflightRequest,
    WorkerExecutionPreflightService,
)
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.core.worker_scheduling_preview import (
    WorkerSchedulingPreviewLogger,
    WorkerSchedulingPreviewService,
    WorkerSchedulingRequest,
)
from pigenus.schemas.systemform import Sensitivity, WorkerHeartbeat, WorkerStatus, WorkerType
from pigenus.storage.database import Database
from pigenus.storage.repositories import DecisionRepository, WorkerRepository


EMPTY_WORKER_LIST_MESSAGE = "No workers found."
WORKER_COMMANDS = {
    "worker-list",
    "worker-show",
    "worker-scheduling-preview",
    "worker-execution-preflight",
}


def add_worker_commands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    worker_list = subparsers.add_parser(
        "worker-list",
        help="List known workers without modifying them.",
    )
    worker_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    worker_list.add_argument(
        "--status",
        choices=tuple(status.value for status in WorkerStatus),
        default=None,
        help="Filter by worker profile status.",
    )
    worker_list.add_argument(
        "--type",
        choices=tuple(worker_type.value for worker_type in WorkerType),
        default=None,
        help="Filter by worker type.",
    )
    worker_list.add_argument("--owner", default=None, help="Filter by owner actor ID.")
    worker_list.add_argument("--room", default=None, help="Filter by home room ID.")
    worker_list.add_argument(
        "--considerable",
        choices=("yes", "no"),
        default=None,
        help="Filter by active profile plus active heartbeat.",
    )

    worker_show = subparsers.add_parser(
        "worker-show",
        help="Show one worker by ID without modifying it.",
    )
    worker_show.add_argument("worker_id", help="Worker ID to inspect.")
    worker_show.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    worker_scheduling_preview = subparsers.add_parser(
        "worker-scheduling-preview",
        help="Preview worker suitability for a capability without modifying storage.",
    )
    worker_scheduling_preview.add_argument("capability", help="Required cell or capability ID.")
    worker_scheduling_preview.add_argument(
        "--db",
        default="pigenus.sqlite3",
        help="SQLite database path.",
    )
    worker_scheduling_preview.add_argument("--runtime", default=None, help="Required runtime.")
    worker_scheduling_preview.add_argument(
        "--sensitivity",
        choices=tuple(sensitivity.value for sensitivity in Sensitivity),
        default=None,
        help="Required sensitivity ceiling.",
    )
    worker_scheduling_preview.add_argument(
        "--network-required",
        action="store_true",
        help="Require worker network access.",
    )
    worker_scheduling_preview.add_argument(
        "--log",
        action="store_true",
        help="Persist the preview decision to the decision log.",
    )
    worker_scheduling_preview.add_argument(
        "--actor",
        default="worker_scheduling_preview_cli",
        help="Actor ID for the preview governance decision.",
    )
    worker_scheduling_preview.add_argument(
        "--room",
        default="room_developer",
        help="Room ID for the preview governance decision.",
    )
    worker_scheduling_preview.add_argument(
        "--event-id",
        default=None,
        help="Optional event ID for the logged preview decision.",
    )

    worker_execution_preflight = subparsers.add_parser(
        "worker-execution-preflight",
        help="Preview-check one worker before execution without modifying storage.",
    )
    worker_execution_preflight.add_argument("worker_id", help="Worker ID to check.")
    worker_execution_preflight.add_argument("capability", help="Required cell or capability ID.")
    worker_execution_preflight.add_argument(
        "--db",
        default="pigenus.sqlite3",
        help="SQLite database path.",
    )
    worker_execution_preflight.add_argument("--runtime", default=None, help="Required runtime.")
    worker_execution_preflight.add_argument(
        "--sensitivity",
        choices=tuple(sensitivity.value for sensitivity in Sensitivity),
        default=None,
        help="Required sensitivity ceiling.",
    )
    worker_execution_preflight.add_argument(
        "--network-required",
        action="store_true",
        help="Require worker network access.",
    )
    worker_execution_preflight.add_argument(
        "--log",
        action="store_true",
        help="Persist the preflight decision to the decision log.",
    )
    worker_execution_preflight.add_argument(
        "--actor",
        default="worker_execution_preflight_cli",
        help="Actor ID for the preflight governance decision.",
    )
    worker_execution_preflight.add_argument(
        "--room",
        default="room_developer",
        help="Room ID for the preflight governance decision.",
    )
    worker_execution_preflight.add_argument(
        "--event-id",
        default=None,
        help="Optional event ID for the logged preflight decision.",
    )


def is_worker_command(command: str) -> bool:
    return command in WORKER_COMMANDS


def handle_worker_command(args: argparse.Namespace) -> int:
    if args.command == "worker-list":
        return _handle_worker_list(args)
    if args.command == "worker-show":
        return _handle_worker_show(args)
    if args.command == "worker-scheduling-preview":
        return _handle_worker_scheduling_preview(args)
    if args.command == "worker-execution-preflight":
        return _handle_worker_execution_preflight(args)
    raise ValueError(f"Unknown worker command: {args.command}")


def _handle_worker_list(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    try:
        repository = WorkerRepository(database)
        workers = repository.list_profiles(
            status=args.status,
            worker_type=args.type,
            owner_actor_id=args.owner,
            home_room_id=args.room,
        )
        rows = []
        for worker in workers:
            heartbeat = repository.get_heartbeat(worker.id)
            rows.append((worker, heartbeat, _worker_is_considerable(worker.status, heartbeat)))
    finally:
        database.close()

    if args.considerable is not None:
        expected = args.considerable == "yes"
        rows = [row for row in rows if row[2] is expected]

    if not rows:
        print(EMPTY_WORKER_LIST_MESSAGE)
        return 0

    for worker, heartbeat, considerable in rows:
        heartbeat_status = heartbeat.status.value if heartbeat is not None else "-"
        last_seen = heartbeat.seen_at.isoformat() if heartbeat is not None else "-"
        print(
            f"{worker.id} | {worker.worker_type.value} | {worker.status.value} | "
            f"heartbeat={heartbeat_status} | last_seen_at={last_seen} | "
            f"considerable={'yes' if considerable else 'no'} | {worker.display_name}"
        )
    return 0


def _handle_worker_show(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    try:
        repository = WorkerRepository(database)
        worker = repository.get_profile(args.worker_id)
        heartbeat = repository.get_heartbeat(args.worker_id)
    finally:
        database.close()

    if worker is None:
        print(f"Worker not found: {args.worker_id}")
        return 1

    payload = {
        "considerable": _worker_is_considerable(
            worker.status,
            heartbeat,
        ),
        "heartbeat": heartbeat.model_dump(mode="json") if heartbeat is not None else None,
        "profile": worker.model_dump(mode="json"),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


def _handle_worker_scheduling_preview(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    logged_record = None
    try:
        repository = WorkerRepository(database)
        registry = _worker_registry_from_repository(repository)
        preview = WorkerSchedulingPreviewService(
            WorkerInspectionService(registry)
        ).preview(
            WorkerSchedulingRequest(
                capability=args.capability,
                required_runtime=args.runtime,
                sensitivity=(
                    Sensitivity(args.sensitivity)
                    if args.sensitivity is not None
                    else None
                ),
                network_required=args.network_required,
            )
        )
        if args.log:
            logged_record = WorkerSchedulingPreviewLogger(
                DecisionRepository(database)
            ).add(
                preview,
                actor_id=args.actor,
                room_id=args.room,
                event_id=args.event_id,
            )
    finally:
        database.close()

    decision = preview.to_governance_decision(
        actor_id=args.actor,
        room_id=args.room,
        event_id=args.event_id,
    )
    recommended_worker = preview.suitable_workers[0] if preview.suitable_workers else "-"

    print("Worker Scheduling Preview")
    print(f"Capability: {preview.request.capability}")
    print(f"Runtime: {preview.request.required_runtime or '-'}")
    sensitivity = preview.request.sensitivity.value if preview.request.sensitivity else "-"
    print(f"Sensitivity: {sensitivity}")
    print(f"Network required: {'yes' if preview.request.network_required else 'no'}")
    print(f"Decision: {decision.decision.value}")
    print(f"Reason: {decision.reason}")
    print(f"Recommended worker: {recommended_worker}")
    if logged_record is not None:
        print(f"Logged decision: {logged_record.decision_id}")
    print("Candidates:")
    if not preview.candidates:
        print("-")
        return 0
    for candidate in preview.candidates:
        print(
            f"{candidate.worker_id} | suitable={'yes' if candidate.suitable else 'no'} | "
            f"reasons={','.join(candidate.reasons)}"
        )
    return 0


def _handle_worker_execution_preflight(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    logged_record = None
    try:
        repository = WorkerRepository(database)
        registry = _worker_registry_from_repository(repository)
        result = WorkerExecutionPreflightService(
            WorkerInspectionService(registry)
        ).check(
            WorkerExecutionPreflightRequest(
                worker_id=args.worker_id,
                capability=args.capability,
                required_runtime=args.runtime,
                sensitivity=(
                    Sensitivity(args.sensitivity)
                    if args.sensitivity is not None
                    else None
                ),
                network_required=args.network_required,
            )
        )
        if args.log:
            logged_record = WorkerExecutionPreflightLogger(
                DecisionRepository(database)
            ).add(
                result,
                actor_id=args.actor,
                room_id=args.room,
                event_id=args.event_id,
            )
    finally:
        database.close()

    decision = result.to_governance_decision(
        actor_id=args.actor,
        room_id=args.room,
        event_id=args.event_id,
    )

    print("Worker Execution Preflight")
    print(f"Worker: {result.request.worker_id}")
    print(f"Capability: {result.request.capability}")
    print(f"Runtime: {result.request.required_runtime or '-'}")
    sensitivity = result.request.sensitivity.value if result.request.sensitivity else "-"
    print(f"Sensitivity: {sensitivity}")
    print(f"Network required: {'yes' if result.request.network_required else 'no'}")
    print(f"Decision: {decision.decision.value}")
    print(f"Reason: {decision.reason}")
    if logged_record is not None:
        print(f"Logged decision: {logged_record.decision_id}")
    print("Checks:")
    for check in result.checks:
        print(
            f"{check.name} | decision={check.decision.value} | "
            f"reason={check.reason}"
        )
    return 0


def _worker_is_considerable(
    profile_status: WorkerStatus,
    heartbeat: WorkerHeartbeat | None,
) -> bool:
    return (
        profile_status == WorkerStatus.ACTIVE
        and heartbeat is not None
        and heartbeat.status == WorkerStatus.ACTIVE
    )


def _worker_registry_from_repository(repository: WorkerRepository) -> WorkerRegistry:
    registry = WorkerRegistry()
    for profile in repository.list_profiles():
        registry.register(profile)
    for heartbeat in repository.list_heartbeats():
        if registry.get(heartbeat.worker_id) is not None:
            registry.record_heartbeat(heartbeat)
    return registry
