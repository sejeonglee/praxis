from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from typer.testing import CliRunner

from praxis_cli import cli


runner = CliRunner()


def write_instruction(tmp_path: Path, text: str) -> Path:
    payload = {"start_instruction": text, "metadata": {"scenario": "reference"}}
    file_path = tmp_path / "instruction.json"
    file_path.write_text(json.dumps(payload))
    return file_path


def test_cli_requires_instruction_file() -> None:
    result = runner.invoke(cli.app, ["run"])
    assert result.exit_code != 0
    assert "instruction-file" in (result.stderr or result.stdout or "")


def test_cli_parses_instruction_file(monkeypatch, tmp_path: Path) -> None:
    instruction_path = write_instruction(tmp_path, "Mock task")
    captured = {}

    class FakeQueue:
        async def publish_session_instruction(self, instruction):
            captured["instruction"] = instruction
            return "1-0"

        async def close(self):
            return None

    monkeypatch.setattr(cli, "RedisQueue", lambda *_, **__: FakeQueue())
    result = runner.invoke(cli.app, ["run", "--instruction-file", str(instruction_path)])
    assert result.exit_code == 0
    payload = captured["instruction"].model_dump()
    assert payload["start_instruction"] == "Mock task"
    assert UUID(str(payload["session_id"]))
