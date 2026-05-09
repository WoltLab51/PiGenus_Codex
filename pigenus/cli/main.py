from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pigenus.core.audit import AuditLogger
from pigenus.core.context_registry import ContextRegistry
from pigenus.core.memory_lifecycle_service import MemoryLifecycleService
from pigenus.core.orchestrator import DEMO_TEXT, SimpleOrchestrator
from pigenus.schemas.registry import SchemaRegistry
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, CellRepository, DecisionRepository, MemoryRepository


EMPTY_MEMORY_LIST_MESSAGE = "No memory objects found."
EMPTY_CELL_LIST_MESSAGE = "No cells found."


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

    decision_list = subparsers.add_parser("decision-list", help="List durable decision records.")
    decision_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    cell_list = subparsers.add_parser("cell-list", help="List registered cells without modifying them.")
    cell_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    cell_list.add_argument("--status", default=None, help="Filter by cell lifecycle status.")

    context_list = subparsers.add_parser("context-list", help="List known contexts without modifying them.")
    context_list.add_argument("--db", default=None, help="Optional existing SQLite database path.")
    context_list.add_argument(
        "--show-cells",
        action="store_true",
        help="Show registered cells allowed in each context when --db is provided.",
    )

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
                decision_repository=DecisionRepository(database),
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

    if args.command == "decision-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            decisions = DecisionRepository(database).list()
        finally:
            database.close()

        if not decisions:
            print("No decision records found.")
            return 0

        for decision in decisions:
            context_name = str(decision.context.get("name") or "")
            print(
                f"{decision.decision_id} | {decision.decision_type} | "
                f"{decision.subject_id} | {context_name} | "
                f"{decision.reason} | {decision.source}"
            )
        return 0

    if args.command == "cell-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            cells = CellRepository(database).list()
        finally:
            database.close()

        if args.status is not None:
            cells = [cell for cell in cells if cell.status == args.status]

        if not cells:
            print(EMPTY_CELL_LIST_MESSAGE)
            return 0

        for cell in cells:
            last_used = cell.last_used_at.isoformat() if cell.last_used_at is not None else "-"
            print(
                f"{cell.cell_id} | {cell.status} | "
                f"fitness={cell.fitness:.2f} | last_used_at={last_used}"
            )
        return 0

    if args.command == "context-list":
        cells = []
        if args.show_cells and args.db is not None and Path(args.db).exists():
            database = Database(Path(args.db))
            try:
                cells = CellRepository(database).list()
            except sqlite3.Error:
                cells = []
            finally:
                database.close()

        contexts = ContextRegistry().list_contexts(cells)
        for context in contexts:
            if args.show_cells:
                allowed_cells = ", ".join(context.allowed_cell_ids) or "-"
                print(f"{context.name} | allowed_cells={allowed_cells}")
            else:
                print(context.name)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
