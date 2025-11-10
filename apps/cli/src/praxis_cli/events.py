"""Data contracts shared by the CLI, mocks, and automated scripts."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, StrictFloat, StrictInt, StrictStr


class MidEventKind(str, Enum):
    HUMAN_FEEDBACK = "human_feedback"
    ENV_UPDATE = "env_update"
    TIMER = "timer"
    BUDGET_ALERT = "budget_alert"


class Stage(str, Enum):
    PLAN = "plan"
    REASON = "reason"
    ACT = "act"
    OBSERVE = "observe"
    VERIFY = "verify"
    REPLAN = "replan"
    FINAL = "final"
    MID_EVENT = "mid_event"


class EventSource(str, Enum):
    CLI = "cli"
    MOCK_LLM = "mock_llm"
    MOCK_DB = "mock_db"
    ORCHESTRATOR = "orchestrator"
    VERIFIER = "verifier"


class Budget(BaseModel):
    tokens: Optional[int] = Field(default=None, ge=0)
    wall_ms: Optional[int] = Field(default=None, ge=0)


class MidEvent(BaseModel):
    id: UUID
    ts: datetime
    kind: MidEventKind
    payload: Dict[str, Any] = Field(default_factory=dict)


class Metrics(BaseModel):
    latency_ms: Optional[int] = Field(default=None, ge=0)
    tokens: Optional[int] = Field(default=None, ge=0)
    cost_usd: Optional[StrictFloat] = Field(default=None, ge=0)


class SessionInstruction(BaseModel):
    session_id: UUID
    start_instruction: StrictStr = Field(min_length=1)
    mid_events: List[MidEvent] = Field(default_factory=list)
    budget: Optional[Budget] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventEnvelope(BaseModel):
    event_id: UUID
    session_id: UUID
    stage: Stage
    ts: datetime
    payload: Dict[str, Any]
    source: EventSource
    metrics: Optional[Metrics] = None

    class Config:
        json_schema_extra = {
            "description": "Canonical schema for all queue messages across plan/act/observe/verify/final stages."
        }


class RunReport(BaseModel):
    session_id: UUID
    scenario: StrictStr
    start_ts: datetime
    end_ts: datetime
    events_checked: StrictInt = Field(ge=0)
    assertions: List[Dict[str, Any]]
    artifacts_path: StrictStr
