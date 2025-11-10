# Implementation Plan (Spec-Driven, TDD-First)

This plan enumerates the steps to implement OBJECTIVE.md with strict TDD and continuous validation via full unit and mocking E2E tests. Each step lists deliverables, tests (RED→GREEN), and notes. Commit at every RED→GREEN boundary.

## Phase 0 — Workspace and Scaffolding

- Deliverables
  - PNPM workspace root (packages under `/apps/*` and `/core/*`).
  - Python project layout with `uv` (virtualenv, `pyproject.toml`).
  - Repo scripts: `scripts/test.unit.sh`, `scripts/test.e2e.mock.sh` (see TESTING.md).
- Tests (RED→GREEN)
  - RED: Empty test skeletons for unit and mock E2E.
  - GREEN: Runners execute and report “0 passed” without failure; CI jobs wired.
- Notes: No product logic; just infra and test harness.

## Phase 1 — Canonical Contracts

- Deliverables
  - `/core/contracts/agent-io.schema.json` (Agent I/O envelope).
  - `/core/contracts/types.ts` (TS types: Progress, Action, FinalAnswer, etc.).
  - `/core/contracts/acp.openapi.yaml` (minimal ACP endpoints: `/stream`, `/invoke`, `/action`).
- Tests (RED→GREEN)
  - RED: Failing unit tests for JSON Schema validation (good/bad payloads), TS type compatibility, and OpenAPI presence.
  - GREEN: Schema validates; types compile; OpenAPI exists and lints.
- Notes: Contracts are normative; all later steps depend on them.

## Phase 2 — Mock API (ACP over SSE)

- Deliverables
  - `/apps/api` mock server exposing:
    - `GET /stream` SSE streaming CloudEvents.
    - `POST /invoke` returns a session id.
    - `POST /action` accepts `cancel|truncate|inject`.
- Tests (RED→GREEN)
  - RED: Mock E2E test expects ordered event types: `agent.progress.*` → `agent.final.ready`.
  - GREEN: SSE client receives events in order within time bounds.
- Notes: No orchestrator logic yet—pure mock responses.

## Phase 3 — Orchestrator Skeleton (State Graph)

- Deliverables
  - `/core/orchestrator`: Idle → Plan → (Act ↔ Observe)* → Verify → Replan → Finalize, with explicit `interrupt()` checkpoints.
  - In-memory session store; resumable state.
- Tests (RED→GREEN)
  - RED: Unit tests for transitions and pause/resume on `mid_events`.
  - GREEN: Deterministic transitions; interruptions resume at checkpoints.
- Notes: Keep deterministic; no LLM/tool execution yet.

## Phase 4 — Minimal Skills Discovery and Progressive Disclosure

- Deliverables
  - `/core/skills/*/SKILL.md` (name/description only at boot; full load via `ReadFile`).
  - A catalog index loader with lazy `ReadFile` fetch.
- Tests (RED→GREEN)
  - RED: Unit tests verify only name/desc loaded at boot; full SKILL is loaded on demand.
  - GREEN: Lazy load works; catalog queries return expected items.

## Phase 5 — Sandbox Runner (`CodeExecute`)

- Deliverables
  - `/core/sandbox-runner` with a stubbed backend (e.g., E2B or local runner interface) honoring `net=off|on`, `timeout_ms`.
  - Embedded MCP client interface stub (no bulk tool exposure to LLM).
- Tests (RED→GREEN)
  - RED: Unit tests for timeout, net off, and artifact listing.
  - GREEN: Runner returns stdout/stderr/artifacts; policy enforced.
- Notes: Keep side effects in sandbox; inject only summaries/metrics externally.

## Phase 6 — MCP Gateway (Lazy Binding)

- Deliverables
  - `/core/mcp-gateway`: server indexing at boot; on first use, fetch tool metadata; enforce `allowed-tools` + `secretsScope`.
- Tests (RED→GREEN)
  - RED: Failing unit tests for allowlists and secrets scoping; no mass exposure of tools.
  - GREEN: Only allowed tools accessible; scope enforced.

## Phase 7 — TTC / Budget-Aware Reasoning

- Deliverables
  - `/core/cost/policies.yaml` + policy executor.
  - Hook into orchestrator for token/latency budget allocation.
- Tests (RED→GREEN)
  - RED: Unit tests for token allocation strategy and early-exit conditions.
  - GREEN: Policies applied; early-exit triggers when confidence > τ.

## Phase 8 — Verifier-First + MoA Hooks

- Deliverables
  - `/core/verifier`: PRM/rules/tests glue; optional critic loop.
  - Orchestrator gating: increase depth/samples only when uncertain.
- Tests (RED→GREEN)
  - RED: Unit tests for gating behavior and “uncertainty → deeper reasoning”.
  - GREEN: Verifier controls depth; metrics recorded.

## Phase 9 — Memory Backends (Context Curation)

- Deliverables
  - `/core/memory` adapters (stubs) for GraphRAG/HippoRAG and Zep.
  - Externalize artifacts/logs; prompt injection uses summaries/graphs.
- Tests (RED→GREEN)
  - RED: Unit tests for multi-hop retrieval and temporal ordering APIs.
  - GREEN: Deterministic retrieval for test fixtures.

## Phase 10 — Observability and Safety

- Deliverables
  - `/core/observability`: OpenTelemetry + OpenLLMetry instrumentation; span factories; safe attribute filters.
- Tests (RED→GREEN)
  - RED: Unit tests assert spans for prompts/tool calls/sandbox runs with tokens/cost/latency.
  - GREEN: Spans appear; secrets not leaked; sampling rules respected.

## Phase 11 — HIL Endpoints and Interrupt Semantics

- Deliverables
  - `/apps/api` implements `cancel`, `truncate`, `inject` mapped to orchestrator `interrupt()`.
- Tests (RED→GREEN)
  - RED: Mock E2E injects a mid-event; asserts pause/resume within ≤ 500 ms end-to-end.
  - GREEN: SLA met in mock; deterministic under CI.

## Phase 12 — Real LLM Client (OpenAI-Compatible)

- Deliverables
  - Toggle `LLM_CLIENT=openai` with runtime selection.
  - Minimal live-run script guarded by env flags.
- Tests (RED→GREEN)
  - RED: Skipped tests until `NET_EGRESS=on`.
  - GREEN: Sanity test passes against a configurable base (e.g., local proxy or cloud).

## Phase 13 — Adapters and Web Stream UI

- Deliverables
  - `/apps/web` SSE stream UI (progress/actions/final); minimal view for ACP events.
- Tests (RED→GREEN)
  - RED: E2E (mock) expects correct rendering for progress and final.
  - GREEN: UI consumes stream and renders deterministic fixtures.

## Phase 14 — Deployment Profiles

- Deliverables
  - Local-Solo: CLI runner + local API dev server.
  - Local-Multi: Docker Compose definitions; `api`, `orchestrator`, `sandbox`, `memory` services.
  - K8s-Multi: Deployments/Services; HPA for scale-out; secrets and egress policies.
- Tests (RED→GREEN)
  - RED: Smoke tests (health, stream connectivity) for each profile.
  - GREEN: Health and basic flows pass under each profile.

## Phase 15 — Evaluation Harnesses

- Deliverables
  - `/eval/are` and `/eval/swe-bench` wiring (skeletons, not heavy data).
- Tests (RED→GREEN)
  - RED: CI stubs ensure invocations succeed and artifacts are collected.
  - GREEN: Minimal fixtures run; results recorded.

## Gates and Hand-offs

- At the end of each phase: build success, full unit pass, mock E2E pass, and working VSCode debugging (breakpoints hit in both Python and Node test runners) are mandatory.
- If any gate fails, apply the Stop-the-Line policy (see CONSTITUTION.md).

## Estimated Sequence and Commit Cadence

- Expect 5–20 small commits per phase, each tied to a RED→GREEN transition or a focused refactor.
- Keep long-running branches rebased daily; prefer merging only when all gates are green.

