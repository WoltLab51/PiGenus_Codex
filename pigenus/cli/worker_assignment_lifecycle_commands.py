from __future__ import annotations

import argparse
from pathlib import Path

from pigenus.core.audit import AuditLogger
from pigenus.core.worker_assignment_creator import WorkerAssignmentCreator
from pigenus.core.worker_assignment_status_transition import (
    WorkerAssignmentStatusTransitionService,
)
from pigenus.core.worker_assignment_status_transition_validator import (
    WorkerAssignmentStatusTransitionValidator,
)
from pigenus.core.worker_assignment_validator import WorkerAssignmentValidator
from pigenus.schemas.systemform import Sensitivity, WorkerAssignment, WorkerAssignmentStatus
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    DecisionRepository,
    WorkerAssignmentRepository,
    WorkerRepository,
)


WORKER_ASSIGNMENT_LIFECYCLE_COMMANDS = {
    "worker-assignment-create",
    "worker-assignment-transition",
}


def add_worker_assignment_lifecycle_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    add_worker_assignment_create_command(subparsers)
    add_worker_assignment_transition_command(subparsers)


def add_worker_assignment_create_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    worker_assignment_create = subparsers.add_parser(
        "worker-assignment-create",
        help="Create pending worker assignment intent after validation.",
    )
    worker_assignment_create.add_argument("worker_id", help="Worker ID to assign.")
    worker_assignment_create.add_argument("capability", help="Capability to assign.")
    worker_assignment_create.add_argument(
        "governance_decision_id",
        help="Matching worker execution preflight decision ID.",
    )
    worker_assignment_create.add_argument(
        "--db",
        default="pigenus.sqlite3",
        help="SQLite database path.",
    )
    worker_assignment_create.add_argument(
        "--room",
        required=True,
        help="Room ID for the assignment intent.",
    )
    worker_assignment_create.add_argument(
        "--actor",
        default="worker_assignment_create_cli",
        help="Actor ID creating the assignment intent.",
    )
    worker_assignment_create.add_argument(
        "--assignment-id",
        default=None,
        help="Optional deterministic assignment ID.",
    )
    worker_assignment_create.add_argument("--runtime", default=None, help="Required runtime.")
    worker_assignment_create.add_argument(
        "--sensitivity",
        choices=tuple(sensitivity.value for sensitivity in Sensitivity),
        default=None,
        help="Required sensitivity ceiling.",
    )
    worker_assignment_create.add_argument(
        "--network-required",
        action="store_true",
        help="Require worker network access.",
    )
    worker_assignment_create.add_argument(
        "--event-id",
        default=None,
        help="Optional event ID linked to the assignment intent.",
    )
    worker_assignment_create.add_argument(
        "--context-stack",
        default=None,
        help="Optional context stack ID linked to the assignment intent.",
    )
    worker_assignment_create.add_argument(
        "--reason",
        default=None,
        help="Optional human-readable assignment reason.",
    )


def add_worker_assignment_transition_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    worker_assignment_transition = subparsers.add_parser(
        "worker-assignment-transition",
        help="Apply a validated worker assignment status transition.",
    )
    worker_assignment_transition.add_argument("assignment_id", help="Assignment ID to update.")
    worker_assignment_transition.add_argument(
        "target_status",
        choices=tuple(status.value for status in WorkerAssignmentStatus),
        help="Target assignment status.",
    )
    worker_assignment_transition.add_argument(
        "--db",
        default="pigenus.sqlite3",
        help="SQLite database path.",
    )
    worker_assignment_transition.add_argument(
        "--actor",
        default="worker_assignment_transition_cli",
        help="Actor ID applying the status transition.",
    )
    worker_assignment_transition.add_argument(
        "--reason",
        default=None,
        help="Optional human-readable transition reason.",
    )


def handle_worker_assignment_lifecycle_command(args: argparse.Namespace) -> int:
    if args.command == "worker-assignment-create":
        return _handle_worker_assignment_create(args)
    if args.command == "worker-assignment-transition":
        return _handle_worker_assignment_transition(args)
    raise ValueError(f"Unknown worker assignment lifecycle command: {args.command}")


def _handle_worker_assignment_create(args: argparse.Namespace) -> int:
    assignment = _assignment_from_args(args)
    database = Database(Path(args.db))
    database.initialize()
    try:
        creator = WorkerAssignmentCreator(
            validator=WorkerAssignmentValidator(
                workers=WorkerRepository(database),
                decisions=DecisionRepository(database),
            ),
            assignments=WorkerAssignmentRepository(database),
            audit_logger=AuditLogger(AuditRepository(database)),
        )
        result = creator.create(assignment)
    finally:
        database.close()

    if not result.created:
        print("Worker Assignment Rejected")
        print(f"Assignment: {assignment.id}")
        print(f"Reasons: {','.join(result.validation.reasons)}")
        return 1

    print("Worker Assignment Created")
    print(f"Assignment: {assignment.id}")
    print(f"Worker: {assignment.worker_id}")
    print(f"Capability: {assignment.capability}")
    print(f"Room: {assignment.room_id}")
    print(f"Status: {assignment.status.value}")
    print(f"Governance decision: {assignment.governance_decision_id}")
    print(f"Audit: {result.audit_id}")
    return 0


def _handle_worker_assignment_transition(args: argparse.Namespace) -> int:
    database = Database(Path(args.db))
    database.initialize()
    try:
        service = WorkerAssignmentStatusTransitionService(
            validator=WorkerAssignmentStatusTransitionValidator(),
            assignments=WorkerAssignmentRepository(database),
            audit_logger=AuditLogger(AuditRepository(database)),
        )
        result = service.transition(
            args.assignment_id,
            args.target_status,
            actor_id=args.actor,
            reason=args.reason,
        )
    finally:
        database.close()

    if not result.transitioned:
        print("Worker Assignment Transition Rejected")
        print(f"Assignment: {args.assignment_id}")
        print(f"Target status: {args.target_status}")
        print(f"Reasons: {','.join(result.validation.reasons)}")
        return 1

    assert result.assignment is not None
    print("Worker Assignment Transitioned")
    print(f"Assignment: {result.assignment.id}")
    print(f"Worker: {result.assignment.worker_id}")
    print(f"Capability: {result.assignment.capability}")
    print(f"Room: {result.assignment.room_id}")
    print(f"Previous status: {result.validation.details['current_status']}")
    print(f"Status: {result.assignment.status.value}")
    print(f"Audit: {result.audit_id}")
    return 0


def _assignment_from_args(args: argparse.Namespace) -> WorkerAssignment:
    kwargs = {}
    if args.assignment_id is not None:
        kwargs["id"] = args.assignment_id
    return WorkerAssignment(
        **kwargs,
        worker_id=args.worker_id,
        capability=args.capability,
        room_id=args.room,
        governance_decision_id=args.governance_decision_id,
        created_by_actor_id=args.actor,
        status=WorkerAssignmentStatus.PENDING,
        event_id=args.event_id,
        context_stack_id=args.context_stack,
        required_runtime=args.runtime,
        sensitivity=Sensitivity(args.sensitivity) if args.sensitivity is not None else None,
        network_required=args.network_required,
        reason=args.reason,
    )
