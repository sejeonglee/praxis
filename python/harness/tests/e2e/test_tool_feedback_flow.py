from __future__ import annotations

from tests.e2e.utils.mock_llm import load_tool_feedback_scenario


def test_tool_feedback_flow_contains_user_feedback() -> None:
    steps = load_tool_feedback_scenario()
    step_types = [step.type for step in steps]
    assert "user_feedback" in step_types, "mock flow must include user feedback"
    assert step_types.count("tool_call") >= 2, "flow should exercise multiple tools"
