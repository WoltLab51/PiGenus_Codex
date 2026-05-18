from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.core.worker_assignment_resource_risk_reflex_readiness import (
    RiskBand,
    WorkerAssignmentResourceRiskReflexReadinessOutcome,
    WorkerAssignmentResourceRiskReflexReadinessValidator,
)
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerProfile,
    WorkerStatus,
    WorkerType,
)
from pigenus.storage.database import Database
from pigenus.storage.repositories import (
    AuditRepository,
    DecisionRepository,
    WorkerRepository,
)
from pigenus.storage.worker_repositories import WorkerAssignmentRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "worker-assignment-resource-risk-reflex-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(worker_id: str = "worker_local") -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=WorkerStatus.ACTIVE,
        home_room_id="room_developer",
        available_cells=["meaning_ingester"],
        supported_runtimes=["python"],
        max_sensitivity=Sensitivity.PRIVATE,
        network_access=True,
    )


def preflight_decision(decision_id: str = "dec_preflight") -> DecisionRecord:
    return DecisionRecord(
        decision_id=decision_id,
        decision_type="governance_decision",
        context={"name": "developer/default"},
        subject_id="evt_preflight",
        actor="agent_preflight",
        reason="worker_execution_preflight_passed",
        source="worker_execution_preflight",
        created_at=datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc),
        details={
            "decision": "allow",
            "family": "worker_execution_preflight",
            "room_id": "room_developer",
        },
    )


def assignment(
    *,
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.ASSIGNED,
    decision_id: str = "dec_preflight",
) -> WorkerAssignment:
    return WorkerAssignment(
        id="wasg_resource_risk_reflex",
        worker_id="worker_local",
        capability="meaning_ingester",
        room_id="room_developer",
        governance_decision_id=decision_id,
        created_by_actor_id="agent_scheduler_preview",
        status=status,
        required_runtime="python",
        sensitivity=Sensitivity.PRIVATE,
        network_required=True,
        reason="preflight_allowed",
        created_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
    )


def prepare_database(
    *,
    item: WorkerAssignment | None = None,
) -> Database:
    database = Database(db_path("readiness"))
    database.initialize()
    WorkerRepository(database).add_profile(worker_profile())
    DecisionRepository(database).add(preflight_decision())
    WorkerAssignmentRepository(database).add(item or assignment())
    return database


def validator(
    database: Database,
) -> WorkerAssignmentResourceRiskReflexReadinessValidator:
    return WorkerAssignmentResourceRiskReflexReadinessValidator(
        assignments=WorkerAssignmentRepository(database)
    )


def passing_inputs() -> dict[str, object]:
    return {
        "resource_request": {"compute": 1, "memory": 128},
        "resource_budget": {"compute": 2, "memory": 256},
        "risk_band": RiskBand.LOW,
        "risk_budget_available": True,
    }


def assert_no_writes(database: Database) -> None:
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0


def test_resource_risk_reflex_readiness_allows_matching_inputs():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        **passing_inputs(),
    )

    assert result.ready is True
    assert result.outcome == WorkerAssignmentResourceRiskReflexReadinessOutcome.ALLOW
    assert result.reasons == (
        "resource_readiness_passed",
        "risk_readiness_passed",
        "reflex_readiness_passed",
    )
    assert result.details["assignment_status"] == "assigned"
    assert result.details["resource"]["request"]["compute"] == 1
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_skips_unknown_assignment():
    database = Database(db_path("missing-assignment"))
    database.initialize()

    result = validator(database).validate("wasg_missing")

    assert result.ready is False
    assert result.outcome == (
        WorkerAssignmentResourceRiskReflexReadinessOutcome.NOT_CONSIDERED
    )
    assert result.reasons == ("assignment_unknown",)
    assert WorkerAssignmentRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_resource_risk_reflex_readiness_skips_non_assigned_status():
    database = prepare_database(
        item=assignment(status=WorkerAssignmentStatus.PENDING)
    )

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        **passing_inputs(),
    )

    assert result.outcome == (
        WorkerAssignmentResourceRiskReflexReadinessOutcome.NOT_CONSIDERED
    )
    assert result.reasons == ("assignment_status_not_considered",)
    assert WorkerAssignmentRepository(database).get(
        "wasg_resource_risk_reflex"
    ).status == WorkerAssignmentStatus.PENDING
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_reviews_missing_resource_inputs():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        risk_band=RiskBand.LOW,
        risk_budget_available=True,
    )

    assert result.outcome == (
        WorkerAssignmentResourceRiskReflexReadinessOutcome.REQUIRE_REVIEW
    )
    assert result.reasons == (
        "resource_request_missing",
        "resource_budget_missing",
    )
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_denies_request_above_budget():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        resource_request={"compute": 3},
        resource_budget={"compute": 2},
        risk_band=RiskBand.LOW,
        risk_budget_available=True,
    )

    assert result.outcome == WorkerAssignmentResourceRiskReflexReadinessOutcome.DENY
    assert result.reasons == ("resource_request_exceeds_grant",)
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_reviews_unknown_risk_band():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        resource_request={"compute": 1},
        resource_budget={"compute": 2},
        risk_budget_available=True,
        kill_switch_available=True,
        abort_path_available=True,
        recovery_path_available=True,
    )

    assert result.outcome == (
        WorkerAssignmentResourceRiskReflexReadinessOutcome.REQUIRE_REVIEW
    )
    assert result.reasons == (
        "risk_band_unknown",
        "risk_band_requires_review",
    )
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_denies_critical_risk_band():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        resource_request={"compute": 1},
        resource_budget={"compute": 2},
        risk_band=RiskBand.CRITICAL,
        risk_budget_available=True,
        kill_switch_available=True,
        abort_path_available=True,
        recovery_path_available=True,
    )

    assert result.outcome == WorkerAssignmentResourceRiskReflexReadinessOutcome.DENY
    assert result.reasons == ("risk_band_denied",)
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_denies_active_kill_switch():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        **passing_inputs(),
        kill_switch_active=True,
    )

    assert result.outcome == WorkerAssignmentResourceRiskReflexReadinessOutcome.DENY
    assert result.reasons == ("kill_switch_active",)
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_denies_open_circuit_breaker():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        **passing_inputs(),
        circuit_breaker_open=True,
    )

    assert result.outcome == WorkerAssignmentResourceRiskReflexReadinessOutcome.DENY
    assert result.reasons == ("circuit_breaker_open",)
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_denies_active_quarantine():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        **passing_inputs(),
        quarantine_active=True,
    )

    assert result.outcome == WorkerAssignmentResourceRiskReflexReadinessOutcome.DENY
    assert result.reasons == ("quarantine_active",)
    assert_no_writes(database)
    database.close()


def test_resource_risk_reflex_readiness_reviews_high_risk_missing_reflex_paths():
    database = prepare_database()

    result = validator(database).validate(
        "wasg_resource_risk_reflex",
        resource_request={"compute": 1},
        resource_budget={"compute": 2},
        risk_band=RiskBand.HIGH,
        risk_budget_available=True,
    )

    assert result.outcome == (
        WorkerAssignmentResourceRiskReflexReadinessOutcome.REQUIRE_REVIEW
    )
    assert result.reasons == (
        "risk_band_requires_review",
        "kill_switch_missing",
        "abort_path_missing",
        "recovery_path_missing",
    )
    assert_no_writes(database)
    database.close()
