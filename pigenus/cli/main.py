from __future__ import annotations

import argparse
from pathlib import Path

from pigenus.core.orchestrator import DEMO_TEXT, SimpleOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("run-demo", help="Run the Phase 1 local memory demo.")
    demo.add_argument("--db", default="pigenus.sqlite3", help="SQLite database path.")
    demo.add_argument("--text", default=DEMO_TEXT, help="Input text for the demo flow.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-demo":
        orchestrator = SimpleOrchestrator(Path(args.db))
        try:
            result = orchestrator.run_demo(args.text)
        finally:
            orchestrator.close()

        print(f"Final response: {result.final_response}")
        print(f"Created memory object ID: {result.memory_id}")
        print(f"Events stored: {result.events_stored}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
