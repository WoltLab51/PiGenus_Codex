from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.events import Event
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, EventRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase29-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_event_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "event-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def run_event_show(path: Path, event_id: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "event-show",
            event_id,
            "--db",
            str(path),
        ],
        capture_output=True,
        text=True,
    )


def task_event(
    text: str,
    *,
    created_by_cell: str = "input_cell@0.1.0",
    context: str = "developer/default",
) -> Event:
    return Event(
        object_type="TaskRequest",
        context={"name": context},
        created_by_cell=created_by_cell,
        payload={"raw_text": text, "action": "memory_write"},
    )


def response_event(memory_id: str) -> Event:
    return Event(
        object_type="HumanResponse",
        context={"name": "developer/default"},
        created_by_cell="explain_cell@0.1.0",
        payload={"response": "Gespeichert.", "memory_id": memory_id},
    )


def test_event_repository_gets_and_lists_with_filters_and_limit():
    database = Database(db_path("repository"))
    database.initialize()
    repository = EventRepository(database)
    first = task_event("Merke dir: eins")
    second = response_event("mem_example")
    third = task_event("Merke dir: trading", context="trading/default")
    repository.add(first)
    repository.add(second)
    repository.add(third)

    filtered = repository.list(object_type="TaskRequest", context="trading/default", limit=1)

    assert repository.get(second.event_id) == second
    assert filtered == [third]
    database.close()


def test_event_list_cli_reports_empty_database():
    result = run_event_list(db_path("empty"))

    assert "No events found." in result.stdout


def test_event_list_cli_prints_recent_events_without_modifying_storage():
    path = db_path("rows")
    database = Database(path)
    database.initialize()
    repository = EventRepository(database)
    event = task_event("Merke dir: PiGenus ist der Zellkern.")
    repository.add(event)
    database.close()

    result = run_event_list(path)

    database = Database(path)
    assert event.event_id in result.stdout
    assert "TaskRequest | input_cell@0.1.0 | developer/default" in result.stdout
    assert EventRepository(database).count() == 1
    assert MemoryRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_event_list_cli_filters_and_limits_events():
    path = db_path("filters")
    database = Database(path)
    database.initialize()
    repository = EventRepository(database)
    hidden = task_event("Merke dir: hidden")
    shown = task_event(
        "Merke dir: visible",
        created_by_cell="trading_input@0.1.0",
        context="trading/default",
    )
    repository.add(hidden)
    repository.add(shown)
    database.close()

    result = run_event_list(
        path,
        "--object-type",
        "TaskRequest",
        "--created-by-cell",
        "trading_input@0.1.0",
        "--context",
        "trading/default",
        "--limit",
        "1",
    )

    assert shown.event_id in result.stdout
    assert hidden.event_id not in result.stdout


def test_event_show_cli_prints_one_event_with_payload_json():
    path = db_path("show")
    database = Database(path)
    database.initialize()
    event = task_event("Merke dir: PiGenus ist der Zellkern.")
    EventRepository(database).add(event)
    database.close()

    result = run_event_show(path, event.event_id)

    assert result.returncode == 0
    assert f"Event ID: {event.event_id}" in result.stdout
    assert "Object type: TaskRequest" in result.stdout
    assert '"raw_text": "Merke dir: PiGenus ist der Zellkern."' in result.stdout


def test_event_show_cli_returns_clean_error_for_unknown_event_id():
    result = run_event_show(db_path("missing"), "evt_missing")

    assert result.returncode == 1
    assert "Event not found: evt_missing" in result.stdout
    assert result.stderr == ""
