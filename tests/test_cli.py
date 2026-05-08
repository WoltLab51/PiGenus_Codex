from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4


def db_path(name: str) -> Path:
    root = Path(".testdata") / "phase1-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}-{uuid4().hex}.sqlite3"


def test_run_demo_cli_works_from_module_entrypoint():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pigenus.cli.main",
            "run-demo",
            "--db",
            str(db_path("cli")),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Final response: Gespeichert: PiGenus ist der Zellkern." in result.stdout
    assert "Created memory object ID: mem_" in result.stdout
    assert "Events stored: 5" in result.stdout
