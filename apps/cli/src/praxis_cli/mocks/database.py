"""Deterministic mock DB service."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class MockDatabase:
    seed: int = 99

    async def query(self, session_id: UUID, request: str) -> dict:
        return {
            "session_id": str(session_id),
            "kind": "db",
            "content": {"rows": [{"id": 1, "value": f"result-{self.seed}"}]},
            "latency_ms": 80,
            "status": "success",
        }
