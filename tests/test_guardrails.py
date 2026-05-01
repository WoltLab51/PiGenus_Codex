from __future__ import annotations

from pathlib import Path

from pigenus.ops.guardrails import _dependency_name, run_guardrails


def test_repository_guardrails_pass():
    result = run_guardrails(Path.cwd())
    assert result.errors == []


def test_dependency_name_normalization():
    assert _dependency_name("uvicorn[standard]>=0.29,<1.0") == "uvicorn"
    assert _dependency_name("llama_cpp_python>=1") == "llama-cpp-python"
