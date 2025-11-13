from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_and_lock_exist() -> None:
    pyproject = ROOT / "pyproject.toml"
    uv_lock = ROOT / "uv.lock"
    assert pyproject.exists(), "pyproject.toml missing"
    assert uv_lock.exists(), "uv.lock missing"


def test_python_version_matches_pin() -> None:
    version_file = Path(ROOT.parents[2]) / ".python-version"
    if not version_file.exists():
        pytest.skip(".python-version not pinned yet")
    pinned = version_file.read_text(encoding="utf-8").strip()
    assert pinned.startswith("3.14"), "Python version pin must be 3.14.x"  # constitution requirement
