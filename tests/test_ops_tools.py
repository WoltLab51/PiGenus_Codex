from __future__ import annotations

from pigenus.ops import healthcheck as healthcheck_module
from pigenus.ops import register_worker as register_worker_module


def test_healthcheck_checks_health_and_admin(monkeypatch):
    calls = []

    def fake_get_json(url, *, token=None, timeout=10.0):
        calls.append({"url": url, "token": token, "timeout": timeout})
        if url.endswith("/health"):
            return {"status": "ok", "service": "pigenus", "database": "ok"}
        return {"workers_total": 1, "jobs_queued": 0}

    monkeypatch.setattr(healthcheck_module, "get_json", fake_get_json)
    result = healthcheck_module.run_healthcheck(
        base_url="http://pi.local:8000/",
        admin_token="admin-token",
        include_admin=True,
        timeout=3,
    )

    assert result["health"]["status"] == "ok"
    assert result["admin_status"]["workers_total"] == 1
    assert calls[0]["url"] == "http://pi.local:8000/health"
    assert calls[1]["token"] == "admin-token"


def test_register_worker_posts_expected_payload(monkeypatch):
    calls = []

    def fake_post_json(url, payload, *, token=None, timeout=10.0):
        calls.append({"url": url, "payload": payload, "token": token, "timeout": timeout})
        return {"worker_id": 4, "token": "worker-token", "status": "registered"}

    monkeypatch.setattr(register_worker_module, "post_json", fake_post_json)
    result = register_worker_module.register_worker(
        base_url="http://127.0.0.1:8000",
        admin_token="admin-token",
        name="pigenus-maintenance",
        capabilities=["maintenance"],
        timeout=5,
    )

    assert result["worker_id"] == 4
    assert calls == [
        {
            "url": "http://127.0.0.1:8000/workers/register",
            "payload": {"name": "pigenus-maintenance", "capabilities": ["maintenance"]},
            "token": "admin-token",
            "timeout": 5,
        }
    ]
