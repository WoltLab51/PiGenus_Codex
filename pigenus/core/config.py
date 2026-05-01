from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator


class Settings(BaseModel):
    app_name: str = "PiGenus"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = "sqlite:///./data/pigenus.sqlite3"
    admin_token: str = Field(min_length=24)
    token_pepper: str = Field(default="development-token-pepper-change-me", min_length=16)
    log_level: str = "INFO"
    worker_lease_seconds: int = 900
    stuck_job_seconds: int = 3600
    worker_stale_seconds: int = 600
    backup_dir: str = "./backups"
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 120
    enable_scheduler: bool = False
    nightly_hour_utc: int = 2

    @field_validator("admin_token")
    @classmethod
    def reject_unsafe_admin_token(cls, value: str) -> str:
        unsafe = {"change-me", "password", "admin", "secret", "token"}
        if value.lower() in unsafe:
            raise ValueError("admin_token must be a long random secret")
        return value

    @field_validator("nightly_hour_utc")
    @classmethod
    def validate_nightly_hour(cls, value: int) -> int:
        if value < 0 or value > 23:
            raise ValueError("nightly_hour_utc must be between 0 and 23")
        return value

    @model_validator(mode="after")
    def reject_production_dev_secrets(self) -> "Settings":
        if (
            self.environment == "production"
            and self.token_pepper == "development-token-pepper-change-me"
        ):
            raise ValueError("PIGENUS_TOKEN_PEPPER must be set in production")
        return self

    @property
    def safe_database_url(self) -> str:
        if self.database_url.startswith("sqlite:///"):
            return self.database_url
        return "<redacted>"

    @property
    def sqlite_path(self) -> Path | None:
        if not self.database_url.startswith("sqlite:///"):
            return None
        raw_path = self.database_url.removeprefix("sqlite:///")
        return Path(raw_path)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            environment=os.getenv("PIGENUS_ENV", "development"),
            host=os.getenv("PIGENUS_HOST", "127.0.0.1"),
            port=int(os.getenv("PIGENUS_PORT", "8000")),
            database_url=os.getenv("PIGENUS_DATABASE_URL", "sqlite:///./data/pigenus.sqlite3"),
            admin_token=os.getenv("PIGENUS_ADMIN_TOKEN", ""),
            token_pepper=os.getenv("PIGENUS_TOKEN_PEPPER", "development-token-pepper-change-me"),
            log_level=os.getenv("PIGENUS_LOG_LEVEL", "INFO"),
            worker_lease_seconds=int(os.getenv("PIGENUS_WORKER_LEASE_SECONDS", "900")),
            stuck_job_seconds=int(os.getenv("PIGENUS_STUCK_JOB_SECONDS", "3600")),
            worker_stale_seconds=int(os.getenv("PIGENUS_WORKER_STALE_SECONDS", "600")),
            backup_dir=os.getenv("PIGENUS_BACKUP_DIR", "./backups"),
            rate_limit_enabled=os.getenv("PIGENUS_RATE_LIMIT_ENABLED", "true").lower()
            in {"1", "true", "yes"},
            rate_limit_requests_per_minute=int(
                os.getenv("PIGENUS_RATE_LIMIT_REQUESTS_PER_MINUTE", "120")
            ),
            enable_scheduler=os.getenv("PIGENUS_ENABLE_SCHEDULER", "false").lower()
            in {"1", "true", "yes"},
            nightly_hour_utc=int(os.getenv("PIGENUS_NIGHTLY_HOUR_UTC", "2")),
        )
