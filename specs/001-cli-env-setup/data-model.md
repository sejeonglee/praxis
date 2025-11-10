# Data Model

## SessionInstruction
- **Purpose**: Represents a CLI-initiated run and provides metadata for all downstream queue events.
- **Fields**:
  - `session_id` (UUID, required) — unique per CLI invocation, used to namespace queue streams and logs.
  - `start_instruction` (string, required, min 1 char) — operator goal forwarded to orchestrator/mocks.
  - `mid_events` (array<MidEvent>, optional) — scheduled interrupts (budget, timers, manual cues) seeded by CLI.
  - `budget` (object, optional) — `{ tokens:int, wall_ms:int }` for TTC guardrails.
  - `metadata` (object, optional) — CLI-provided context (e.g., scenario label) stored for reports.
- **Relationships**: Owns `mid_events`; referenced by every `EventEnvelope.session_id`.
- **Validation Rules**: `session_id` must be UUIDv4; `mid_events[*].ts` ISO-8601; `budget.tokens` >=0.
- **Lifecycle**: Created when CLI command validates input → becomes immutable; archived once final answer event delivered.

## EventEnvelope
- **Purpose**: Canonical structure for all queue messages (plan/progress/observation/final answer/interruption).
- **Fields**:
  - `event_id` (UUID, required) — dedupe key for at-least-once delivery.
  - `session_id` (UUID, required) — ties to `SessionInstruction`.
  - `stage` (enum: plan|reason|act|observe|verify|replan|final|mid_event) — indicates workflow phase.
  - `ts` (ISO-8601 string, required) — publication timestamp.
  - `payload` (object, required) — stage-specific content (summaries, artifacts, errors).
  - `metrics` (object, optional) — `{ latency_ms:int, tokens:int, cost_usd:float }` from mocks.
  - `source` (enum: cli|mock_llm|mock_db|orchestrator|verifier) — emitter of the event.
- **Relationships**: Consumed by CLI UI, mocks, and Litestar API; stored temporarily in Redis Streams with consumer group per component.
- **Validation Rules**: `stage` must align with allowed transitions (plan→act/observe, observe→verify, etc.); `payload` requires `note` for progress entries and `final_answer` for final stage.
- **State Transitions**: Ordered per session; each new event must reference the previous logical stage; duplicates ignored if `event_id` seen.

## MockServiceResponse
- **Purpose**: Deterministic outputs from mock LLM/DB workers used in unit/e2e tests.
- **Fields**:
  - `response_id` (UUID)
  - `session_id` (UUID)
  - `kind` (enum: llm|db)
  - `content` (string or object) — e.g., synthesized reasoning, query results.
  - `latency_ms` (int) — simulated runtime injected into `EventEnvelope.metrics`.
  - `status` (enum: success|error)
  - `error` (object, optional) — `{ code:str, message:str }` when `status=error`.
- **Relationships**: Converted into `EventEnvelope` by orchestrator mock; stored only in memory/logs.
- **Validation Rules**: `latency_ms` between 0 and 10_000; `content` must include deterministic seed for reproducibility.
- **Lifecycle**: Created on demand when orchestrator requests assistance → consumed immediately → optionally recorded in telemetry.

## RunReport
- **Purpose**: Output artifact from e2e script verifying event order and expectations.
- **Fields**:
  - `session_id` (UUID)
  - `scenario` (string)
  - `start_ts` / `end_ts` (ISO-8601)
  - `events_checked` (int)
  - `assertions` (array<{ name:string, status:pass|fail, details?:string }>)
  - `artifacts_path` (string) — location for logs/traces.
- **Relationships**: Generated after e2e run; referenced by CI and documentation.
- **Validation Rules**: `events_checked` must equal expected scenario length; at least one assertion recorded.
- **Lifecycle**: Created per script execution → persisted under `apps/cli/.reports/<timestamp>.json`.

## Supporting Types
- **MidEvent**: `{ id:UUID, ts:ISO-8601, kind:human_feedback|env_update|timer|budget_alert, payload:object }`.
- **TelemetryEntry**: `{ event_id:UUID, level:str, message:str, attributes:dict }` recorded via structlog/Otel.
