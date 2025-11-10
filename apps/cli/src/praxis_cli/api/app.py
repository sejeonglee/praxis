"""Litestar control-plane application."""
from __future__ import annotations

from typing import Any, Dict

from litestar import Litestar, Router, get
from redis.asyncio import Redis

from ..config import get_settings


@get("/health")
async def health_check() -> Dict[str, Any]:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url.unicode_string(), decode_responses=True)
    status = "ok"
    try:
        await redis.ping()
        redis_status = "connected"
    except Exception:  # pragma: no cover - network issues surfaced in response payload
        status = "degraded"
        redis_status = "disconnected"
    finally:
        await redis.aclose()
    return {"status": status, "redis": redis_status, "mocks": "idle"}


app = Litestar(route_handlers=[Router(path="", route_handlers=[health_check])])
