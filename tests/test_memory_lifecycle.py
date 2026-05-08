from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from pigenus.core.audit import AuditLogger
from pigenus.core.memory_lifecycle import MemoryLifecycleEngine
from pigenus.core.memory_lifecycle_service import MemoryLifecycleService
from pigenus.schemas.memory import MemoryObject
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase2-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def memory(status: str = "active", **overrides) -> MemoryObject:
    data = {
        "memory_type": "fact",
        "context": {"name": "developer/default"},
        "status": status,
        "content": {"text": "PiGenus ist der Zellkern."},
        "human_summary": "PiGenus ist der Zellkern.",
        **overrides,
    }
    return MemoryObject(**data)


def lifecycle_service(path: Path) -> tuple[Database, MemoryRepository, AuditRepository, MemoryLifecycleService]:
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    audit_repository = AuditRepository(database)
    service = MemoryLifecycleService(
        repository=memory_repository,
        audit_logger=AuditLogger(audit_repository),
    )
    return database, memory_repository, audit_repository, service


def test_manual_transition_allows_documented_paths():
    engine = MemoryLifecycleEngine()
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    item = memory("fresh")

    decision = engine.manual_transition(item, new_status="active", now=now)

    assert decision.changed is True
    assert decision.old_status == "fresh"
    assert decision.new_status == "active"


def test_manual_transition_rejects_undocumented_paths():
    engine = MemoryLifecycleEngine()
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    item = memory("dead")

    with pytest.raises(ValueError):
        engine.manual_transition(item, new_status="active", now=now)


def test_review_due_changes_active_to_watch():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("review-due")
    database, memory_repository, audit_repository, service = lifecycle_service(path)
    item = memory("active", review_due_at=now - timedelta(minutes=1))
    memory_repository.add(item)

    result = service.review(now=now)
    updated = memory_repository.get(item.memory_id)

    assert result.checked == 1
    assert result.changed == 1
    assert updated.status == "watch"
    assert audit_repository.count() == 1
    database.close()


def test_expiry_changes_active_to_dead():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("expiry-active")
    database, memory_repository, audit_repository, service = lifecycle_service(path)
    item = memory("active", expires_at=now - timedelta(minutes=1))
    memory_repository.add(item)

    service.review(now=now)

    assert memory_repository.get(item.memory_id).status == "dead"
    assert audit_repository.list()[0]["action"] == "memory_lifecycle_expire"
    database.close()


def test_expiry_changes_dormant_to_fossil():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("expiry-dormant")
    database, memory_repository, audit_repository, service = lifecycle_service(path)
    item = memory("dormant", expires_at=now - timedelta(minutes=1))
    memory_repository.add(item)

    service.review(now=now)

    assert memory_repository.get(item.memory_id).status == "fossil"
    assert audit_repository.count() == 1
    database.close()


def test_canonical_is_not_changed_by_review_or_expiry():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("canonical")
    database, memory_repository, audit_repository, service = lifecycle_service(path)
    item = memory(
        "canonical",
        review_due_at=now - timedelta(days=1),
        expires_at=now - timedelta(days=1),
    )
    memory_repository.add(item)

    result = service.review(now=now)

    assert result.checked == 1
    assert result.changed == 0
    assert memory_repository.get(item.memory_id).status == "canonical"
    assert audit_repository.count() == 0
    database.close()


def test_manual_transition_to_active_sets_last_validated_and_audit():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("manual-active")
    database, memory_repository, audit_repository, service = lifecycle_service(path)
    item = memory("stale")
    memory_repository.add(item)

    updated = service.manual_transition(item, new_status="active", now=now)
    audit = audit_repository.list()[0]

    assert updated.status == "active"
    assert updated.last_validated_at == now
    assert audit["action"] == "memory_lifecycle_manual_transition"
    assert audit["details"]["old_status"] == "stale"
    assert audit["details"]["new_status"] == "active"
    database.close()


def test_lifecycle_rules_do_not_change_context():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("context-preserved")
    database, memory_repository, _audit_repository, service = lifecycle_service(path)
    item = memory("active", review_due_at=now - timedelta(minutes=1))
    memory_repository.add(item)

    service.review(now=now)

    assert memory_repository.get(item.memory_id).context == item.context
    database.close()


def test_memory_review_cli_runs_and_reports_counts():
    now = datetime(2026, 5, 8, tzinfo=timezone.utc)
    path = db_path("cli-review")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    memory_repository.add(memory("active", review_due_at=now - timedelta(minutes=1)))
    database.close()

    result = subprocess.run(
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

    assert "Memories checked: 1" in result.stdout
    assert "Statuses changed: 1" in result.stdout
