from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pigenus.core.governance_decision_log import GovernanceDecisionLogger
from pigenus.core.worker_inspection import WorkerInspection, WorkerInspectionService
from pigenus.schemas.context import Context
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import GovernanceDecision, GuardDecisionType, Sensitivity
from pigenus.storage.repositories import DecisionRepository


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

    def to_governance_decision(
        self,
        *,
        actor_id: str,
        room_id: str,
        event_id: str | None = None,
        rule_id: str = "worker_scheduling_preview",
    ) -> GovernanceDecision:
        suitable_workers = self.suitable_workers
        decision = GuardDecisionType.ALLOW if suitable_workers else GuardDecisionType.BLOCK
        reason = "worker_candidates_available" if suitable_workers else "no_suitable_worker"
        return GovernanceDecision(
            decision=decision,
            reason=reason,
            actor_id=actor_id,
            room_id=room_id,
            event_id=event_id,
            rule_id=rule_id,
            details={
                "family": "worker_scheduling",
                "recommended_worker_id": suitable_workers[0] if suitable_workers else None,
                "request": _request_details(self.request),
                "candidates": [
                    {
                        "worker_id": candidate.worker_id,
                        "suitable": candidate.suitable,
                        "reasons": list(candidate.reasons),
                    }
                    for candidate in self.candidates
                ],
                "trace": [
                    {
                        "name": "worker_candidate",
                        "family": "worker_scheduling",
                        "decision": "allow" if candidate.suitable else "block",
                        "reason": candidate.reasons[0],
                        "details": {
                            "worker_id": candidate.worker_id,
                            "reasons": ",".join(candidate.reasons),
                        },
                    }
                    for candidate in self.candidates
                ],
            },
        )


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


class WorkerSchedulingPreviewLogger:
    """Opt-in persistence for worker scheduling previews via the decision log."""

    def __init__(self, repository: DecisionRepository) -> None:
        self.governance_logger = GovernanceDecisionLogger(repository)

    def add(
        self,
        preview: WorkerSchedulingPreview,
        *,
        actor_id: str,
        room_id: str,
        event_id: str | None = None,
        rule_id: str = "worker_scheduling_preview",
        context: Context | dict[str, Any] | None = None,
    ) -> DecisionRecord:
        decision = preview.to_governance_decision(
            actor_id=actor_id,
            room_id=room_id,
            event_id=event_id,
            rule_id=rule_id,
        )
        return self.governance_logger.add(
            decision,
            context=context,
            source="worker_scheduling_preview",
        )


def _request_details(request: WorkerSchedulingRequest) -> dict[str, str | bool | None]:
    return {
        "capability": request.capability,
        "required_runtime": request.required_runtime,
        "sensitivity": request.sensitivity.value if request.sensitivity is not None else None,
        "network_required": request.network_required,
    }
