from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_json(url: str, *, token: str | None = None, timeout: float = 10.0) -> dict[str, Any]:
    request = Request(url, headers=_headers(token), method="GET")
    return _send(request, timeout=timeout)


def post_json(
    url: str,
    payload: dict[str, Any],
    *,
    token: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**_headers(token), "Content-Type": "application/json"},
        method="POST",
    )
    return _send(request, timeout=timeout)


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _send(request: Request, *, timeout: float) -> dict[str, Any]:
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"connection failed: {exc.reason}") from exc
    return json.loads(raw) if raw else {}
