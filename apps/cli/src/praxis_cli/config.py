"""Configuration helpers for the Praxis CLI."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, RedisDsn, StrictInt, StrictStr, ValidationError

DEFAULT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseModel):
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    session_stream: StrictStr = Field(default="praxis:sessions")
    progress_stream: StrictStr = Field(default="praxis:progress")
    litestar_host: StrictStr = Field(default="127.0.0.1")
    litestar_port: StrictInt = Field(default=8090, ge=1, le=65535)
    default_scenario: StrictStr = Field(default="reference")
    otel_exporter_otlp_endpoint: StrictStr = Field(default="http://localhost:4318")
    log_level: StrictStr = Field(default="INFO")


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@lru_cache(maxsize=1)
def get_settings(env_file: Optional[Path] = None) -> Settings:
    """Load settings from environment (and optional .env file)."""
    env_path = env_file or DEFAULT_ENV_PATH
    _load_env_file(env_path)
    try:
        return Settings(
            redis_url=os.getenv("REDIS_URL", Settings.model_fields["redis_url"].default),
            session_stream=os.getenv("PRAXIS_SESSION_STREAM", Settings.model_fields["session_stream"].default),
            progress_stream=os.getenv("PRAXIS_PROGRESS_STREAM", Settings.model_fields["progress_stream"].default),
            litestar_host=os.getenv("LITESTAR_HOST", Settings.model_fields["litestar_host"].default),
            litestar_port=int(os.getenv("LITESTAR_PORT", Settings.model_fields["litestar_port"].default)),
            default_scenario=os.getenv("E2E_SCENARIO", Settings.model_fields["default_scenario"].default),
            otel_exporter_otlp_endpoint=os.getenv(
                "OTEL_EXPORTER_OTLP_ENDPOINT", Settings.model_fields["otel_exporter_otlp_endpoint"].default
            ),
            log_level=os.getenv("LOG_LEVEL", Settings.model_fields["log_level"].default),
        )
    except (ValidationError, ValueError) as exc:
        raise RuntimeError("Invalid CLI environment configuration") from exc
