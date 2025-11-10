from __future__ import annotations

import anyio


class SessionBus:
    """Tiny helper that ensures async tasks do not leak state across sessions."""

    def __init__(self) -> None:
        self._messages: dict[str, list[str]] = {}

    async def record(self, session_id: str, note: str) -> None:
        await anyio.sleep(0)
        self._messages.setdefault(session_id, []).append(note)

    def history(self, session_id: str) -> list[str]:
        return self._messages.get(session_id, [])
