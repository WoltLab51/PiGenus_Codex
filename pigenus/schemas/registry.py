from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from pigenus.schemas.events import EventType, REQUIRED_PAYLOAD_KEYS


@dataclass(frozen=True)
class EventContract:
    """Inspectable contract for a structured event type."""

    object_type: str
    schema_version: str
    required_payload_keys: tuple[str, ...]


class SchemaRegistry:
    """Small read-only registry for runtime schema contracts."""

    schema_version = "1.0"

    def list_event_contracts(self) -> list[EventContract]:
        return [
            self.get_event_contract(object_type)
            for object_type in sorted(str(value) for value in get_args(EventType))
        ]

    def get_event_contract(self, object_type: str) -> EventContract:
        known_types = {str(value) for value in get_args(EventType)}
        if object_type not in known_types:
            raise KeyError(f"Unknown event type: {object_type}")
        return EventContract(
            object_type=object_type,
            schema_version=self.schema_version,
            required_payload_keys=tuple(sorted(REQUIRED_PAYLOAD_KEYS.get(object_type, set()))),
        )
