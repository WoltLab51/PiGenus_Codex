from __future__ import annotations

from typing import Any

from pigenus.core.guard_pipeline import GuardPipeline, GuardPipelineResult
from pigenus.schemas.cells import CellSpec
from pigenus.schemas.context import Context
from pigenus.schemas.memory import MemoryObject
from pigenus.schemas.systemform import MeaningObject, ResourceGrant, Room
from pigenus.schemas.systemform_adapters import (
    cell_spec_to_actor_identity,
    cell_spec_to_contract,
    context_to_room,
    memory_to_meaning_object,
)


class GuardPipelineRuntimePreview:
    """Runs the Systemform guard pipeline against current runtime objects in shadow mode."""

    def __init__(self, pipeline: GuardPipeline | None = None) -> None:
        self.pipeline = pipeline or GuardPipeline()

    def preview_cell_action(
        self,
        *,
        cell: CellSpec,
        context: Context | dict[str, Any] | Room,
        action: str,
        capability: str | None = None,
        target_context: Context | dict[str, Any] | Room | None = None,
        memory: MemoryObject | None = None,
        meaning: MeaningObject | None = None,
        resource_request: dict[str, int | float] | None = None,
        resource_grant: ResourceGrant | None = None,
    ) -> GuardPipelineResult:
        source_room = _to_room(context)
        target_room = _to_room(target_context) if target_context is not None else None
        preview_meaning = meaning
        if preview_meaning is None and memory is not None:
            preview_meaning = memory_to_meaning_object(memory, created_by=cell.cell_id)

        return self.pipeline.evaluate(
            actor=cell_spec_to_actor_identity(cell),
            room=source_room,
            contract=cell_spec_to_contract(cell),
            action=action,
            capability=capability,
            resource_request=resource_request,
            resource_grant=resource_grant,
            source_room=source_room if target_room is not None else None,
            target_room=target_room,
            meaning=preview_meaning,
        )


def _to_room(value: Context | dict[str, Any] | Room) -> Room:
    if isinstance(value, Room):
        return value
    return context_to_room(value)
