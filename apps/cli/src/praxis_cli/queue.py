"""Redis Streams helpers for publishing and consuming events."""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Dict, Optional, Set
from uuid import UUID

from redis.asyncio import Redis

from .config import Settings, get_settings
from .events import EventEnvelope, SessionInstruction

STREAM_BLOCK_MS = 500
DEFAULT_BATCH_SIZE = 20


class RedisQueue:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._redis = Redis.from_url(self.settings.redis_url.unicode_string(), decode_responses=True)
        self._seen_event_ids: Set[UUID] = set()

    async def publish_session_instruction(self, instruction: SessionInstruction) -> str:
        payload = instruction.model_dump_json()
        return await self._redis.xadd(
            self.settings.session_stream,
            {"event_id": str(instruction.session_id), "payload": payload},
        )

    async def publish_event(self, event: EventEnvelope, stream: Optional[str] = None) -> str:
        payload = event.model_dump_json()
        stream_name = stream or self.settings.progress_stream
        return await self._redis.xadd(stream_name, {"event_id": str(event.event_id), "payload": payload})

    async def read_events(
        self,
        stream: Optional[str] = None,
        last_id: str = "$",
        block_ms: int = STREAM_BLOCK_MS,
        count: int = DEFAULT_BATCH_SIZE,
    ) -> AsyncIterator[EventEnvelope]:
        stream_name = stream or self.settings.progress_stream
        latest_id = last_id
        while True:
            response = await self._redis.xread({stream_name: latest_id}, block=block_ms, count=count)
            if not response:
                await asyncio.sleep(block_ms / 1000)
                continue
            for _, entries in response:
                for message_id, fields in entries:
                    event_id = fields.get("event_id")
                    payload = fields.get("payload")
                    if not payload:
                        continue
                    if event_id:
                        uuid = UUID(event_id)
                        if uuid in self._seen_event_ids:
                            continue
                        self._seen_event_ids.add(uuid)
                    latest_id = message_id
                    yield EventEnvelope.model_validate(json.loads(payload))

    async def close(self) -> None:
        await self._redis.aclose()


async def ensure_streams(settings: Optional[Settings] = None) -> None:
    cfg = settings or get_settings()
    redis = Redis.from_url(cfg.redis_url.unicode_string(), decode_responses=True)
    try:
        for stream_name in {cfg.session_stream, cfg.progress_stream}:
            exists = await redis.exists(stream_name)
            if not exists:
                await redis.xadd(stream_name, {"bootstrap": "1"})
                await redis.xtrim(stream_name, maxlen=0)
    finally:
        await redis.aclose()
