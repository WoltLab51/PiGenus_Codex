from __future__ import annotations

import argparse
import os

from pigenus.ops.http import get_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus-healthcheck")
    parser.add_argument("--base-url", default=os.getenv("PIGENUS_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--admin-token", default=os.getenv("PIGENUS_ADMIN_TOKEN"))
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--admin",
        action="store_true",
        help="Also check authenticated admin status.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_healthcheck(
        base_url=args.base_url,
        admin_token=args.admin_token,
        include_admin=args.admin,
        timeout=args.timeout,
    )
    print(result)
    return 0


def run_healthcheck(
    *,
    base_url: str,
    admin_token: str | None,
    include_admin: bool,
    timeout: float = 10.0,
) -> dict:
    base = base_url.rstrip("/")
    health = get_json(f"{base}/health", timeout=timeout)
    if health.get("status") != "ok" or health.get("database") != "ok":
        raise RuntimeError(f"unhealthy response: {health}")
    result = {"health": health}
    if include_admin:
        if not admin_token:
            raise RuntimeError("--admin requires PIGENUS_ADMIN_TOKEN or --admin-token")
        result["admin_status"] = get_json(
            f"{base}/admin/status",
            token=admin_token,
            timeout=timeout,
        )
    return result
