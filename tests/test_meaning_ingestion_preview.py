from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from pigenus.core.meaning_ingestion import MeaningIngestionPreview
from pigenus.schemas.memory import MemoryObject
from pigenus.schemas.systemform import TruthStatus
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    DecisionRepository,
    MeaningRepository,
    MemoryRepository,
)


def db_path(name: str) -> Path:
    root = Path(".testdata") / "meaning-ingestion-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def run_ingest_memory(path: Path, memory_id: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "meaning-ingest-memory",
            memory_id,
            "--db",
            str(path),
        ],
        capture_output=True,
        text=True,
    )


def memory(memory_id: str = "mem_ingest") -> MemoryObject:
    return MemoryObject(
        memory_id=memory_id,
        memory_type="fact",
        context={"name": "developer/default"},
        status="canonical",
        content={"text": "PiGenus can ingest memory into meaning."},
        human_summary="PiGenus can ingest memory into meaning.",
        confidence=0.95,
    )


def test_meaning_ingestion_preview_persists_adapted_memory_object():
    path = db_path("service")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    meaning_repository = MeaningRepository(database)
    item = memory()
    memory_repository.add(item)

    result = MeaningIngestionPreview(
        memory_repository=memory_repository,
        meaning_repository=meaning_repository,
    ).ingest_memory_by_id("mem_ingest", created_by="cell_preview")

    assert result is not None
    assert result.created is True
    assert result.meaning.id == "bo_from_mem_ingest"
    assert result.meaning.created_by == "cell_preview"
    assert result.meaning.truth_status == TruthStatus.VERIFIED
    assert result.meaning.content == item.content
    assert meaning_repository.count() == 1
    database.close()


def test_meaning_ingestion_preview_is_idempotent_for_same_memory_id():
    path = db_path("idempotent")
    database = Database(path)
    database.initialize()
    memory_repository = MemoryRepository(database)
    meaning_repository = MeaningRepository(database)
    memory_repository.add(memory("mem_repeat"))
    ingestion = MeaningIngestionPreview(
        memory_repository=memory_repository,
        meaning_repository=meaning_repository,
    )

    first = ingestion.ingest_memory_by_id("mem_repeat")
    second = ingestion.ingest_memory_by_id("mem_repeat")

    assert first is not None
    assert second is not None
    assert first.created is True
    assert second.created is False
    assert second.meaning.id == first.meaning.id
    assert meaning_repository.count() == 1
    database.close()


def test_meaning_ingestion_preview_returns_none_for_missing_memory():
    path = db_path("missing")
    database = Database(path)
    database.initialize()

    result = MeaningIngestionPreview(
        memory_repository=MemoryRepository(database),
        meaning_repository=MeaningRepository(database),
    ).ingest_memory_by_id("mem_missing")

    assert result is None
    assert MeaningRepository(database).count() == 0
    database.close()


def test_meaning_ingest_memory_cli_creates_meaning_without_other_side_effects():
    path = db_path("cli")
    database = Database(path)
    database.initialize()
    MemoryRepository(database).add(memory("mem_cli"))
    database.close()

    result = run_ingest_memory(path, "mem_cli")

    database = Database(path)
    database.initialize()
    stored = MeaningRepository(database).get("bo_from_mem_cli")
    assert result.returncode == 0
    assert "Meaning ingestion: created" in result.stdout
    assert "Memory: mem_cli" in result.stdout
    assert "Meaning: bo_from_mem_cli" in result.stdout
    assert stored is not None
    assert AuditRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    database.close()


def test_meaning_ingest_memory_cli_reports_existing_meaning_without_duplicate():
    path = db_path("cli-repeat")
    database = Database(path)
    database.initialize()
    MemoryRepository(database).add(memory("mem_cli_repeat"))
    database.close()

    first = run_ingest_memory(path, "mem_cli_repeat")
    second = run_ingest_memory(path, "mem_cli_repeat")

    database = Database(path)
    database.initialize()
    assert first.returncode == 0
    assert second.returncode == 0
    assert "Meaning ingestion: already_exists" in second.stdout
    assert MeaningRepository(database).count() == 1
    database.close()


def test_meaning_ingest_memory_cli_returns_clean_error_for_missing_memory():
    result = run_ingest_memory(db_path("cli-missing"), "mem_missing")

    assert result.returncode == 1
    assert "Memory object not found: mem_missing" in result.stdout
    assert result.stderr == ""
