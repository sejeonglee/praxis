"""Structured logging + OpenTelemetry helpers."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

import structlog
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from .config import get_settings

_LOGGER: Optional[structlog.stdlib.BoundLogger] = None


def configure_logging() -> structlog.stdlib.BoundLogger:
    global _LOGGER
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.log_level)),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
    )
    _LOGGER = structlog.get_logger("praxis-cli")
    return _LOGGER


def get_logger() -> structlog.stdlib.BoundLogger:
    return _LOGGER or configure_logging()


def configure_tracer() -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": "praxis-cli"}))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


@contextmanager
def telemetry_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> Iterator[None]:
    tracer = trace.get_tracer_provider().get_tracer("praxis-cli")
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span
