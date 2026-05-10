from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pigenus.core.human_approval import (
    ApprovalStatus,
    HumanApprovalLog,
    HumanApprovalRecord,
    human_approval_to_decision_record,
)
from pigenus.core.orchestrator import SimpleOrchestrator
from pigenus.storage.database import Database
from pigenus.storage.repositories import DecisionRepository


def db_path(name: str) -> Path:
    root = Path(".testdata") / "human-approval-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_human_approval_pending_record_serializes_to_decision_record():
    approval = HumanApprovalRecord(
        governance_decision_id="gdec_example",
        requested_by="cell_memory_writer_0_1_0",
        context={"name": "developer/default"},
        reason="human_approval_required",
    )

    decision = human_approval_to_decision_record(approval)

    assert decision.decision_type == "human_approval"
    assert decision.subject_id == "gdec_example"
    assert decision.actor == "cell_memory_writer_0_1_0"
    assert decision.details["status"] == "pending"
    assert decision.details["approval"]["approval_id"] == approval.approval_id


def test_human_approval_log_persists_pending_approval():
    path = db_path("pending")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)

    approval = HumanApprovalLog(repository).create_pending(
        governance_decision_id="gdec_example",
        requested_by="cell_memory_writer_0_1_0",
        context={"name": "developer/default"},
        reason="human_approval_required",
    )

    stored = repository.list()[0]
    assert approval.status == ApprovalStatus.PENDING
    assert repository.count() == 1
    assert stored.details["approval_id"] == approval.approval_id
    assert stored.details["status"] == "pending"
    database.close()


def test_human_approval_log_persists_approval_resolution():
    path = db_path("approved")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    log = HumanApprovalLog(repository)
    pending = log.create_pending(
        governance_decision_id="gdec_example",
        requested_by="cell_memory_writer_0_1_0",
        context={"name": "developer/default"},
        reason="human_approval_required",
    )

    approved = log.approve(pending, resolved_by="human_ronny", reason="looks_ok")

    records = repository.list()
    assert approved.status == ApprovalStatus.APPROVED
    assert approved.resolved_by == "human_ronny"
    assert approved.resolution_reason == "looks_ok"
    assert len(records) == 2
    assert records[1].actor == "human_ronny"
    assert records[1].details["status"] == "approved"
    database.close()


def test_human_approval_log_persists_rejection_resolution():
    path = db_path("rejected")
    database = Database(path)
    database.initialize()
    repository = DecisionRepository(database)
    log = HumanApprovalLog(repository)
    pending = log.create_pending(
        governance_decision_id="gdec_example",
        requested_by="cell_memory_writer_0_1_0",
        context={"name": "developer/default"},
        reason="human_approval_required",
    )

    rejected = log.reject(pending, resolved_by="human_ronny", reason="too_risky")

    records = repository.list()
    assert rejected.status == ApprovalStatus.REJECTED
    assert rejected.resolution_reason == "too_risky"
    assert len(records) == 2
    assert records[1].details["status"] == "rejected"
    database.close()


def test_human_approval_stub_does_not_change_current_orchestrator_flow():
    path = db_path("orchestrator")
    orchestrator = SimpleOrchestrator(path)
    result = orchestrator.run_demo()
    orchestrator.close()

    assert result.final_response == "Gespeichert: PiGenus ist der Zellkern."
    assert result.events_stored == 5
