from __future__ import annotations

import argparse
import os
import time

from pigenus.core.config import Settings
from pigenus.core.logging import configure_logging, get_logger
from pigenus.db import session as db_session
from pigenus.db.session import init_db
from pigenus.workers.http_client import PiGenusApiClient
from pigenus.workers.maintenance_tasks import SUPPORTED_MAINTENANCE_JOBS, run_maintenance_task

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus-worker")
    parser.add_argument("--base-url", default=os.getenv("PIGENUS_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--worker-id", type=int, default=_env_int("PIGENUS_WORKER_ID"))
    parser.add_argument("--worker-token", default=os.getenv("PIGENUS_WORKER_TOKEN"))
    parser.add_argument("--sleep-seconds", type=float, default=float(os.getenv("PIGENUS_WORKER_SLEEP", "15")))
    parser.add_argument("--once", action="store_true", help="Run one lease cycle and exit.")
    parser.add_argument("--max-jobs", type=int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.worker_id is None or not args.worker_token:
        raise SystemExit("PIGENUS_WORKER_ID and PIGENUS_WORKER_TOKEN are required")

    settings = Settings.from_env()
    configure_logging(settings.log_level)
    init_db(settings)
    client = PiGenusApiClient(base_url=args.base_url, token=args.worker_token)
    worker = MaintenanceWorker(
        settings=settings,
        client=client,
        worker_id=args.worker_id,
        sleep_seconds=args.sleep_seconds,
        max_jobs=args.max_jobs,
    )
    worker.run(once=args.once)
    return 0


class MaintenanceWorker:
    def __init__(
        self,
        *,
        settings: Settings,
        client: PiGenusApiClient,
        worker_id: int,
        sleep_seconds: float = 15,
        max_jobs: int = 1,
    ) -> None:
        self.settings = settings
        self.client = client
        self.worker_id = worker_id
        self.sleep_seconds = sleep_seconds
        self.max_jobs = max_jobs

    def run(self, *, once: bool = False) -> None:
        while True:
            handled = self.run_once()
            if once:
                return
            if handled == 0:
                time.sleep(self.sleep_seconds)

    def run_once(self) -> int:
        self.client.heartbeat(self.worker_id, capabilities=["maintenance"])
        jobs = self.client.lease(self.worker_id, max_jobs=self.max_jobs)
        handled = 0
        for job in jobs:
            handled += 1
            self._handle_job(job)
        return handled

    def _handle_job(self, job: dict) -> None:
        job_id = int(job["id"])
        job_type = str(job["job_type"])
        if job_type not in SUPPORTED_MAINTENANCE_JOBS:
            self.client.fail(self.worker_id, job_id, f"unsupported maintenance job: {job_type}", retry=False)
            return
        if db_session.SessionLocal is None:
            self.client.fail(self.worker_id, job_id, "database is not initialized", retry=True)
            return
        try:
            with db_session.SessionLocal() as session:
                result = run_maintenance_task(
                    session,
                    self.settings,
                    job_type=job_type,
                    payload=dict(job.get("payload") or {}),
                )
            self.client.ack(self.worker_id, job_id, result)
            logger.info("maintenance_job_completed", extra={"job_id": job_id, "job_type": job_type})
        except Exception as exc:
            logger.exception("maintenance_job_failed", extra={"job_id": job_id, "job_type": job_type})
            self.client.fail(self.worker_id, job_id, str(exc), retry=True)


def _env_int(name: str) -> int | None:
    value = os.getenv(name)
    if value is None or value == "":
        return None
    return int(value)
