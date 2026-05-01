from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "docs/PIGENUS_CHARTER.md",
    "docs/ARCHITECTURE.md",
    "docs/MVP_ROADMAP.md",
    "docs/ROADMAP_GUARDRAILS.md",
    "docs/DEPLOYMENT.md",
    ".github/pull_request_template.md",
]

REQUIRED_CHARTER_TERMS = [
    "Persistence",
    "Orchestration",
    "Administration",
    "Interface Readiness",
    "Continuity",
    "Non-Negotiable Design Rule",
]

REQUIRED_ROADMAP_PHASES = [
    "Phase 1: Reliable Core",
    "Phase 2: Operational Hardening",
    "Phase 3: Memory and Session Workflows",
    "Phase 4: Developer Orchestration",
]

FORBIDDEN_RUNTIME_DEPENDENCIES = {
    "torch",
    "tensorflow",
    "transformers",
    "llama-cpp-python",
    "vllm",
    "chromadb",
    "qdrant-client",
}


@dataclass
class GuardrailResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def run_guardrails(root: Path) -> GuardrailResult:
    errors: list[str] = []
    warnings: list[str] = []

    _check_required_files(root, errors)
    _check_charter(root, errors)
    _check_roadmap(root, errors)
    _check_docs_links(root, errors)
    _check_pyproject(root, errors, warnings)
    return GuardrailResult(errors=errors, warnings=warnings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pigenus-guardrails")
    parser.add_argument("--root", default=".", help="Repository root.")
    args = parser.parse_args(argv)

    result = run_guardrails(Path(args.root).resolve())
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    if result.ok:
        print("PiGenus guardrails passed")
        return 0
    return 1


def _check_required_files(root: Path, errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not (root / path).exists():
            errors.append(f"required file missing: {path}")


def _check_charter(root: Path, errors: list[str]) -> None:
    charter = _read(root / "docs/PIGENUS_CHARTER.md")
    for term in REQUIRED_CHARTER_TERMS:
        if term.lower() not in charter.lower():
            errors.append(f"charter is missing required term: {term}")
    forbidden_identity = "main llm"
    if forbidden_identity not in charter.lower():
        errors.append("charter must explicitly state PiGenus is not the main LLM")


def _check_roadmap(root: Path, errors: list[str]) -> None:
    roadmap = _read(root / "docs/MVP_ROADMAP.md")
    for phase in REQUIRED_ROADMAP_PHASES:
        if phase not in roadmap:
            errors.append(f"roadmap is missing required phase: {phase}")


def _check_docs_links(root: Path, errors: list[str]) -> None:
    readme = _read(root / "README.md")
    architecture = _read(root / "docs/ARCHITECTURE.md")
    contributing = _read(root / "CONTRIBUTING.md")
    if "docs/PIGENUS_CHARTER.md" not in readme:
        errors.append("README must link to docs/PIGENUS_CHARTER.md")
    if "PIGENUS_CHARTER.md" not in architecture:
        errors.append("architecture must link to PIGENUS_CHARTER.md")
    if "MVP_ROADMAP.md" not in contributing:
        errors.append("CONTRIBUTING must link to MVP_ROADMAP.md")


def _check_pyproject(root: Path, errors: list[str], warnings: list[str]) -> None:
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        errors.append("pyproject.toml is missing")
        return
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    dependencies = project.get("dependencies", [])
    normalized = {_dependency_name(dep) for dep in dependencies}
    banned = sorted(normalized & FORBIDDEN_RUNTIME_DEPENDENCIES)
    if banned:
        errors.append(
            "runtime dependencies include heavy/core-forbidden packages: " + ", ".join(banned)
        )
    scripts = project.get("scripts", {})
    for script in ["pigenus", "pigenus-admin", "pigenus-worker", "pigenus-guardrails"]:
        if script not in scripts:
            errors.append(f"required script missing from pyproject: {script}")
    if len(dependencies) > 12:
        warnings.append("runtime dependency count is growing; verify Raspberry Pi suitability")


def _dependency_name(requirement: str) -> str:
    chars = []
    for char in requirement:
        if char.isalnum() or char in {"-", "_", "."}:
            chars.append(char)
            continue
        break
    return "".join(chars).lower().replace("_", "-")


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
