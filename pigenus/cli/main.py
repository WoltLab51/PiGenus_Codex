from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pigenus.core.audit import AuditLogger
from pigenus.core.backup import SnapshotBackupService
from pigenus.core.context_boundary import ContextBoundaryDecisionLogger, ContextBoundaryEngine
from pigenus.core.context_registry import ContextRegistry
from pigenus.core.health import HealthChecker
from pigenus.core.meaning_ingestion import MeaningIngestionPreview
from pigenus.core.memory_lifecycle_service import MemoryLifecycleService
from pigenus.core.orchestrator import DEMO_TEXT, SimpleOrchestrator
from pigenus.core.permission_registry import PermissionRegistry
from pigenus.core.runtime_overview import RuntimeOverviewBuilder
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.core.worker_scheduling_preview import (
    WorkerSchedulingPreviewLogger,
    WorkerSchedulingPreviewService,
    WorkerSchedulingRequest,
)
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.registry import SchemaRegistry
from pigenus.schemas.systemform import Sensitivity, WorkerHeartbeat, WorkerStatus, WorkerType
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    CellRepository,
    DecisionRepository,
    EventRepository,
    MeaningRepository,
    MemoryRepository,
    WorkerRepository,
)


EMPTY_MEMORY_LIST_MESSAGE = "No memory objects found."
EMPTY_CELL_LIST_MESSAGE = "No cells found."
EMPTY_AUDIT_LIST_MESSAGE = "No audit log rows found."
EMPTY_EVENT_LIST_MESSAGE = "No events found."
EMPTY_MEANING_LIST_MESSAGE = "No meaning objects found."
EMPTY_CONTEXT_BOUNDARY_LIST_MESSAGE = "No context boundary decisions found."
EMPTY_WORKER_LIST_MESSAGE = "No workers found."


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

    meaning_list = subparsers.add_parser(
        "meaning-list",
        help="List Systemform meaning objects without modifying them.",
    )
    meaning_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    meaning_list.add_argument("--room", default=None, help="Filter by room ID.")
    meaning_list.add_argument("--type", default=None, help="Filter by meaning type.")
    meaning_list.add_argument("--truth-status", default=None, help="Filter by truth status.")
    meaning_list.add_argument("--sensitivity", default=None, help="Filter by sensitivity.")

    meaning_show = subparsers.add_parser(
        "meaning-show",
        help="Show one Systemform meaning object by ID without modifying it.",
    )
    meaning_show.add_argument("meaning_id", help="Meaning object ID to inspect.")
    meaning_show.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")

    meaning_ingest = subparsers.add_parser(
        "meaning-ingest-memory",
        help="Preview-ingest one stored memory object into the Meaning Store.",
    )
    meaning_ingest.add_argument("memory_id", help="Memory object ID to ingest.")
    meaning_ingest.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    meaning_ingest.add_argument(
        "--created-by",
        default="meaning_ingestion_preview",
        help="Actor ID recorded on the created meaning object.",
    )

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

    guard_decision_list = subparsers.add_parser(
        "guard-decision-list",
        help="List logged guard governance decisions without modifying them.",
    )
    guard_decision_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    guard_decision_list.add_argument("--family", default=None, help="Filter by guard decision family.")
    guard_decision_list.add_argument(
        "--decision",
        choices=("allow", "block", "escalate"),
        default=None,
        help="Filter by final guard decision.",
    )

    guard_decision_summary = subparsers.add_parser(
        "guard-decision-summary",
        help="Summarize logged guard governance decisions without modifying them.",
    )
    guard_decision_summary.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    guard_decision_summary.add_argument("--family", default=None, help="Filter by guard decision family.")
    guard_decision_summary.add_argument(
        "--decision",
        choices=("allow", "block", "escalate"),
        default=None,
        help="Filter by final guard decision.",
    )

    audit_list = subparsers.add_parser("audit-list", help="List audit log rows without modifying them.")
    audit_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    audit_list.add_argument("--actor", default=None, help="Filter by audit actor.")
    audit_list.add_argument("--action", default=None, help="Filter by audit action.")
    audit_list.add_argument("--context", default=None, help="Filter by context name.")

    cell_list = subparsers.add_parser("cell-list", help="List registered cells without modifying them.")
    cell_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    cell_list.add_argument("--status", default=None, help="Filter by cell lifecycle status.")

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

    context_list = subparsers.add_parser("context-list", help="List known contexts without modifying them.")
    context_list.add_argument("--db", default=None, help="Optional existing SQLite database path.")
    context_list.add_argument(
        "--show-cells",
        action="store_true",
        help="Show registered cells allowed in each context when --db is provided.",
    )

    context_check = subparsers.add_parser(
        "context-boundary-check",
        help="Preview-check one registered cell against a context.",
    )
    context_check.add_argument("cell_id", help="Registered cell ID to check.")
    context_check.add_argument("--context", required=True, help="Context name to check.")
    context_check.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    context_check.add_argument(
        "--log",
        action="store_true",
        help="Persist the preview decision to the decision log.",
    )

    context_boundary_list = subparsers.add_parser(
        "context-boundary-list",
        help="List logged context boundary decisions without modifying them.",
    )
    context_boundary_list.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    context_boundary_list.add_argument("--cell", default=None, help="Filter by cell ID.")
    context_boundary_list.add_argument("--context", default=None, help="Filter by context name.")
    context_boundary_list.add_argument("--room", default=None, help="Filter by room ID.")
    context_boundary_list.add_argument(
        "--allowed",
        choices=("yes", "no"),
        default=None,
        help="Filter by allow/deny decision.",
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
                meanings=MeaningRepository(database),
                cells=CellRepository(database),
                audit=AuditRepository(database),
                decisions=DecisionRepository(database),
            ).build()
        finally:
            database.close()

        print("PiGenus Runtime Overview")
        print(f"Events: {overview.event_count}")
        print(f"Memory objects: {overview.memory_count}")
        print(f"Meaning objects: {overview.meaning_count}")
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

    if args.command == "meaning-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            meanings = MeaningRepository(database).list(
                room_id=args.room,
                type=args.type,
                truth_status=args.truth_status,
                sensitivity=args.sensitivity,
            )
        finally:
            database.close()

        if not meanings:
            print(EMPTY_MEANING_LIST_MESSAGE)
            return 0

        for meaning in meanings:
            print(
                f"{meaning.id} | {meaning.type} | {meaning.room_id} | "
                f"{meaning.truth_status.value} | {meaning.sensitivity.value} | "
                f"{_meaning_summary(meaning.content)}"
            )
        return 0

    if args.command == "meaning-show":
        database = Database(Path(args.db))
        database.initialize()
        try:
            meaning = MeaningRepository(database).get(args.meaning_id)
        finally:
            database.close()

        if meaning is None:
            print(f"Meaning object not found: {args.meaning_id}")
            return 1

        print(json.dumps(meaning.model_dump(mode="json"), ensure_ascii=True, indent=2, sort_keys=True))
        return 0

    if args.command == "meaning-ingest-memory":
        database = Database(Path(args.db))
        database.initialize()
        try:
            result = MeaningIngestionPreview(
                memory_repository=MemoryRepository(database),
                meaning_repository=MeaningRepository(database),
            ).ingest_memory_by_id(args.memory_id, created_by=args.created_by)
        finally:
            database.close()

        if result is None:
            print(f"Memory object not found: {args.memory_id}")
            return 1

        status = "created" if result.created else "already_exists"
        print(f"Meaning ingestion: {status}")
        print(f"Memory: {result.source_memory_id}")
        print(f"Meaning: {result.meaning.id}")
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

    if args.command == "guard-decision-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            decisions = [
                decision
                for decision in DecisionRepository(database).list()
                if decision.decision_type == "governance_decision"
            ]
        finally:
            database.close()

        decisions = _filter_guard_decisions(
            decisions,
            family=args.family,
            decision=args.decision,
        )

        if not decisions:
            print("No guard decision records found.")
            return 0

        for decision in decisions:
            details = decision.details
            governance = _governance_decision_details(details)
            guard_decision = str(details.get("decision") or governance.get("decision") or "")
            family = _guard_decision_family(decision)
            room_id = str(details.get("room_id") or governance.get("room_id") or "")
            print(
                f"{decision.decision_id} | {guard_decision} | family={family} | "
                f"{decision.actor} | {room_id} | {decision.reason}"
            )
        return 0

    if args.command == "guard-decision-summary":
        database = Database(Path(args.db))
        database.initialize()
        try:
            decisions = [
                decision
                for decision in DecisionRepository(database).list()
                if decision.decision_type == "governance_decision"
            ]
        finally:
            database.close()

        decisions = _filter_guard_decisions(
            decisions,
            family=args.family,
            decision=args.decision,
        )

        if not decisions:
            print("No guard decision records found.")
            return 0

        for decision_name, family, count in _summarize_guard_decisions(decisions):
            print(f"{decision_name} | family={family} | count={count}")
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

    if args.command == "worker-list":
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

    if args.command == "worker-show":
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

    if args.command == "worker-scheduling-preview":
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

    if args.command == "context-boundary-check":
        database = Database(Path(args.db))
        database.initialize()
        try:
            cell = CellRepository(database).get(args.cell_id)
            if cell is None:
                print(f"Cell not found: {args.cell_id}")
                return 1

            decision = ContextBoundaryEngine().check(
                cell=cell,
                context={"name": args.context},
            )
            if args.log:
                ContextBoundaryDecisionLogger(DecisionRepository(database)).add(decision)
        finally:
            database.close()

        print("Context Boundary Check")
        print(f"Cell: {decision.cell_id}")
        print(f"Context: {decision.context}")
        print(f"Room: {decision.room_id}")
        print(f"Protection level: {decision.protection_level}")
        print(f"Allowed: {'yes' if decision.allowed else 'no'}")
        print(f"Reason: {decision.reason}")
        return 0

    if args.command == "context-boundary-list":
        database = Database(Path(args.db))
        database.initialize()
        try:
            decisions = [
                decision
                for decision in DecisionRepository(database).list()
                if decision.decision_type == "context_boundary"
            ]
        finally:
            database.close()

        decisions = _filter_context_boundary_decisions(
            decisions,
            cell_id=args.cell,
            context=args.context,
            room_id=args.room,
            allowed=args.allowed,
        )

        if not decisions:
            print(EMPTY_CONTEXT_BOUNDARY_LIST_MESSAGE)
            return 0

        for decision in decisions:
            details = decision.details
            boundary = details.get("context_boundary", {})
            allowed = "yes" if bool(details.get("allowed")) else "no"
            print(
                f"{decision.decision_id} | {decision.actor} | "
                f"{boundary.get('context', '')} | {details.get('room_id', '')} | "
                f"allowed={allowed} | {decision.reason}"
            )
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


def _meaning_summary(content: dict[str, object]) -> str:
    for key in ("claim", "text", "summary"):
        value = content.get(key)
        if value is not None:
            return str(value)
    return json.dumps(content, ensure_ascii=True, sort_keys=True)


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


def _filter_context_boundary_decisions(
    decisions: list[DecisionRecord],
    *,
    cell_id: str | None,
    context: str | None,
    room_id: str | None,
    allowed: str | None,
) -> list[DecisionRecord]:
    filtered: list[DecisionRecord] = []
    for decision in decisions:
        details = decision.details
        boundary = details.get("context_boundary", {})
        if cell_id is not None and decision.actor != cell_id:
            continue
        if context is not None and boundary.get("context") != context:
            continue
        if room_id is not None and details.get("room_id") != room_id:
            continue
        if allowed is not None and bool(details.get("allowed")) != (allowed == "yes"):
            continue
        filtered.append(decision)
    return filtered


def _filter_guard_decisions(
    decisions: list[DecisionRecord],
    *,
    family: str | None,
    decision: str | None,
) -> list[DecisionRecord]:
    filtered: list[DecisionRecord] = []
    for record in decisions:
        details = record.details
        governance = _governance_decision_details(details)
        record_decision = str(details.get("decision") or governance.get("decision") or "")
        if family is not None and _guard_decision_family(record) != family:
            continue
        if decision is not None and record_decision != decision:
            continue
        filtered.append(record)
    return filtered


def _guard_decision_family(decision: DecisionRecord) -> str:
    details = decision.details
    family = details.get("family")
    if family:
        return str(family)

    governance = _governance_decision_details(details)
    governance_details = governance.get("details", {})
    family = governance_details.get("family") if isinstance(governance_details, dict) else None
    if family:
        return str(family)

    trace = details.get("trace", [])
    if not isinstance(trace, list):
        return ""

    for step in trace:
        if not isinstance(step, dict):
            continue
        if step.get("decision") in {"block", "escalate"} and step.get("family"):
            return str(step["family"])
    for step in trace:
        if isinstance(step, dict) and step.get("family"):
            return str(step["family"])
    return ""


def _guard_decision_name(decision: DecisionRecord) -> str:
    details = decision.details
    governance = _governance_decision_details(details)
    return str(details.get("decision") or governance.get("decision") or "")


def _summarize_guard_decisions(decisions: list[DecisionRecord]) -> list[tuple[str, str, int]]:
    counts: dict[tuple[str, str], int] = {}
    for decision in decisions:
        key = (_guard_decision_name(decision), _guard_decision_family(decision))
        counts[key] = counts.get(key, 0) + 1
    return [
        (decision_name, family, count)
        for (decision_name, family), count in sorted(counts.items())
    ]


def _governance_decision_details(details: dict[str, object]) -> dict[str, object]:
    governance = details.get("governance_decision", {})
    if isinstance(governance, dict):
        return governance
    return {}


if __name__ == "__main__":
    raise SystemExit(main())
