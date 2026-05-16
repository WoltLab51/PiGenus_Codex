from __future__ import annotations

import argparse
from pathlib import Path

from pigenus.schemas.systemform import WorkerAssignmentStatus
from pigenus.storage.database import Database
from pigenus.storage.repositories import WorkerAssignmentRepository


EMPTY_WORKER_ASSIGNMENT_LIST_MESSAGE = "No worker assignments found."
WORKER_ASSIGNMENT_COMMANDS = {
    "worker-assignment-list",
}


def add_worker_assignment_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    worker_assignment_list = subparsers.add_parser(
        "worker-assignment-list",
        help="List worker assignment intent records without modifying them.",
    )
    worker_assignment_list.add_argument(
        "--db",
        default="pigenus.sqlite3",
        help="SQLite database path.",
    )
    worker_assignment_list.add_argument("--worker", default=None, help="Filter by worker ID.")
    worker_assignment_list.add_argument(
        "--status",
        choices=tuple(status.value for status in WorkerAssignmentStatus),
        default=None,
        help="Filter by assignment status.",
    )
    worker_assignment_list.add_argument("--room", default=None, help="Filter by room ID.")
    worker_assignment_list.add_argument("--capability", default=None, help="Filter by capability.")
    worker_assignment_list.add_argument(
        "--governance-decision",
        default=None,
        help="Filter by governance decision ID.",
    )


def is_worker_assignment_command(command: str) -> bool:
    return command in WORKER_ASSIGNMENT_COMMANDS


def handle_worker_assignment_command(args: argparse.Namespace) -> int:
    if args.command == "worker-assignment-list":
        return _handle_worker_assignment_list(args)
    raise ValueError(f"Unknown worker assignment command: {args.command}")


def _handle_worker_assignment_list(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    try:
        repository = WorkerAssignmentRepository(database)
        assignments = repository.list(
            worker_id=args.worker,
            status=args.status,
            room_id=args.room,
            capability=args.capability,
            governance_decision_id=args.governance_decision,
        )
    finally:
        database.close()

    if not assignments:
        print(EMPTY_WORKER_ASSIGNMENT_LIST_MESSAGE)
        return 0

    for assignment in assignments:
        sensitivity = assignment.sensitivity.value if assignment.sensitivity else "-"
        runtime = assignment.required_runtime or "-"
        print(
            f"{assignment.id} | worker={assignment.worker_id} | "
            f"status={assignment.status.value} | capability={assignment.capability} | "
            f"room={assignment.room_id} | decision={assignment.governance_decision_id} | "
            f"runtime={runtime} | sensitivity={sensitivity} | "
            f"network_required={'yes' if assignment.network_required else 'no'} | "
            f"created_by={assignment.created_by_actor_id}"
        )
    return 0
