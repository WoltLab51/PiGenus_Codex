from __future__ import annotations

import argparse

from pigenus.cli.worker_assignment_inspection_commands import (
    WORKER_ASSIGNMENT_INSPECTION_COMMANDS,
    add_worker_assignment_list_command,
    add_worker_assignment_scheduling_eligibility_command,
    handle_worker_assignment_inspection_command,
)
from pigenus.cli.worker_assignment_lifecycle_commands import (
    WORKER_ASSIGNMENT_LIFECYCLE_COMMANDS,
    add_worker_assignment_create_command,
    add_worker_assignment_transition_command,
    handle_worker_assignment_lifecycle_command,
)


WORKER_ASSIGNMENT_COMMANDS = (
    WORKER_ASSIGNMENT_INSPECTION_COMMANDS | WORKER_ASSIGNMENT_LIFECYCLE_COMMANDS
)


def add_worker_assignment_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    add_worker_assignment_list_command(subparsers)
    add_worker_assignment_create_command(subparsers)
    add_worker_assignment_transition_command(subparsers)
    add_worker_assignment_scheduling_eligibility_command(subparsers)


def is_worker_assignment_command(command: str) -> bool:
    return command in WORKER_ASSIGNMENT_COMMANDS


def handle_worker_assignment_command(args: argparse.Namespace) -> int:
    if args.command in WORKER_ASSIGNMENT_INSPECTION_COMMANDS:
        return handle_worker_assignment_inspection_command(args)
    if args.command in WORKER_ASSIGNMENT_LIFECYCLE_COMMANDS:
        return handle_worker_assignment_lifecycle_command(args)
    raise ValueError(f"Unknown worker assignment command: {args.command}")
