from __future__ import annotations

from tests.e2e.utils.telemetry import as_dict, emit_span


def test_emit_span_defaults_tokens_and_cost_to_zero() -> None:
    span = emit_span("mock-suite", "OK", "mock", 42)
    data = as_dict(span)
    assert data["tokens"] == 0
    assert data["cost_usd"] == 0.0
    assert data["llm_client"] == "mock"
