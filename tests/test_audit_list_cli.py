from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase28-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_audit_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "audit-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def add_audit(
    repository: AuditRepository,
    *,
    actor: str,
    action: str,
    context: str = "developer/default",
) -> str:
    return repository.add(
        actor=actor,
        action=action,
        context={"name": context},
        details={"example": True},
    )


def test_audit_repository_lists_with_filters():
    database = Database(db_path("repository"))
    database.initialize()
    repository = AuditRepository(database)
    memory_audit_id = add_audit(
        repository,
        actor="memory_writer@0.1.0",
        action="memory_write",
    )
    add_audit(
        repository,
        actor="rule_guard@0.1.0",
        action="permission_check",
        context="trading/default",
    )

    audits = repository.list(actor="memory_writer@0.1.0", action="memory_write")

    assert len(audits) == 1
    assert audits[0]["audit_id"] == memory_audit_id
    database.close()


def test_audit_list_cli_reports_empty_database():
    result = run_audit_list(db_path("empty"))

    assert "No audit log rows found." in result.stdout


def test_audit_list_cli_prints_rows_without_modifying_storage():
    path = db_path("rows")
    database = Database(path)
    database.initialize()
    audit_repository = AuditRepository(database)
    audit_id = add_audit(
        audit_repository,
        actor="memory_writer@0.1.0",
        action="memory_write",
    )
    database.close()

    result = run_audit_list(path)

    database = Database(path)
    assert audit_id in result.stdout
    assert "memory_writer@0.1.0 | memory_write | developer/default" in result.stdout
    assert AuditRepository(database).count() == 1
    assert MemoryRepository(database).count() == 0
    database.close()


def test_audit_list_cli_filters_by_actor_action_and_context():
    path = db_path("filters")
    database = Database(path)
    database.initialize()
    audit_repository = AuditRepository(database)
    add_audit(
        audit_repository,
        actor="memory_writer@0.1.0",
        action="memory_write",
    )
    add_audit(
        audit_repository,
        actor="rule_guard@0.1.0",
        action="permission_check",
    )
    add_audit(
        audit_repository,
        actor="memory_writer@0.1.0",
        action="memory_write",
        context="trading/default",
    )
    database.close()

    result = run_audit_list(
        path,
        "--actor",
        "memory_writer@0.1.0",
        "--action",
        "memory_write",
        "--context",
        "trading/default",
    )

    assert "trading/default" in result.stdout
    assert "developer/default" not in result.stdout
    assert "rule_guard@0.1.0" not in result.stdout
