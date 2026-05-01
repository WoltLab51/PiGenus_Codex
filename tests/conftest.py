from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PIGENUS_ADMIN_TOKEN", "test-import-token-with-enough-length")

from pigenus.core.config import Settings
from pigenus.main import create_app


@pytest.fixture()
def admin_token() -> str:
    return "test-admin-token-with-enough-length"


@pytest.fixture()
def client(admin_token: str) -> TestClient:
    settings = Settings(
        database_url="sqlite://",
        admin_token=admin_token,
        token_pepper="test-token-pepper-with-enough-length",
        enable_scheduler=False,
    )
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
