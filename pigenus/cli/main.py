from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pigenus.core.audit import AuditLogger
from pigenus.core.backup import SnapshotBackupService
from pigenus.core.context_registry import ContextRegistry
from pigenus.core.health import HealthChecker
from pigenus.core.memory_lifecycle_service import MemoryLifecycleService
from pigenus.core.orchestrator import DEMO_TEXT, SimpleOrchestrator
from pigenus.core.permission_registry import PermissionRegistry
from pigenus.core.runtime_overview import RuntimeOverviewBuilder
from pigenus.schemas.registry import SchemaRegistry
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    CellRepository,
    DecisionRepository,
    EventRepository,
    MemoryRepository,
)


EMPTY_MEMORY_LIST_MESSAGE = "No memory objects found."
EMPTY_CELL_LIST_MESSAGE = "No cells found."
EMPTY_AUDIT_LIST_MESSAGE = "No audit log rows found."
EMPTY_EVENT_LIST_MESSAGE = "No events found."


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

    overview = subparsers.add_parser("runtime-overview", help="Show a read-only runtime overview.")
    overview.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    health = subparsers.add_parser("health-check", help="Check local runtime storage health.")
    health.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    backup = subparsers.add_parser("backup-create", help="Create a local SQLite runtime snapshot.")
    backup.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    backup.add_argument("--output-dir", default="backups", help="Directory for backup files.")
    backup.add_argument("--name", default=None, help="Optional backup filename.")

    review = subparsers.add_parser("memory-review", help="Apply deterministic memory lifecycle rules.")
    review.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    review.add_argument("--now", default=None, help="ISO timestamp for deterministic review.")

    memory_list = subparsers.add_parser("memory-list", help="List memory objects without modifying them.")
    memory_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    memory_list.add_argument("--status", default=None, help="Filter by memory status.")
    memory_list.add_argument("--context", default=None, help="Filter by context name.")

    event_list = subparsers.add_parser("event-list", help="List events without modifying them.")
    event_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    event_list.add_argument("--object-type", default=None, help="Filter by event object type.")
    event_list.add_argument("--created-by-cell", default=None, help="Filter by creator cell ID.")
    event_list.add_argument("--context", default=None, help="Filter by context name.")
    event_list.add_argument("--limit", type=int, default=None, help="Show only the most recent N events.")

    event_show = subparsers.add_parser("event-show", help="Show one event by ID without modifying it.")
    event_show.add_argument("event_id", help="Event ID to inspect.")
    event_show.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    subparsers.add_parser("schema-list", help="List known schema contracts.")

    decision_list = subparsers.add_parser("decision-list", help="List durable decision records.")
    decision_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    audit_list = subparsers.add_parser("audit-list", help="List audit log rows without modifying them.")
    audit_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    audit_list.add_argument("--actor", default=None, help="Filter by audit actor.")
    audit_list.add_argument("--action", default=None, help="Filter by audit action.")
    audit_list.add_argument("--context", default=None, help="Filter by context name.")

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

    subparsers.add_parser("permission-list", help="List built-in permissions without modifying them.")

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

    if args.command == "runtime-overview":
        database = Database(Path(args.db))
        database.initialize()
        try:
            overview = RuntimeOverviewBuilder(
                events=EventRepository(database),
                memory=MemoryRepository(database),
                cells=CellRepository(database),
                audit=AuditRepository(database),
                decisions=DecisionRepository(database),
            ).build()
        finally:
            database.close()

        print("PiGenus Runtime Overview")
        print(f"Events: {overview.event_count}")
        print(f"Memory objects: {overview.memory_count}")
        print(f"Cells: {overview.cell_count}")
        print(f"Audit logs: {overview.audit_count}")
        print(f"Decision records: {overview.decision_count}")
        print(f"Contexts: {', '.join(overview.contexts) or '-'}")
        print(f"Default permissions: {', '.join(overview.default_permissions) or '-'}")
        return 0

    if args.command == "health-check":
        result = HealthChecker(Path(args.db)).check()
        print("PiGenus Health Check")
        for check in result.checks:
            print(f"OK: {check}")
        for failure in result.failures:
            print(f"FAIL: {failure}")
        print("Status: healthy" if result.ok else "Status: unhealthy")
        return 0 if result.ok else 1

    if args.command == "backup-create":
        try:
            result = SnapshotBackupService(Path(args.db)).create(
                output_dir=Path(args.output_dir),
                name=args.name,
            )
        except (FileExistsError, FileNotFoundError, RuntimeError, sqlite3.Error, OSError) as exc:
            print(f"Backup failed: {exc}")
            return 1

        print("PiGenus Backup")
        print(f"Source: {result.source_path}")
        print(f"Backup: {result.backup_path}")
        print(f"Size bytes: {result.size_bytes}")
        print(f"Integrity: {result.integrity_check}")
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

    if args.command == "event-list":
        if args.limit is not None and args.limit < 1:
            parser.error("--limit must be greater than 0")

        database = Database(Path(args.db))
        database.initialize()
        try:
            events = EventRepository(database).list(
                object_type=args.object_type,
                created_by_cell=args.created_by_cell,
                context=args.context,
                limit=args.limit,
            )
        finally:
            database.close()

        if not events:
            print(EMPTY_EVENT_LIST_MESSAGE)
            return 0

        for event in events:
            context_name = str(event.context.get("name") or "")
            print(
                f"{event.event_id} | {event.created_at.isoformat()} | "
                f"{event.object_type} | {event.created_by_cell} | {context_name}"
            )
        return 0

    if args.command == "event-show":
        database = Database(Path(args.db))
        database.initialize()
        try:
            event = EventRepository(database).get(args.event_id)
        finally:
            database.close()

        if event is None:
            print(f"Event not found: {args.event_id}")
            return 1

        context_name = str(event.context.get("name") or "")
        print(f"Event ID: {event.event_id}")
        print(f"Object type: {event.object_type}")
        print(f"Schema version: {event.schema_version}")
        print(f"Context: {context_name}")
        print(f"Created at: {event.created_at.isoformat()}")
        print(f"Created by cell: {event.created_by_cell}")
        print("Payload:")
        print(json.dumps(event.payload, ensure_ascii=True, indent=2, sort_keys=True))
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

    if args.command == "audit-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            audits = AuditRepository(database).list(
                actor=args.actor,
                action=args.action,
                context=args.context,
            )
        finally:
            database.close()

        if not audits:
            print(EMPTY_AUDIT_LIST_MESSAGE)
            return 0

        for audit in audits:
            context_name = str(audit["context"].get("name") or "")
            print(
                f"{audit['audit_id']} | {audit['created_at']} | "
                f"{audit['actor']} | {audit['action']} | {context_name}"
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

    if args.command == "permission-list":
        rules = PermissionRegistry().list_default_rules()
        if not rules:
            print("No default permissions found.")
            return 0

        for rule in rules:
            print(f"{rule.context} | {rule.action} | source={rule.source}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
