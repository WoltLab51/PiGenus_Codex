from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from pigenus.api.routes import admin, health, jobs, memory, sessions, workers
from pigenus.core.config import Settings
from pigenus.core.logging import configure_logging, get_logger
from pigenus.db.session import init_db
from pigenus.scheduler.nightly import NightlyScheduler

logger = get_logger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(settings)
        logger.info("pigenus_started", extra={"database_url": settings.safe_database_url})
        if settings.enable_scheduler:
            app.state.nightly_scheduler.start()
        try:
            yield
        finally:
            app.state.nightly_scheduler.stop()
            logger.info("pigenus_stopped")

    app = FastAPI(
        title="PiGenus",
        description="Private orchestration and memory node for the GENUS ecosystem.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.nightly_scheduler = NightlyScheduler(settings)

    app.include_router(health.router)
    app.include_router(admin.router)
    app.include_router(workers.router)
    app.include_router(jobs.router)
    app.include_router(sessions.router)
    app.include_router(memory.router)

    return app


app = create_app()


def run() -> None:
    settings = Settings.from_env()
    uvicorn.run(
        "pigenus.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
