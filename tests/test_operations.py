from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pigenus.core.config import Settings
from pigenus.db.migrations import CURRENT_SCHEMA_VERSION, get_schema_version, migrate_database
from pigenus.db.session import build_engine, init_db
from pigenus.main import create_app
from pigenus.services.maintenance import create_sqlite_backup


@pytest.fixture()
def local_tmp_dir() -> Path:
    path = Path(".testdata") / f"ops-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def test_schema_migration_records_version(local_tmp_dir):
    settings = Settings(
        database_url=sqlite_url(local_tmp_dir / "pigenus.sqlite3"),
        admin_token="test-admin-token-with-enough-length",
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
    )
    engine = build_engine(settings)
    version = migrate_database(engine)
    assert version == CURRENT_SCHEMA_VERSION
    assert get_schema_version(engine) == CURRENT_SCHEMA_VERSION


def test_sqlite_backup_is_created(local_tmp_dir):
    settings = Settings(
        database_url=sqlite_url(local_tmp_dir / "pigenus.sqlite3"),
        backup_dir=str(local_tmp_dir / "backups"),
        admin_token="test-admin-token-with-enough-length",
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
    )
    init_db(settings)
    backup_path = create_sqlite_backup(settings)
    assert backup_path is not None
    assert (local_tmp_dir / "backups").exists()
    assert backup_path.endswith(".sqlite3")


def test_rate_limit_blocks_excess_authenticated_requests():
    settings = Settings(
        database_url="sqlite://",
        admin_token="test-admin-token-with-enough-length",
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
        rate_limit_enabled=True,
        rate_limit_requests_per_minute=2,
    )
    app = create_app(settings)
    headers = {"Authorization": "Bearer test-admin-token-with-enough-length"}
    with TestClient(app) as client:
        assert client.get("/admin/status", headers=headers).status_code == 200
        assert client.get("/admin/status", headers=headers).status_code == 200
        blocked = client.get("/admin/status", headers=headers)
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "rate limit exceeded"


def test_health_is_not_rate_limited():
    settings = Settings(
        database_url="sqlite://",
        admin_token="test-admin-token-with-enough-length",
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
        rate_limit_enabled=True,
        rate_limit_requests_per_minute=1,
    )
    app = create_app(settings)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200
