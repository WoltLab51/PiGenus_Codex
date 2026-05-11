from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.cells.input_cell import InputCell
from pigenus.core.context_boundary import (
    ContextBoundaryDecisionLogger,
    ContextBoundaryEngine,
    context_boundary_decision_to_record,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import CellRepository, DecisionRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "context-boundary-logging-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_context_boundary_check(path: Path, cell_id: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "context-boundary-check",
            cell_id,
            "--db",
            str(path),
            *args,
        ],
        capture_output=True,
        text=True,
    )


def run_context_boundary_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "context-boundary-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def register_input_cell(path: Path) -> str:
    database = Database(path)
    database.initialize()
    cell = InputCell().spec
    CellRepository(database).add(cell)
    database.close()
    return cell.cell_id


def test_context_boundary_decision_record_preserves_room_metadata():
    decision = ContextBoundaryEngine().check(
        cell=InputCell().spec,
        context={"name": "developer/default"},
    )

    record = context_boundary_decision_to_record(decision)

    assert record.decision_type == "context_boundary"
    assert record.actor == "input_cell@0.1.0"
    assert record.reason == "context_allowed"
    assert record.details["allowed"] is True
    assert record.details["room_id"] == "room_developer"
    assert record.details["protection_level"] == "medium"
    assert record.details["context_boundary"]["context"] == "developer/default"


def test_context_boundary_decision_logger_persists_decision_record():
    path = db_path("logger")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    decision = ContextBoundaryEngine().check(
        cell=InputCell().spec,
        context={"name": "trading/default"},
    )

    record = ContextBoundaryDecisionLogger(repository).add(decision)
    stored = repository.list()

    assert record.reason == "context_not_allowed"
    assert len(stored) == 1
    assert stored[0].details["allowed"] is False
    assert stored[0].details["room_id"] == "room_trading"
    database.close()


def test_context_boundary_check_cli_reports_decision_without_logging_by_default():
    path = db_path("cli-read-only")
    cell_id = register_input_cell(path)

    result = run_context_boundary_check(path, cell_id, "--context", "developer/default")

    database = Database(path)
    database.initialize()
    assert result.returncode == 0
    assert "Context Boundary Check" in result.stdout
    assert "Allowed: yes" in result.stdout
    assert "Room: room_developer" in result.stdout
    assert DecisionRepository(database).count() == 0
    database.close()


def test_context_boundary_check_cli_can_log_preview_decision():
    path = db_path("cli-log")
    cell_id = register_input_cell(path)

    result = run_context_boundary_check(path, cell_id, "--context", "trading/default", "--log")

    database = Database(path)
    database.initialize()
    decisions = DecisionRepository(database).list()
    assert result.returncode == 0
    assert "Allowed: no" in result.stdout
    assert "Reason: context_not_allowed" in result.stdout
    assert len(decisions) == 1
    assert decisions[0].decision_type == "context_boundary"
    assert decisions[0].details["room_id"] == "room_trading"
    database.close()


def test_context_boundary_check_cli_returns_clean_error_for_unknown_cell():
    result = run_context_boundary_check(
        db_path("cli-missing-cell"),
        "cell_missing",
        "--context",
        "developer/default",
    )

    assert result.returncode == 1
    assert "Cell not found: cell_missing" in result.stdout
    assert result.stderr == ""


def test_context_boundary_list_cli_reports_empty_database():
    result = run_context_boundary_list(db_path("empty-list"))

    assert result.returncode == 0
    assert "No context boundary decisions found." in result.stdout


def test_context_boundary_list_cli_prints_logged_decisions_without_modifying_data():
    path = db_path("list")
    cell_id = register_input_cell(path)
    run_context_boundary_check(path, cell_id, "--context", "developer/default", "--log")

    result = run_context_boundary_list(path)

    database = Database(path)
    database.initialize()
    assert "input_cell@0.1.0 | developer/default | room_developer | allowed=yes" in result.stdout
    assert "context_allowed" in result.stdout
    assert DecisionRepository(database).count() == 1
    database.close()


def test_context_boundary_list_cli_filters_by_cell_context_room_and_allowed():
    path = db_path("filters")
    cell_id = register_input_cell(path)
    run_context_boundary_check(path, cell_id, "--context", "developer/default", "--log")
    run_context_boundary_check(path, cell_id, "--context", "trading/default", "--log")

    result = run_context_boundary_list(
        path,
        "--cell",
        "input_cell@0.1.0",
        "--context",
        "trading/default",
        "--room",
        "room_trading",
        "--allowed",
        "no",
    )

    assert "trading/default" in result.stdout
    assert "allowed=no" in result.stdout
    assert "developer/default" not in result.stdout


def test_context_boundary_list_cli_allowed_filter_can_select_allowed_decisions():
    path = db_path("allowed-filter")
    cell_id = register_input_cell(path)
    run_context_boundary_check(path, cell_id, "--context", "developer/default", "--log")
    run_context_boundary_check(path, cell_id, "--context", "trading/default", "--log")

    result = run_context_boundary_list(path, "--allowed", "yes")

    assert "developer/default" in result.stdout
    assert "trading/default" not in result.stdout
