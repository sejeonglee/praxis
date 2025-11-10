from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import json


@dataclass
class ScenarioStep:
    type: str
    payload: dict


def load_tool_feedback_scenario() -> list[ScenarioStep]:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "tool_feedback_flow.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    steps: list[ScenarioStep] = []
    for raw in data["steps"]:
        payload = {k: v for k, v in raw.items() if k != "type"}
        steps.append(ScenarioStep(type=raw["type"], payload=payload))
    return steps


def load_concurrent_sessions() -> list[tuple[str, Iterable[ScenarioStep]]]:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "concurrent_sessions.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    sessions: list[tuple[str, Iterable[ScenarioStep]]] = []
    for session in data["sessions"]:
        steps = [ScenarioStep(type=raw["type"], payload={k: v for k, v in raw.items() if k != "type"}) for raw in session["events"]]
        sessions.append((session["session_id"], steps))
    return sessions
