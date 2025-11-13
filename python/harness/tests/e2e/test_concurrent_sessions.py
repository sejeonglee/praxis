from __future__ import annotations

import anyio

from tests.e2e.utils.mock_llm import load_concurrent_sessions
from tests.e2e.utils.session_bus import SessionBus


async def _play_session(bus: SessionBus, session_id: str) -> None:
    sessions = {sid: steps for sid, steps in load_concurrent_sessions()}
    for event in sessions[session_id]:
        await bus.record(session_id, f"{event.type}:{event.payload.get('note', '')}")


def test_sessions_do_not_share_state() -> None:
    bus = SessionBus()

    async def runner() -> None:
        async with anyio.create_task_group() as tg:
            tg.start_soon(_play_session, bus, "alpha")
            tg.start_soon(_play_session, bus, "beta")

    anyio.run(runner)

    assert bus.history("alpha")
    assert bus.history("beta")
    assert bus.history("alpha") != bus.history("beta"), "histories must remain isolated"
