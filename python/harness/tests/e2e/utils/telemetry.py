from __future__ import annotations

from dataclasses import dataclass
from time import time
from uuid import uuid4


@dataclass
class TelemetrySpan:
    trace_id: str
    span_id: str
    name: str
    status: str
    llm_client: str
    latency_ms: int
    tokens: int = 0
    cost_usd: float = 0.0


def emit_span(name: str, status: str, llm_client: str, latency_ms: int) -> TelemetrySpan:
    return TelemetrySpan(
        trace_id=uuid4().hex,
        span_id=uuid4().hex,
        name=name,
        status=status,
        llm_client=llm_client,
        latency_ms=latency_ms,
    )


def as_dict(span: TelemetrySpan) -> dict[str, object]:
    return {
        "trace_id": span.trace_id,
        "span_id": span.span_id,
        "name": span.name,
        "status": span.status,
        "llm_client": span.llm_client,
        "latency_ms": span.latency_ms,
        "tokens": span.tokens,
        "cost_usd": span.cost_usd,
        "ts": time(),
    }
