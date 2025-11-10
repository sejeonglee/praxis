"""Deterministic mock LLM responses for local testing."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class MockLLM:
    seed: int = 42

    async def run(self, session_id: UUID, prompt: str) -> dict:
        return {
            "session_id": str(session_id),
            "kind": "llm",
            "content": f"[mock-llm:{self.seed}] {prompt[:64]}",
            "latency_ms": 120,
            "status": "success",
        }
