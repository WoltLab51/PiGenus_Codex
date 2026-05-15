from __future__ import annotations

import argparse
import json
from pathlib import Path

from pigenus.core.meaning_ingestion import MeaningIngestionPreview
from pigenus.storage.database import Database
from pigenus.storage.repositories import MeaningRepository, MemoryRepository


EMPTY_MEANING_LIST_MESSAGE = "No meaning objects found."
MEANING_COMMANDS = {
    "meaning-list",
    "meaning-show",
    "meaning-ingest-memory",
}


def add_meaning_commands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
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


def is_meaning_command(command: str) -> bool:
    return command in MEANING_COMMANDS


def handle_meaning_command(args: argparse.Namespace) -> int:
    if args.command == "meaning-list":
        return _handle_meaning_list(args)
    if args.command == "meaning-show":
        return _handle_meaning_show(args)
    if args.command == "meaning-ingest-memory":
        return _handle_meaning_ingest_memory(args)
    raise ValueError(f"Unknown meaning command: {args.command}")


def _handle_meaning_list(args: argparse.Namespace) -> int:
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


def _handle_meaning_show(args: argparse.Namespace) -> int:
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


def _handle_meaning_ingest_memory(args: argparse.Namespace) -> int:
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


def _meaning_summary(content: dict[str, object]) -> str:
    for key in ("claim", "text", "summary"):
        value = content.get(key)
        if value is not None:
            return str(value)
    return json.dumps(content, ensure_ascii=True, sort_keys=True)
