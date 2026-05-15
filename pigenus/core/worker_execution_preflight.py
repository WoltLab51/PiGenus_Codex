from __future__ import annotations

from dataclasses import dataclass

from pigenus.core.worker_inspection import WorkerInspection, WorkerInspectionService
from pigenus.core.worker_scheduling_preview import SENSITIVITY_RANK
from pigenus.schemas.systemform import GovernanceDecision, GuardDecisionType, Sensitivity


@dataclass(frozen=True)
class WorkerExecutionPreflightRequest:
    """Storage-free request for checking whether one worker may execute work."""

    worker_id: str
    capability: str
    required_runtime: str | None = None
    sensitivity: Sensitivity | None = None
    network_required: bool = False


@dataclass(frozen=True)
class WorkerExecutionPreflightCheck:
    """One ordered preflight check result."""

    name: str
    decision: GuardDecisionType
    reason: str
    details: dict[str, str | bool | None]


@dataclass(frozen=True)
class WorkerExecutionPreflightResult:
    """Storage-free worker execution preflight result. It does not execute work."""

    request: WorkerExecutionPreflightRequest
    checks: tuple[WorkerExecutionPreflightCheck, ...]

    @property
    def allowed(self) -> bool:
        return all(check.decision == GuardDecisionType.ALLOW for check in self.checks)

    @property
    def reason(self) -> str:
        for check in self.checks:
            if check.decision != GuardDecisionType.ALLOW:
                return check.reason
        return "worker_execution_preflight_passed"

    def to_governance_decision(
        self,
        *,
        actor_id: str,
        room_id: str,
        event_id: str | None = None,
        rule_id: str = "worker_execution_preflight",
    ) -> GovernanceDecision:
        return GovernanceDecision(
            decision=GuardDecisionType.ALLOW if self.allowed else GuardDecisionType.BLOCK,
            reason=self.reason,
            actor_id=actor_id,
            room_id=room_id,
            event_id=event_id,
            rule_id=rule_id,
            details={
                "family": "worker_execution_preflight",
                "worker_id": self.request.worker_id,
                "request": _request_details(self.request),
                "trace": [
                    {
                        "name": check.name,
                        "family": "worker_execution_preflight",
                        "decision": check.decision.value,
                        "reason": check.reason,
                        "details": check.details,
                    }
                    for check in self.checks
                ],
            },
        )


class WorkerExecutionPreflightService:
    """Checks one worker before any assignment, routing, or execution exists."""

    def __init__(self, inspection: WorkerInspectionService) -> None:
        self.inspection = inspection

    def check(self, request: WorkerExecutionPreflightRequest) -> WorkerExecutionPreflightResult:
        worker = self.inspection.show_worker(request.worker_id)
        if worker is None:
            return WorkerExecutionPreflightResult(
                request=request,
                checks=(
                    _check(
                        "worker_known",
                        GuardDecisionType.BLOCK,
                        "worker_unknown",
                        worker_id=request.worker_id,
                    ),
                ),
            )

        return WorkerExecutionPreflightResult(
            request=request,
            checks=(
                self._worker_considerable(worker),
                self._capability_available(worker, request),
                self._runtime_supported(worker, request),
                self._sensitivity_allowed(worker, request),
                self._network_allowed(worker, request),
            ),
        )

    def _worker_considerable(self, worker: WorkerInspection) -> WorkerExecutionPreflightCheck:
        if worker.considerable:
            return _check(
                "worker_considerable",
                GuardDecisionType.ALLOW,
                "worker_considerable",
                worker_id=worker.worker_id,
            )
        return _check(
            "worker_considerable",
            GuardDecisionType.BLOCK,
            "worker_not_considerable",
            worker_id=worker.worker_id,
        )

    def _capability_available(
        self,
        worker: WorkerInspection,
        request: WorkerExecutionPreflightRequest,
    ) -> WorkerExecutionPreflightCheck:
        if request.capability in worker.available_cells:
            return _check(
                "capability_available",
                GuardDecisionType.ALLOW,
                "capability_available",
                worker_id=worker.worker_id,
                capability=request.capability,
            )
        return _check(
            "capability_available",
            GuardDecisionType.BLOCK,
            "capability_missing",
            worker_id=worker.worker_id,
            capability=request.capability,
        )

    def _runtime_supported(
        self,
        worker: WorkerInspection,
        request: WorkerExecutionPreflightRequest,
    ) -> WorkerExecutionPreflightCheck:
        if request.required_runtime is None:
            return _check(
                "runtime_supported",
                GuardDecisionType.ALLOW,
                "runtime_not_required",
                worker_id=worker.worker_id,
            )
        if request.required_runtime in worker.supported_runtimes:
            return _check(
                "runtime_supported",
                GuardDecisionType.ALLOW,
                "runtime_supported",
                worker_id=worker.worker_id,
                required_runtime=request.required_runtime,
            )
        return _check(
            "runtime_supported",
            GuardDecisionType.BLOCK,
            "runtime_missing",
            worker_id=worker.worker_id,
            required_runtime=request.required_runtime,
        )

    def _sensitivity_allowed(
        self,
        worker: WorkerInspection,
        request: WorkerExecutionPreflightRequest,
    ) -> WorkerExecutionPreflightCheck:
        if request.sensitivity is None:
            return _check(
                "sensitivity_allowed",
                GuardDecisionType.ALLOW,
                "sensitivity_not_required",
                worker_id=worker.worker_id,
            )
        if SENSITIVITY_RANK[request.sensitivity] <= SENSITIVITY_RANK[worker.max_sensitivity]:
            return _check(
                "sensitivity_allowed",
                GuardDecisionType.ALLOW,
                "sensitivity_allowed",
                worker_id=worker.worker_id,
                sensitivity=request.sensitivity.value,
                max_sensitivity=worker.max_sensitivity.value,
            )
        return _check(
            "sensitivity_allowed",
            GuardDecisionType.BLOCK,
            "sensitivity_exceeds_worker_limit",
            worker_id=worker.worker_id,
            sensitivity=request.sensitivity.value,
            max_sensitivity=worker.max_sensitivity.value,
        )

    def _network_allowed(
        self,
        worker: WorkerInspection,
        request: WorkerExecutionPreflightRequest,
    ) -> WorkerExecutionPreflightCheck:
        if not request.network_required:
            return _check(
                "network_allowed",
                GuardDecisionType.ALLOW,
                "network_not_required",
                worker_id=worker.worker_id,
            )
        if worker.network_access:
            return _check(
                "network_allowed",
                GuardDecisionType.ALLOW,
                "network_available",
                worker_id=worker.worker_id,
            )
        return _check(
            "network_allowed",
            GuardDecisionType.BLOCK,
            "network_unavailable",
            worker_id=worker.worker_id,
        )


def _check(
    name: str,
    decision: GuardDecisionType,
    reason: str,
    **details: str | bool | None,
) -> WorkerExecutionPreflightCheck:
    return WorkerExecutionPreflightCheck(
        name=name,
        decision=decision,
        reason=reason,
        details=details,
    )


def _request_details(
    request: WorkerExecutionPreflightRequest,
) -> dict[str, str | bool | None]:
    return {
        "worker_id": request.worker_id,
        "capability": request.capability,
        "required_runtime": request.required_runtime,
        "sensitivity": request.sensitivity.value if request.sensitivity is not None else None,
        "network_required": request.network_required,
    }
