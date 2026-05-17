from __future__ import annotations

import argparse
from pathlib import Path

from pigenus.core.worker_assignment_scheduling_eligibility import (
    WorkerAssignmentSchedulingEligibilityLogger,
    WorkerAssignmentSchedulingEligibilityValidator,
)
from pigenus.schemas.systemform import WorkerAssignmentStatus
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    DecisionRepository,
    WorkerAssignmentRepository,
    WorkerRepository,
)


EMPTY_WORKER_ASSIGNMENT_LIST_MESSAGE = "No worker assignments found."
WORKER_ASSIGNMENT_INSPECTION_COMMANDS = {
    "worker-assignment-list",
    "worker-assignment-scheduling-eligibility",
}


def add_worker_assignment_inspection_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    add_worker_assignment_list_command(subparsers)
    add_worker_assignment_scheduling_eligibility_command(subparsers)


def add_worker_assignment_list_command(
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


def add_worker_assignment_scheduling_eligibility_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    worker_assignment_scheduling_eligibility = subparsers.add_parser(
        "worker-assignment-scheduling-eligibility",
        help="Inspect read-only scheduling eligibility for one assignment.",
    )
    worker_assignment_scheduling_eligibility.add_argument(
        "assignment_id",
        help="Assignment ID to inspect.",
    )
    worker_assignment_scheduling_eligibility.add_argument(
        "--db",
        default="pigenus.sqlite3",
        help="SQLite database path.",
    )
    worker_assignment_scheduling_eligibility.add_argument(
        "--log",
        action="store_true",
        help="Persist loggable eligibility results to the decision log.",
    )
    worker_assignment_scheduling_eligibility.add_argument(
        "--actor",
        default="worker_assignment_scheduling_eligibility_cli",
        help="Actor ID for the eligibility governance decision.",
    )
    worker_assignment_scheduling_eligibility.add_argument(
        "--event-id",
        default=None,
        help="Optional event ID for the logged eligibility decision.",
    )


def handle_worker_assignment_inspection_command(args: argparse.Namespace) -> int:
    if args.command == "worker-assignment-list":
        return _handle_worker_assignment_list(args)
    if args.command == "worker-assignment-scheduling-eligibility":
        return _handle_worker_assignment_scheduling_eligibility(args)
    raise ValueError(f"Unknown worker assignment inspection command: {args.command}")


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


def _handle_worker_assignment_scheduling_eligibility(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    logged_record = None
    try:
        decisions = DecisionRepository(database)
        result = WorkerAssignmentSchedulingEligibilityValidator(
            assignments=WorkerAssignmentRepository(database),
            workers=WorkerRepository(database),
            decisions=decisions,
        ).validate(args.assignment_id)
        if args.log:
            logged_record = WorkerAssignmentSchedulingEligibilityLogger(decisions).add(
                result,
                actor_id=args.actor,
                event_id=args.event_id,
            )
    finally:
        database.close()

    print("Worker Assignment Scheduling Eligibility")
    print(f"Assignment: {result.assignment_id}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Eligible: {'yes' if result.eligible else 'no'}")
    print(f"Reasons: {','.join(result.reasons)}")
    worker_id = result.details.get("worker_id", "-")
    capability = result.details.get("capability", "-")
    room_id = result.details.get("room_id", "-")
    governance_decision_id = result.details.get("governance_decision_id", "-")
    print(f"Worker: {worker_id}")
    print(f"Capability: {capability}")
    print(f"Room: {room_id}")
    print(f"Governance decision: {governance_decision_id}")
    if args.log:
        logged_value = (
            logged_record.decision_id
            if logged_record is not None
            else "skipped"
        )
        print(f"Logged decision: {logged_value}")
    return 0
