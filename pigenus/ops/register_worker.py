from __future__ import annotations

import argparse
import os

from pigenus.ops.http import post_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus-register-worker")
    parser.add_argument("--base-url", default=os.getenv("PIGENUS_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--admin-token", default=os.getenv("PIGENUS_ADMIN_TOKEN"))
    parser.add_argument("--name", default=os.getenv("PIGENUS_REGISTER_WORKER_NAME", "pigenus-maintenance"))
    parser.add_argument(
        "--capability",
        action="append",
        dest="capabilities",
        default=None,
        help="Worker capability. Repeat for multiple capabilities.",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.admin_token:
        raise SystemExit("PIGENUS_ADMIN_TOKEN or --admin-token is required")
    capabilities = args.capabilities or ["maintenance"]
    response = register_worker(
        base_url=args.base_url,
        admin_token=args.admin_token,
        name=args.name,
        capabilities=capabilities,
        timeout=args.timeout,
    )
    print(f"PIGENUS_WORKER_ID={response['worker_id']}")
    print(f"PIGENUS_WORKER_TOKEN={response['token']}")
    return 0


def register_worker(
    *,
    base_url: str,
    admin_token: str,
    name: str,
    capabilities: list[str],
    timeout: float = 10.0,
) -> dict:
    return post_json(
        f"{base_url.rstrip('/')}/workers/register",
        {"name": name, "capabilities": capabilities},
        token=admin_token,
        timeout=timeout,
    )
