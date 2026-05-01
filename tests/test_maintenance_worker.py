from __future__ import annotations

from pigenus.core.config import Settings
from pigenus.db import session as db_session
from pigenus.db.orm import MemoryItem, Message, SessionRecord
from pigenus.db.session import init_db
from pigenus.memory.store import remember
from pigenus.workers.runner import MaintenanceWorker
from pigenus.workers.maintenance_tasks import run_maintenance_task


def test_maintenance_tasks_summarize_compress_and_brief():
    settings = Settings(
        database_url="sqlite://",
        admin_token="test-admin-token-with-enough-length",
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
    )
    init_db(settings)
    assert db_session.SessionLocal is not None
    with db_session.SessionLocal() as session:
        record = SessionRecord(title="Maintenance test")
        session.add(record)
        session.flush()
        session.add_all(
            [
                Message(session_id=record.id, role="user", content="PiGenus remembers context."),
                Message(session_id=record.id, role="assistant", content="PiGenus coordinates work."),
            ]
        )
        remember(
            session,
            namespace="charter",
            key="identity",
            value="first",
            importance=50,
        )
        remember(
            session,
            namespace="charter",
            key="identity",
            value="second",
            importance=90,
        )

        summary = run_maintenance_task(
            session,
            settings,
            job_type="maintenance.summarize_sessions",
            payload={},
        )
        assert summary["sessions_summarized"] == 1
        session.refresh(record)
        assert "2 messages" in record.summary

        compressed = run_maintenance_task(
            session,
            settings,
            job_type="maintenance.compress_memory",
            payload={},
        )
        assert compressed["removed_duplicates"] == 1
        remaining = session.query(MemoryItem).filter_by(namespace="charter", key="identity").all()
        assert len(remaining) == 1
        assert remaining[0].importance == 90

        briefing = run_maintenance_task(
            session,
            settings,
            job_type="maintenance.daily_briefing",
            payload={},
        )
        assert "briefing_key" in briefing
        assert "PiGenus daily briefing" in briefing["briefing"]


def test_maintenance_worker_leases_and_acks_job():
    settings = Settings(
        database_url="sqlite://",
        admin_token="test-admin-token-with-enough-length",
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
    )
    init_db(settings)
    fake_client = FakeWorkerClient(
        jobs=[
            {
                "id": 7,
                "job_type": "maintenance.rotate_logs",
                "payload": {},
            }
        ]
    )
    worker = MaintenanceWorker(
        settings=settings,
        client=fake_client,
        worker_id=3,
        sleep_seconds=0,
        max_jobs=1,
    )
    handled = worker.run_once()
    assert handled == 1
    assert fake_client.heartbeats == 1
    assert fake_client.acks[0]["job_id"] == 7
    assert fake_client.failures == []


class FakeWorkerClient:
    def __init__(self, jobs):
        self.jobs = jobs
        self.heartbeats = 0
        self.acks = []
        self.failures = []

    def heartbeat(self, worker_id, *, capabilities):
        self.heartbeats += 1
        assert worker_id == 3
        assert capabilities == ["maintenance"]
        return {}

    def lease(self, worker_id, *, max_jobs):
        assert worker_id == 3
        assert max_jobs == 1
        return self.jobs

    def ack(self, worker_id, job_id, result):
        self.acks.append({"worker_id": worker_id, "job_id": job_id, "result": result})
        return {}

    def fail(self, worker_id, job_id, error, *, retry=True):
        self.failures.append(
            {"worker_id": worker_id, "job_id": job_id, "error": error, "retry": retry}
        )
        return {}
