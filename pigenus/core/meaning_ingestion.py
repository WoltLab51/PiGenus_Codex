from __future__ import annotations

from dataclasses import dataclass

from pigenus.schemas.memory import MemoryObject
from pigenus.schemas.systemform import MeaningObject
from pigenus.schemas.systemform_adapters import memory_to_meaning_object
from pigenus.storage.repositories import MeaningRepository, MemoryRepository


@dataclass(frozen=True)
class MeaningIngestionResult:
    """Result of a preview ingestion into the Meaning Store."""

    meaning: MeaningObject
    created: bool
    source_memory_id: str


class MeaningIngestionPreview:
    """Narrow bridge from current runtime memory into the Systemform Meaning Store."""

    def __init__(
        self,
        *,
        memory_repository: MemoryRepository,
        meaning_repository: MeaningRepository,
    ) -> None:
        self.memory_repository = memory_repository
        self.meaning_repository = meaning_repository

    def ingest_memory(
        self,
        memory: MemoryObject,
        *,
        created_by: str = "meaning_ingestion_preview",
    ) -> MeaningIngestionResult:
        meaning = memory_to_meaning_object(memory, created_by=created_by)
        existing = self.meaning_repository.get(meaning.id)
        if existing is not None:
            return MeaningIngestionResult(
                meaning=existing,
                created=False,
                source_memory_id=memory.memory_id,
            )

        self.meaning_repository.add(meaning)
        return MeaningIngestionResult(
            meaning=meaning,
            created=True,
            source_memory_id=memory.memory_id,
        )

    def ingest_memory_by_id(
        self,
        memory_id: str,
        *,
        created_by: str = "meaning_ingestion_preview",
    ) -> MeaningIngestionResult | None:
        memory = self.memory_repository.get(memory_id)
        if memory is None:
            return None
        return self.ingest_memory(memory, created_by=created_by)
