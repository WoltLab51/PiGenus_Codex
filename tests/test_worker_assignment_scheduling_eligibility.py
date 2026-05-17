from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pigenus.core.worker_assignment_scheduling_eligibility import (
    WorkerAssignmentSchedulingEligibilityLogger,
    WorkerAssignmentSchedulingEligibilityOutcome,
    WorkerAssignmentSchedulingEligibilityValidator,
)
from pigenus.core.worker_execution_preflight import (
    WorkerExecutionPreflightLogger,
    WorkerExecutionPreflightRequest,
    WorkerExecutionPreflightService,
)
from pigenus.core.worker_inspection import WorkerInspectionService
from pigenus.core.worker_registry import WorkerRegistry
from pigenus.schemas.decisions import DecisionRecord
from pigenus.schemas.systemform import (
    Sensitivity,
    WorkerAssignment,
    WorkerAssignmentStatus,
    WorkerHeartbeat,
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
    root = Path(".testdata") / "worker-assignment-scheduling-eligibility-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def worker_profile(
    worker_id: str = "worker_local",
    *,
    status: WorkerStatus = WorkerStatus.ACTIVE,
    cells: list[str] | None = None,
    runtimes: list[str] | None = None,
    max_sensitivity: Sensitivity = Sensitivity.PRIVATE,
    network_access: bool = True,
) -> WorkerProfile:
    return WorkerProfile(
        id=worker_id,
        worker_type=WorkerType.LOCAL_PROCESS,
        display_name=f"{worker_id} display",
        status=status,
        home_room_id="room_developer",
        available_cells=cells or ["meaning_ingester"],
        supported_runtimes=runtimes or ["python"],
        max_sensitivity=max_sensitivity,
        network_access=network_access,
    )


def assignment(
    decision_id: str = "dec_preflight",
    *,
    assignment_id: str = "wasg_sched",
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.ASSIGNED,
    capability: str = "meaning_ingester",
    runtime: str | None = "python",
    sensitivity: Sensitivity | None = Sensitivity.PRIVATE,
    network_required: bool = True,
) -> WorkerAssignment:
    return WorkerAssignment(
        id=assignment_id,
        worker_id="worker_local",
        capability=capability,
        room_id="room_developer",
        governance_decision_id=decision_id,
        created_by_actor_id="agent_scheduler_preview",
        status=status,
        required_runtime=runtime,
        sensitivity=sensitivity,
        network_required=network_required,
        reason="preflight_allowed",
        created_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
    )


def prepare_database() -> Database:
    database = Database(db_path("eligibility"))
    database.initialize()
    workers = WorkerRepository(database)
    workers.add_profile(worker_profile())
    workers.record_heartbeat(
        WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.ACTIVE)
    )
    return database


def log_preflight_decision(database: Database) -> DecisionRecord:
    registry = WorkerRegistry()
    workers = WorkerRepository(database)
    for profile in workers.list_profiles():
        registry.register(profile)
    for heartbeat in workers.list_heartbeats():
        registry.record_heartbeat(heartbeat)
    result = WorkerExecutionPreflightService(WorkerInspectionService(registry)).check(
        WorkerExecutionPreflightRequest(
            worker_id="worker_local",
            capability="meaning_ingester",
            required_runtime="python",
            sensitivity=Sensitivity.PRIVATE,
            network_required=True,
        )
    )
    return WorkerExecutionPreflightLogger(DecisionRepository(database)).add(
        result,
        actor_id="agent_preflight",
        room_id="room_developer",
        event_id="evt_preflight",
    )


def add_assignment(
    database: Database,
    *,
    status: WorkerAssignmentStatus = WorkerAssignmentStatus.ASSIGNED,
    decision_id: str | None = None,
) -> WorkerAssignment:
    if decision_id is None:
        decision_id = log_preflight_decision(database).decision_id
    item = assignment(decision_id, status=status)
    WorkerAssignmentRepository(database).add(item)
    return item


def validator(database: Database) -> WorkerAssignmentSchedulingEligibilityValidator:
    return WorkerAssignmentSchedulingEligibilityValidator(
        assignments=WorkerAssignmentRepository(database),
        workers=WorkerRepository(database),
        decisions=DecisionRepository(database),
    )


def test_worker_assignment_scheduling_eligibility_allows_assigned_current_worker():
    database = prepare_database()
    add_assignment(database)

    result = validator(database).validate("wasg_sched")

    assert result.eligible is True
    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.ALLOW
    assert result.reasons == ("assignment_scheduling_eligible",)
    assert result.details["assignment_status"] == "assigned"
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_skips_unknown_assignment():
    database = prepare_database()

    result = validator(database).validate("wasg_missing")

    assert result.eligible is False
    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.NOT_CONSIDERED
    assert result.reasons == ("assignment_unknown",)
    assert WorkerAssignmentRepository(database).count() == 0
    assert DecisionRepository(database).count() == 0
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_skips_non_assigned_status():
    database = prepare_database()
    add_assignment(database, status=WorkerAssignmentStatus.PENDING)

    result = validator(database).validate("wasg_sched")

    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.NOT_CONSIDERED
    assert result.reasons == ("assignment_status_not_assigned",)
    assert WorkerAssignmentRepository(database).get("wasg_sched").status == (
        WorkerAssignmentStatus.PENDING
    )
    database.close()


def test_worker_assignment_scheduling_eligibility_skips_terminal_status():
    database = prepare_database()
    add_assignment(database, status=WorkerAssignmentStatus.CANCELLED)

    result = validator(database).validate("wasg_sched")

    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.NOT_CONSIDERED
    assert result.reasons == ("assignment_status_terminal",)
    assert WorkerAssignmentRepository(database).get("wasg_sched").status == (
        WorkerAssignmentStatus.CANCELLED
    )
    database.close()


def test_worker_assignment_scheduling_eligibility_denies_stale_worker_conditions():
    database = prepare_database()
    add_assignment(database)
    WorkerRepository(database).add_profile(
        worker_profile(
            cells=["log_reader"],
            runtimes=["node"],
            max_sensitivity=Sensitivity.INTERNAL,
            network_access=False,
        )
    )

    result = validator(database).validate("wasg_sched")

    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.DENY
    assert result.reasons == (
        "worker_capability_missing",
        "runtime_mismatch",
        "sensitivity_exceeded",
        "network_not_allowed",
    )
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_requires_review_for_degraded_worker():
    database = prepare_database()
    add_assignment(database)
    WorkerRepository(database).record_heartbeat(
        WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.DEGRADED)
    )

    result = validator(database).validate("wasg_sched")

    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.REQUIRE_REVIEW
    assert result.reasons == ("worker_degraded",)
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_denies_invalid_evidence():
    database = prepare_database()
    DecisionRepository(database).add(
        DecisionRecord(
            decision_id="dec_preview",
            decision_type="governance_decision",
            context={"name": "developer/default"},
            subject_id="worker_assignment_candidate",
            actor="agent_preview",
            reason="worker_candidates_available",
            source="worker_scheduling_preview",
            details={"decision": "allow", "family": "worker_scheduling"},
        )
    )
    add_assignment(database, decision_id="dec_preview")

    result = validator(database).validate("wasg_sched")

    assert result.outcome == WorkerAssignmentSchedulingEligibilityOutcome.DENY
    assert result.reasons == ("governance_evidence_not_preflight_allow",)
    assert WorkerAssignmentRepository(database).count() == 1
    assert DecisionRepository(database).count() == 1
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_logger_persists_allow_decision():
    database = prepare_database()
    add_assignment(database)
    result = validator(database).validate("wasg_sched")
    repository = DecisionRepository(database)

    record = WorkerAssignmentSchedulingEligibilityLogger(repository).add(
        result,
        actor_id="operator_cli",
        event_id="evt_eligibility",
    )

    assert record is not None
    assert record.subject_id == "wasg_sched"
    assert record.actor == "operator_cli"
    assert record.source == "worker_assignment_scheduling_eligibility"
    assert record.reason == "assignment_scheduling_eligible"
    assert record.details["decision"] == "allow"
    assert record.details["family"] == "worker_assignment_scheduling_eligibility"
    assert record.details["room_id"] == "room_developer"
    assert record.details["trace"][0]["decision"] == "allow"
    decision_details = record.details["governance_decision"]["details"]
    assert decision_details["assignment_id"] == "wasg_sched"
    assert decision_details["outcome"] == "allow_scheduling"
    assert decision_details["eligible"] is True
    assert WorkerAssignmentRepository(database).count() == 1
    assert repository.count() == 2
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_logger_persists_deny_decision():
    database = prepare_database()
    add_assignment(database)
    WorkerRepository(database).add_profile(
        worker_profile(
            cells=["log_reader"],
            runtimes=["node"],
            max_sensitivity=Sensitivity.INTERNAL,
            network_access=False,
        )
    )
    result = validator(database).validate("wasg_sched")
    repository = DecisionRepository(database)

    record = WorkerAssignmentSchedulingEligibilityLogger(repository).add(
        result,
        actor_id="operator_cli",
    )

    assert record is not None
    assert record.subject_id == "wasg_sched"
    assert record.source == "worker_assignment_scheduling_eligibility"
    assert record.reason == "worker_capability_missing"
    assert record.details["decision"] == "block"
    assert record.details["family"] == "worker_assignment_scheduling_eligibility"
    assert record.details["trace"][0]["decision"] == "block"
    decision_details = record.details["governance_decision"]["details"]
    assert decision_details["outcome"] == "deny_scheduling"
    assert decision_details["eligible"] is False
    assert decision_details["reasons"] == [
        "worker_capability_missing",
        "runtime_mismatch",
        "sensitivity_exceeded",
        "network_not_allowed",
    ]
    assert WorkerAssignmentRepository(database).count() == 1
    assert repository.count() == 2
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_logger_persists_review_decision():
    database = prepare_database()
    add_assignment(database)
    WorkerRepository(database).record_heartbeat(
        WorkerHeartbeat(worker_id="worker_local", status=WorkerStatus.DEGRADED)
    )
    result = validator(database).validate("wasg_sched")
    repository = DecisionRepository(database)

    record = WorkerAssignmentSchedulingEligibilityLogger(repository).add(
        result,
        actor_id="operator_cli",
    )

    assert record is not None
    assert record.subject_id == "wasg_sched"
    assert record.source == "worker_assignment_scheduling_eligibility"
    assert record.reason == "worker_degraded"
    assert record.details["decision"] == "escalate"
    assert record.details["requires_human"] is True
    assert record.details["trace"][0]["decision"] == "escalate"
    decision_details = record.details["governance_decision"]["details"]
    assert decision_details["outcome"] == "require_review"
    assert decision_details["reasons"] == ["worker_degraded"]
    assert WorkerAssignmentRepository(database).count() == 1
    assert repository.count() == 2
    assert AuditRepository(database).count() == 0
    database.close()


def test_worker_assignment_scheduling_eligibility_logger_skips_not_considered():
    database = prepare_database()
    add_assignment(database, status=WorkerAssignmentStatus.PENDING)
    result = validator(database).validate("wasg_sched")
    repository = DecisionRepository(database)

    record = WorkerAssignmentSchedulingEligibilityLogger(repository).add(
        result,
        actor_id="operator_cli",
    )

    assert record is None
    assert WorkerAssignmentRepository(database).count() == 1
    assert repository.count() == 1
    assert AuditRepository(database).count() == 0
    database.close()
