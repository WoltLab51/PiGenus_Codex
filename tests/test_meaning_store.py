from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.schemas.systemform import MeaningObject, Sensitivity, TruthStatus
from pigenus.storage.database import Database
from pigenus.storage.repositories import MeaningRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "meaning-store-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def meaning(
    meaning_id: str,
    *,
    type: str = "fact",
    room_id: str = "room_developer",
    truth_status: TruthStatus = TruthStatus.VERIFIED,
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
) -> MeaningObject:
    return MeaningObject(
        id=meaning_id,
        type=type,
        content={
            "claim": f"{meaning_id} is persisted.",
            "tags": ["meaning", "store"],
        },
        source="test-suite",
        provenance=[{"source": "test_meaning_store", "confidence": 0.9}],
        room_id=room_id,
        truth_status=truth_status,
        confidence=0.9,
        sensitivity=sensitivity,
        parent_ids=["bo_parent"],
        valid_from=datetime(2026, 5, 10, tzinfo=timezone.utc),
        created_by="cell_meaning_test",
        created_at=datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc),
    )


def test_meaning_repository_adds_and_gets_systemform_meaning_object():
    database = Database(db_path("roundtrip"))
    database.initialize()
    repository = MeaningRepository(database)
    original = meaning("bo_roundtrip")

    repository.add(original)
    stored = repository.get("bo_roundtrip")

    assert stored == original
    assert stored is not None
    assert stored.content["tags"] == ["meaning", "store"]
    assert stored.truth_status == TruthStatus.VERIFIED
    assert repository.count() == 1
    database.close()


def test_meaning_repository_lists_in_created_order():
    database = Database(db_path("list"))
    database.initialize()
    repository = MeaningRepository(database)

    repository.add(meaning("bo_second", room_id="room_family"))
    first = meaning("bo_first")
    first_data = first.model_dump(mode="json")
    first_data["created_at"] = "2026-05-10T11:00:00Z"
    repository.add(MeaningObject.model_validate(first_data))

    assert [item.id for item in repository.list()] == ["bo_first", "bo_second"]
    database.close()


def test_meaning_repository_filters_by_room_type_truth_status_and_sensitivity():
    database = Database(db_path("filters"))
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

    assert [item.id for item in repository.list(room_id="room_family")] == ["bo_family_note"]
    assert [item.id for item in repository.list(type="fact")] == ["bo_dev_fact", "bo_private_fact"]
    assert [item.id for item in repository.list(truth_status=TruthStatus.CONTESTED)] == [
        "bo_private_fact"
    ]
    assert [item.id for item in repository.list(sensitivity=Sensitivity.FAMILY)] == [
        "bo_family_note"
    ]
    assert [
        item.id
        for item in repository.list(
            room_id="room_family",
            type="note",
            truth_status="believed",
            sensitivity="family",
        )
    ] == ["bo_family_note"]
    database.close()


def test_meaning_repository_returns_none_for_unknown_id():
    database = Database(db_path("missing"))
    database.initialize()

    assert MeaningRepository(database).get("bo_missing") is None
    database.close()
