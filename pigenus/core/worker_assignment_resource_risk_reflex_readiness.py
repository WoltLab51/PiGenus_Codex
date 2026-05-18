from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from pigenus.schemas.systemform import WorkerAssignment, WorkerAssignmentStatus
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


class RiskBand(str, Enum):
    """Coarse risk bands for read-only worker readiness checks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class WorkerAssignmentResourceRiskReflexReadinessOutcome(str, Enum):
    """Read-only resource/risk/reflex outcome for assigned worker intent."""

    ALLOW = "allow_readiness"
    DENY = "deny_readiness"
    REQUIRE_REVIEW = "require_review"
    NOT_CONSIDERED = "not_considered"


@dataclass(frozen=True)
class WorkerAssignmentResourceRiskReflexPolicy:
    """Caller-supplied readiness policy for the storage-free validator."""

    allowed_risk_bands: tuple[RiskBand, ...] = (RiskBand.LOW, RiskBand.MEDIUM)
    review_risk_bands: tuple[RiskBand, ...] = (RiskBand.HIGH, RiskBand.UNKNOWN)
    denied_risk_bands: tuple[RiskBand, ...] = (RiskBand.CRITICAL,)
    high_risk_bands: tuple[RiskBand, ...] = (
        RiskBand.HIGH,
        RiskBand.CRITICAL,
        RiskBand.UNKNOWN,
    )
    require_risk_budget: bool = True
    require_reflex_boundaries_for_high_risk: bool = True


@dataclass(frozen=True)
class WorkerAssignmentResourceRiskReflexReadinessResult:
    """Result of checking resource, risk, and reflex readiness."""

    assignment_id: str
    outcome: WorkerAssignmentResourceRiskReflexReadinessOutcome
    reasons: tuple[str, ...]
    details: dict[str, Any]

    @property
    def ready(self) -> bool:
        return (
            self.outcome
            == WorkerAssignmentResourceRiskReflexReadinessOutcome.ALLOW
        )


class WorkerAssignmentResourceRiskReflexReadinessValidator:
    """Read-only check before future scheduling enforcement can be considered."""

    def __init__(
        self,
        *,
        assignments: WorkerAssignmentRepository,
        policy: WorkerAssignmentResourceRiskReflexPolicy | None = None,
    ) -> None:
        self.assignments = assignments
        self.policy = policy or WorkerAssignmentResourceRiskReflexPolicy()

    def validate(
        self,
        assignment_id: str,
        *,
        resource_request: Mapping[str, int | float] | None = None,
        resource_budget: Mapping[str, int | float] | None = None,
        risk_band: RiskBand | str | None = None,
        risk_budget_available: bool | None = None,
        kill_switch_available: bool | None = None,
        kill_switch_active: bool = False,
        circuit_breaker_open: bool = False,
        quarantine_active: bool = False,
        abort_path_available: bool | None = None,
        recovery_path_available: bool | None = None,
    ) -> WorkerAssignmentResourceRiskReflexReadinessResult:
        assignment = self.assignments.get(assignment_id)
        if assignment is None:
            return WorkerAssignmentResourceRiskReflexReadinessResult(
                assignment_id=assignment_id,
                outcome=WorkerAssignmentResourceRiskReflexReadinessOutcome.NOT_CONSIDERED,
                reasons=("assignment_unknown",),
                details={"assignment_id": assignment_id},
            )

        details = _assignment_details(assignment)
        details["resource"] = {
            "request": dict(resource_request or {}),
            "budget": dict(resource_budget or {}),
        }
        details["risk"] = {
            "risk_band": _risk_band_value(risk_band),
            "risk_budget_available": risk_budget_available,
        }
        details["reflex"] = {
            "kill_switch_available": kill_switch_available,
            "kill_switch_active": kill_switch_active,
            "circuit_breaker_open": circuit_breaker_open,
            "quarantine_active": quarantine_active,
            "abort_path_available": abort_path_available,
            "recovery_path_available": recovery_path_available,
        }

        if assignment.status != WorkerAssignmentStatus.ASSIGNED:
            return WorkerAssignmentResourceRiskReflexReadinessResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentResourceRiskReflexReadinessOutcome.NOT_CONSIDERED,
                reasons=("assignment_status_not_considered",),
                details=details,
            )

        deny_reasons: list[str] = []
        review_reasons: list[str] = []
        pass_reasons: list[str] = []

        self._check_resource_readiness(
            resource_request=resource_request,
            resource_budget=resource_budget,
            deny_reasons=deny_reasons,
            review_reasons=review_reasons,
            pass_reasons=pass_reasons,
        )
        normalized_risk_band = self._check_risk_readiness(
            risk_band=risk_band,
            risk_budget_available=risk_budget_available,
            deny_reasons=deny_reasons,
            review_reasons=review_reasons,
            pass_reasons=pass_reasons,
        )
        self._check_reflex_readiness(
            risk_band=normalized_risk_band,
            kill_switch_available=kill_switch_available,
            kill_switch_active=kill_switch_active,
            circuit_breaker_open=circuit_breaker_open,
            quarantine_active=quarantine_active,
            abort_path_available=abort_path_available,
            recovery_path_available=recovery_path_available,
            deny_reasons=deny_reasons,
            review_reasons=review_reasons,
            pass_reasons=pass_reasons,
        )

        if deny_reasons:
            return WorkerAssignmentResourceRiskReflexReadinessResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentResourceRiskReflexReadinessOutcome.DENY,
                reasons=tuple(deny_reasons),
                details=details,
            )

        if review_reasons:
            return WorkerAssignmentResourceRiskReflexReadinessResult(
                assignment_id=assignment.id,
                outcome=WorkerAssignmentResourceRiskReflexReadinessOutcome.REQUIRE_REVIEW,
                reasons=tuple(review_reasons),
                details=details,
            )

        return WorkerAssignmentResourceRiskReflexReadinessResult(
            assignment_id=assignment.id,
            outcome=WorkerAssignmentResourceRiskReflexReadinessOutcome.ALLOW,
            reasons=tuple(pass_reasons),
            details=details,
        )

    @staticmethod
    def _check_resource_readiness(
        *,
        resource_request: Mapping[str, int | float] | None,
        resource_budget: Mapping[str, int | float] | None,
        deny_reasons: list[str],
        review_reasons: list[str],
        pass_reasons: list[str],
    ) -> None:
        if not resource_request:
            _append_reason(review_reasons, "resource_request_missing")
        if not resource_budget:
            _append_reason(review_reasons, "resource_budget_missing")
        if not resource_request or not resource_budget:
            return

        for resource_name, requested in resource_request.items():
            if requested < 0:
                _append_reason(deny_reasons, "resource_request_invalid")
                continue

            granted = resource_budget.get(resource_name)
            if granted is None or requested > granted:
                _append_reason(deny_reasons, "resource_request_exceeds_grant")
            elif requested > 0 and granted <= 0:
                _append_reason(deny_reasons, "resource_budget_exhausted")

        if not deny_reasons:
            _append_reason(pass_reasons, "resource_readiness_passed")

    def _check_risk_readiness(
        self,
        *,
        risk_band: RiskBand | str | None,
        risk_budget_available: bool | None,
        deny_reasons: list[str],
        review_reasons: list[str],
        pass_reasons: list[str],
    ) -> RiskBand:
        normalized = _normalize_risk_band(risk_band)
        if normalized is None:
            normalized = RiskBand.UNKNOWN
            _append_reason(review_reasons, "risk_band_unknown")

        if self.policy.require_risk_budget and risk_budget_available is not True:
            _append_reason(review_reasons, "risk_budget_missing")

        if normalized in self.policy.denied_risk_bands:
            _append_reason(deny_reasons, "risk_band_denied")
        elif normalized in self.policy.review_risk_bands:
            _append_reason(review_reasons, "risk_band_requires_review")
        elif normalized not in self.policy.allowed_risk_bands:
            _append_reason(review_reasons, "risk_band_requires_review")

        if not any(
            reason.startswith("risk_")
            for reason in [*deny_reasons, *review_reasons]
        ):
            _append_reason(pass_reasons, "risk_readiness_passed")
        return normalized

    def _check_reflex_readiness(
        self,
        *,
        risk_band: RiskBand,
        kill_switch_available: bool | None,
        kill_switch_active: bool,
        circuit_breaker_open: bool,
        quarantine_active: bool,
        abort_path_available: bool | None,
        recovery_path_available: bool | None,
        deny_reasons: list[str],
        review_reasons: list[str],
        pass_reasons: list[str],
    ) -> None:
        if kill_switch_active:
            _append_reason(deny_reasons, "kill_switch_active")
        if circuit_breaker_open:
            _append_reason(deny_reasons, "circuit_breaker_open")
        if quarantine_active:
            _append_reason(deny_reasons, "quarantine_active")

        if (
            self.policy.require_reflex_boundaries_for_high_risk
            and risk_band in self.policy.high_risk_bands
        ):
            if kill_switch_available is not True:
                _append_reason(review_reasons, "kill_switch_missing")
            if abort_path_available is not True:
                _append_reason(review_reasons, "abort_path_missing")
            if recovery_path_available is not True:
                _append_reason(review_reasons, "recovery_path_missing")

        if not any(
            reason
            in {
                "kill_switch_active",
                "circuit_breaker_open",
                "quarantine_active",
                "kill_switch_missing",
                "abort_path_missing",
                "recovery_path_missing",
                "reflex_boundary_missing",
                "reflex_review_required",
            }
            for reason in [*deny_reasons, *review_reasons]
        ):
            _append_reason(pass_reasons, "reflex_readiness_passed")


def _assignment_details(assignment: WorkerAssignment) -> dict[str, Any]:
    return {
        "assignment_id": assignment.id,
        "assignment_status": assignment.status.value,
        "worker_id": assignment.worker_id,
        "capability": assignment.capability,
        "room_id": assignment.room_id,
        "governance_decision_id": assignment.governance_decision_id,
        "required_runtime": assignment.required_runtime,
        "sensitivity": assignment.sensitivity.value
        if assignment.sensitivity is not None
        else None,
        "network_required": assignment.network_required,
    }


def _normalize_risk_band(value: RiskBand | str | None) -> RiskBand | None:
    if isinstance(value, RiskBand):
        return value
    if value is None:
        return None
    try:
        return RiskBand(value)
    except ValueError:
        return None


def _risk_band_value(value: RiskBand | str | None) -> str | None:
    if isinstance(value, RiskBand):
        return value.value
    return value


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)
