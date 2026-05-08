from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from pigenus.core.event_bus import EventBus
from pigenus.schemas.events import Event
from pigenus.storage.database import Database
from pigenus.storage.repositories import EventRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_event_bus_can_publish_and_store_events():
    database = Database(db_path("events"))
    database.initialize()
    bus = EventBus(EventRepository(database))

    event = Event(
        object_type="TaskRequest",
        context={"name": "developer/default"},
        created_by_cell="input_cell@0.1.0",
        payload={"raw_text": "Merke dir: PiGenus ist der Zellkern.", "action": "memory_write"},
    )

    stored = bus.publish(event)

    assert stored.event_id == event.event_id
    assert bus.count() == 1
    assert bus.list_events()[0].payload["action"] == "memory_write"
    database.close()


def test_event_contract_rejects_unknown_event_types():
    with pytest.raises(ValidationError):
        Event(
            object_type="UnknownEvent",
            context={"name": "developer/default"},
            created_by_cell="test_cell@0.1.0",
            payload={},
        )


def test_event_contract_requires_payload_keys_for_known_events():
    with pytest.raises(ValidationError):
        Event(
            object_type="MemoryProposal",
            context={"name": "developer/default"},
            created_by_cell="memory_proposer@0.1.0",
            payload={"human_summary": "PiGenus ist der Zellkern."},
        )
