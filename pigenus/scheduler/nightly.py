from __future__ import annotations

import threading
import time
from pigenus.core.config import Settings
from pigenus.core.logging import get_logger
from pigenus.core.time import utcnow
from pigenus.db.session import SessionLocal
from pigenus.services.maintenance import run_maintenance

logger = get_logger(__name__)


class NightlyScheduler:
    """Small in-process scheduler for Pi-friendly maintenance.

    Phase 1 keeps this intentionally boring. Later milestones can move specific tasks to the job
    queue while keeping this class as the trigger point.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_run_date: str | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, name="pigenus-nightly", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        while not self._stop.is_set():
            now = utcnow()
            run_key = now.date().isoformat()
            if now.hour == self.settings.nightly_hour_utc and self._last_run_date != run_key:
                self.run_once()
                self._last_run_date = run_key
            time.sleep(60)

    def run_once(self) -> dict[str, int]:
        if SessionLocal is None:
            logger.warning("nightly_skipped_database_not_initialized")
            return {
                "requeued_stuck_jobs": 0,
                "stale_workers_marked_offline": 0,
                "maintenance_jobs_created": 0,
            }
        with SessionLocal() as session:
            result = run_maintenance(session, self.settings)
        logger.info(
            "nightly_maintenance_complete",
            extra={
                "requeued_stuck_jobs": result["requeued_stuck_jobs"],
                "stale_workers_marked_offline": result["stale_workers_marked_offline"],
                "backup_path": result["backup_path"],
                "maintenance_jobs_created": result["maintenance_jobs_created"],
            },
        )
        return {
            "requeued_stuck_jobs": int(result["requeued_stuck_jobs"] or 0),
            "stale_workers_marked_offline": int(result["stale_workers_marked_offline"] or 0),
            "maintenance_jobs_created": int(result["maintenance_jobs_created"] or 0),
        }
