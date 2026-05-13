from __future__ import annotations

from dataclasses import dataclass

from pigenus.core.worker_inspection import WorkerInspection, WorkerInspectionService
from pigenus.schemas.systemform import Sensitivity


SENSITIVITY_RANK: dict[Sensitivity, int] = {
    Sensitivity.PUBLIC: 0,
    Sensitivity.INTERNAL: 1,
    Sensitivity.PRIVATE: 2,
    Sensitivity.FAMILY: 3,
    Sensitivity.FINANCIAL: 4,
    Sensitivity.CHILD_RELATED: 5,
    Sensitivity.SECRET: 6,
}


@dataclass(frozen=True)
class WorkerSchedulingRequest:
    """Storage-free request for previewing worker suitability."""

    capability: str
    required_runtime: str | None = None
    sensitivity: Sensitivity | None = None
    network_required: bool = False


@dataclass(frozen=True)
class WorkerSchedulingCandidate:
    """One worker suitability result with ordered reasons."""

    worker_id: str
    suitable: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class WorkerSchedulingPreview:
    """Storage-free preview result. It does not schedule or execute work."""

    request: WorkerSchedulingRequest
    candidates: tuple[WorkerSchedulingCandidate, ...]

    @property
    def suitable_workers(self) -> tuple[str, ...]:
        return tuple(candidate.worker_id for candidate in self.candidates if candidate.suitable)


class WorkerSchedulingPreviewService:
    """Explains which known workers could host a requested capability."""

    def __init__(self, inspection: WorkerInspectionService) -> None:
        self.inspection = inspection

    def preview(self, request: WorkerSchedulingRequest) -> WorkerSchedulingPreview:
        candidates = tuple(
            self._candidate(row, request)
            for row in self.inspection.list_workers()
        )
        return WorkerSchedulingPreview(
            request=request,
            candidates=tuple(
                sorted(
                    candidates,
                    key=lambda candidate: (not candidate.suitable, candidate.worker_id),
                )
            ),
        )

    def _candidate(
        self,
        row: WorkerInspection,
        request: WorkerSchedulingRequest,
    ) -> WorkerSchedulingCandidate:
        reasons: list[str] = []

        if not row.considerable:
            reasons.append("worker_not_considerable")
        if request.capability not in row.available_cells:
            reasons.append("capability_missing")
        if (
            request.required_runtime is not None
            and request.required_runtime not in row.supported_runtimes
        ):
            reasons.append("runtime_missing")
        if (
            request.sensitivity is not None
            and SENSITIVITY_RANK[request.sensitivity] > SENSITIVITY_RANK[row.max_sensitivity]
        ):
            reasons.append("sensitivity_exceeds_worker_limit")
        if request.network_required and not row.network_access:
            reasons.append("network_unavailable")

        suitable = not reasons
        if suitable:
            reasons.append("preview_suitable")

        return WorkerSchedulingCandidate(
            worker_id=row.worker_id,
            suitable=suitable,
            reasons=tuple(reasons),
        )
