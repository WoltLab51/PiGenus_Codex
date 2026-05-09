from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from pigenus.core.audit import AuditLogger
from pigenus.core.memory_lifecycle_service import MemoryLifecycleService
from pigenus.core.orchestrator import DEMO_TEXT, SimpleOrchestrator
from pigenus.schemas.registry import SchemaRegistry
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


EMPTY_MEMORY_LIST_MESSAGE = "No memory objects found."


def parse_datetime(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("run-demo", help="Run the Phase 1 local memory demo.")
    demo.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    demo.add_argument("--text", default=DEMO_TEXT, help="Input text for the demo flow.")

    review = subparsers.add_parser("memory-review", help="Apply deterministic memory lifecycle rules.")
    review.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    review.add_argument("--now", default=None, help="ISO timestamp for deterministic review.")

    memory_list = subparsers.add_parser("memory-list", help="List memory objects without modifying them.")
    memory_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    memory_list.add_argument("--status", default=None, help="Filter by memory status.")
    memory_list.add_argument("--context", default=None, help="Filter by context name.")

    subparsers.add_parser("schema-list", help="List known schema contracts.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-demo":
        orchestrator = SimpleOrchestrator(Path(args.db))
        try:
            result = orchestrator.run_demo(args.text)
        finally:
            orchestrator.close()

        print(f"Final response: {result.final_response}")
        print(f"Created memory object ID: {result.memory_id}")
        print(f"Events stored: {result.events_stored}")
        return 0

    if args.command == "memory-review":
        database = Database(Path(args.db))
        database.initialize()
        try:
            service = MemoryLifecycleService(
                repository=MemoryRepository(database),
                audit_logger=AuditLogger(AuditRepository(database)),
            )
            result = service.review(now=parse_datetime(args.now))
        finally:
            database.close()

        print(f"Memories checked: {result.checked}")
        print(f"Statuses changed: {result.changed}")
        return 0

    if args.command == "memory-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            memories = MemoryRepository(database).list()
        finally:
            database.close()

        if args.status is not None:
            memories = [memory for memory in memories if memory.status == args.status]
        if args.context is not None:
            memories = [
                memory
                for memory in memories
                if str(memory.context.get("name") or "") == args.context
            ]

        if not memories:
            print(EMPTY_MEMORY_LIST_MESSAGE)
            return 0

        for memory in memories:
            context_name = str(memory.context.get("name") or "")
            print(
                f"{memory.memory_id} | {memory.status} | "
                f"{context_name} | {memory.human_summary}"
            )
        return 0

    if args.command == "schema-list":
        registry = SchemaRegistry()
        for contract in registry.list_event_contracts():
            required = ", ".join(contract.required_payload_keys) or "-"
            print(
                f"{contract.object_type} | "
                f"schema {contract.schema_version} | "
                f"required: {required}"
            )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
