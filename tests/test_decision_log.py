from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.memory import MemoryObject
from pigenus.storage.database import Database
from pigenus.storage.repositories import DecisionRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase24-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def memory_with_review_due(now: datetime) -> MemoryObject:
    return MemoryObject(
        memory_type="fact",
        context={"name": "developer/default"},
        status="active",
        content={"text": "PiGenus ist der Zellkern."},
        human_summary="PiGenus ist der Zellkern.",
        review_due_at=now - timedelta(minutes=1),
    )


def test_decision_repository_stores_and_lists_decision_records():
    path = db_path("repository")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    decision = DecisionRecord(
        decision_type="memory_lifecycle_status_change",
        context={"name": "developer/default"},
        subject_id="mem_example",
        actor="memory_lifecycle@0.1.0",
        reason="review_due",
        source="automatic",
        details={"old_status": "active", "new_status": "watch"},
    )

    repository.add(decision)

    assert repository.count() == 1
    assert repository.list()[0] == decision
    database.close()


def test_memory_review_cli_writes_decision_records():
    now = datetime(2026, 5, 9, tzinfo=timezone.utc)
    path = db_path("review-cli")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    item = memory_with_review_due(now)
    memory_repository.add(item)
    database.close()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "memory-review",
            "--db",
            str(path),
            "--now",
            now.isoformat(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()

    assert len(decisions) == 1
    assert decisions[0].subject_id == item.memory_id
    assert decisions[0].reason == "review_due"
    assert decisions[0].details["old_status"] == "active"
    assert decisions[0].details["new_status"] == "watch"
    database.close()


def test_decision_list_cli_is_read_only_and_stable():
    now = datetime(2026, 5, 9, tzinfo=timezone.utc)
    path = db_path("decision-list")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    decision = DecisionRecord(
        decision_type="memory_lifecycle_status_change",
        context={"name": "developer/default"},
        subject_id="mem_example",
        actor="memory_lifecycle@0.1.0",
        reason="expired",
        source="automatic",
        created_at=now,
        details={"old_status": "active", "new_status": "dead"},
    )
    repository.add(decision)
    database.close()

    result = subprocess.run(
        [sys.executable, "-m", "pigenus.cli.main", "decision-list", "--db", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )

    database = Database(path)
    database.initialize()
    assert decision.decision_id in result.stdout
    assert "memory_lifecycle_status_change | mem_example | developer/default | expired | automatic" in result.stdout
    assert DecisionRepository(database).count() == 1
    database.close()


def test_decision_list_cli_reports_empty_database():
    path = db_path("empty")

    result = subprocess.run(
        [sys.executable, "-m", "pigenus.cli.main", "decision-list", "--db", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "No decision records found." in result.stdout
