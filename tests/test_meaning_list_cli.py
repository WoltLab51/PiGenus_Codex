from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.systemform import MeaningObject, Sensitivity, TruthStatus
from pigenus.storage.database import Database
from pigenus.storage.repositories import AuditRepository, MeaningRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "meaning-list-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_meaning_list(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "meaning-list",
            "--db",
            str(path),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def meaning(
    meaning_id: str,
    *,
    type: str = "fact",
    room_id: str = "room_developer",
    truth_status: TruthStatus = TruthStatus.VERIFIED,
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
    claim: str | None = None,
) -> MeaningObject:
    return MeaningObject(
        id=meaning_id,
        type=type,
        content={"claim": claim or f"{meaning_id} is persisted."},
        source="test-suite",
        room_id=room_id,
        truth_status=truth_status,
        confidence=0.9,
        sensitivity=sensitivity,
        created_by="cell_meaning_test",
        created_at=datetime(2026, 5, 10, tzinfo=timezone.utc),
    )


def test_meaning_list_reports_empty_database():
    path = db_path("empty")

    result = run_meaning_list(path)

    assert result.returncode == 0
    assert "No meaning objects found." in result.stdout


def test_meaning_list_prints_rows_without_modifying_data():
    path = db_path("rows")
    database = Database(path)
    database.initialize()
    item = meaning("bo_runtime_fact", claim="PiGenus stores meaning.")
    MeaningRepository(database).add(item)
    database.close()

    result = run_meaning_list(path)

    database = Database(path)
    database.initialize()
    assert "bo_runtime_fact | fact | room_developer | verified | internal" in result.stdout
    assert "PiGenus stores meaning." in result.stdout
    assert MeaningRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_meaning_list_filters_by_room_type_truth_status_and_sensitivity():
    path = db_path("filters")
    database = Database(path)
    database.initialize()
    repository = MeaningRepository(database)
    repository.add(meaning("bo_dev_fact"))
    repository.add(
        meaning(
            "bo_family_note",
            type="note",
            room_id="room_family",
            truth_status=TruthStatus.BELIEVED,
            sensitivity=Sensitivity.FAMILY,
        )
    )
    repository.add(
        meaning(
            "bo_private_fact",
            room_id="room_private",
            truth_status=TruthStatus.CONTESTED,
            sensitivity=Sensitivity.PRIVATE,
        )
    )
    database.close()

    result = run_meaning_list(
        path,
        "--room",
        "room_family",
        "--type",
        "note",
        "--truth-status",
        "believed",
        "--sensitivity",
        "family",
    )

    assert "bo_family_note" in result.stdout
    assert "bo_dev_fact" not in result.stdout
    assert "bo_private_fact" not in result.stdout
