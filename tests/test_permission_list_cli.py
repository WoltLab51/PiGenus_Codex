from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.permission_registry import PermissionRegistry
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MemoryRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase27-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_permission_list() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "permission-list",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_permission_registry_lists_default_rules_from_engine():
    rules = PermissionRegistry().list_default_rules()

    assert [(rule.context, rule.action, rule.source) for rule in rules] == [
        ("developer/default", "memory_write", "default")
    ]


def test_permission_list_cli_prints_default_permissions():
    result = run_permission_list()

    assert "developer/default | memory_write | source=default" in result.stdout


def test_permission_list_cli_does_not_mutate_existing_storage():
    path = db_path("permission-list")
    database = Database(path)
    database.initialize()
    database.close()

    result = run_permission_list()

    database = Database(path)
    assert result.returncode == 0
    assert MemoryRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()
