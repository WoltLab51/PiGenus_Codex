from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass
class PiGenusApiClient:
    base_url: str
    token: str
    timeout: float = 30.0

    def heartbeat(self, worker_id: int, *, capabilities: list[str]) -> dict[str, Any]:
        return self._post(
            f"/workers/{worker_id}/heartbeat",
            {"status": "online", "capabilities": capabilities},
        )

    def lease(self, worker_id: int, *, max_jobs: int = 1) -> list[dict[str, Any]]:
        response = self._post(f"/jobs/lease/{worker_id}", {"max_jobs": max_jobs})
        return list(response.get("jobs", []))

    def ack(self, worker_id: int, job_id: int, result: dict[str, Any]) -> dict[str, Any]:
        return self._post(f"/jobs/{job_id}/ack/{worker_id}", {"result": result})

    def fail(self, worker_id: int, job_id: int, error: str, *, retry: bool = True) -> dict[str, Any]:
        return self._post(f"/jobs/{job_id}/fail/{worker_id}", {"error": error, "retry": retry})

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url.rstrip("/") + path,
            data=body,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"PiGenus API returned {exc.code}: {detail}") from exc
        return json.loads(raw) if raw else {}
