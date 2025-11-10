from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from praxis_cli import queue
from praxis_cli.config import Settings
from praxis_cli.events import EventEnvelope, EventSource, SessionInstruction, Stage


class FakeRedis:
    def __init__(self) -> None:
        self.added = []
        self._read_calls = 0

    async def xadd(self, stream, payload):
        self.added.append((stream, payload))
        return f"1-{len(self.added)}"

    async def xread(self, streams, block, count):
        self._read_calls += 1
        if self._read_calls > 1:
            return []
        event = EventEnvelope(
            event_id=uuid4(),
            session_id=uuid4(),
            stage=Stage.OBSERVE,
            ts=datetime.now(timezone.utc),
            payload={"note": "mock"},
            source=EventSource.MOCK_LLM,
        )
        payload = json.dumps(event.model_dump())
        entries = [(f"event-{self._read_calls}", {"event_id": str(event.event_id), "payload": payload})]
        # Duplicate entry to assert dedupe uses event_id
        entries.append((f"event-{self._read_calls+1}", {"event_id": str(event.event_id), "payload": payload}))
        stream_name = next(iter(streams))
        return [(stream_name, entries)]

    async def exists(self, *_):
        return True

    async def aclose(self):
        return None

    async def ping(self):
        return True


@pytest.mark.asyncio
async def test_queue_publishes_and_dedupes(monkeypatch):
    settings = Settings()
    fake = FakeRedis()
    monkeypatch.setattr(queue, "Redis", type("_Factory", (), {"from_url": staticmethod(lambda *_, **__: fake)}) )
    client = queue.RedisQueue(settings)
    instruction = SessionInstruction(session_id=uuid4(), start_instruction="demo")
    message_id = await client.publish_session_instruction(instruction)
    assert message_id == "1-1"
    event = EventEnvelope(
        event_id=uuid4(),
        session_id=instruction.session_id,
        stage=Stage.PLAN,
        ts=datetime.now(timezone.utc),
        payload={"note": "starting"},
        source=EventSource.ORCHESTRATOR,
    )
    await client.publish_event(event)
    iterator = client.read_events()
    first_event = await asyncio.wait_for(iterator.__anext__(), timeout=1)
    assert first_event.payload["note"] == "mock"
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(iterator.__anext__(), timeout=0.1)
    await client.close()
