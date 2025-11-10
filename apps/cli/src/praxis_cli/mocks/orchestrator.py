"""Simulated agent loop that publishes deterministic events."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from ..events import EventEnvelope, EventSource, SessionInstruction, Stage


class MockOrchestrator:
    def __init__(self) -> None:
        self._running_sessions: set[str] = set()

    async def run(self, instruction: SessionInstruction) -> List[EventEnvelope]:
        self._running_sessions.add(str(instruction.session_id))
        await asyncio.sleep(0.01)
        now = datetime.now(timezone.utc)
        return [
            EventEnvelope(
                event_id=uuid4(),
                session_id=instruction.session_id,
                stage=Stage.PLAN,
                ts=now,
                payload={"note": "Mock plan created"},
                source=EventSource.ORCHESTRATOR,
            )
        ]
