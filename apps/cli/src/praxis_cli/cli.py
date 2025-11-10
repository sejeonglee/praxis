from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

import typer

from .config import get_settings
from .events import EventEnvelope, SessionInstruction
from .queue import RedisQueue
from .telemetry import configure_logging, telemetry_span

app = typer.Typer(help="Praxis event-driven CLI")


def _load_instruction(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise typer.BadParameter(f"Instruction file not found: {path}")
    raw = path.read_text().strip()
    if not raw:
        raise typer.BadParameter("Instruction file is empty")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"start_instruction": raw}


def build_instruction(payload: Dict[str, Any], session_id: Optional[UUID] = None) -> SessionInstruction:
    body = payload.copy()
    instruction_text = body.pop("start_instruction", None)
    if not instruction_text:
        raise typer.BadParameter("start_instruction missing from instruction payload")
    return SessionInstruction(
        session_id=session_id or uuid4(),
        start_instruction=instruction_text,
        mid_events=body.get("mid_events", []),
        metadata=body.get("metadata", {}),
        budget=body.get("budget"),
    )


async def _run_flow(instruction_file: Path) -> None:
    settings = get_settings()
    logger = configure_logging()
    queue = RedisQueue(settings)
    payload = _load_instruction(instruction_file)
    instruction = build_instruction(payload)
    await queue.publish_session_instruction(instruction)
    logger.info("session_published", session_id=str(instruction.session_id))
    try:
        async for event in queue.read_events():
            _log_event(logger, event)
            if event.stage.value == "final":
                break
    finally:
        await queue.close()


def _log_event(logger, event: EventEnvelope) -> None:
    with telemetry_span("cli.event", {"stage": event.stage.value, "source": event.source.value}):
        logger.info(
            "event",
            stage=event.stage.value,
            source=event.source.value,
            payload=event.payload,
            metrics=(event.metrics.model_dump() if event.metrics else None),
        )


@app.command()
def run(
    instruction_file: Path = typer.Option(..., exists=True, readable=True, help="Path to start instruction JSON file"),
) -> None:
    """Publish a session instruction and follow progress events."""
    asyncio.run(_run_flow(instruction_file))
