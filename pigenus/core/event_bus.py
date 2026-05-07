from __future__ import annotations

from pigenus.schemas.events import Event
from pigenus.storage.repositories import EventRepository


class EventBus:
    """Stores structured meaning events for the local runtime."""

    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def publish(self, event: Event | dict) -> Event:
        validated = Event.model_validate(event)
        self.repository.add(validated)
        return validated

    def count(self) -> int:
        return self.repository.count()

    def list_events(self) -> list[Event]:
        return self.repository.list()
