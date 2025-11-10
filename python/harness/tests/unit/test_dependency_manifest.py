from __future__ import annotations

from pathlib import Path

DEPENDENCIES = {"pytest", "anyio", "opentelemetry-sdk"}


def test_required_dependencies_listed_in_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    for dep in DEPENDENCIES:
        assert dep in text, f"{dep} missing from dependencies"
