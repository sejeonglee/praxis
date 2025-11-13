# Research: Workspace & Test Harness Bootstrap

## Decision 1: pnpm workspace auto-discovers `/apps/*` and `/sdk/*`
- **Rationale**: Matches OBJECTIVE.md layout, keeps future services/SDK modules zero-config, and lets tooling share node_modules without manual manifest edits.
- **Alternatives considered**:
  - **Single root package**: rejected because every new service would require manual wiring and defeat isolation.
  - **Yarn workspaces**: rejected to stay aligned with Constitution (pnpm-only).

## Decision 2: Placeholder packages mirror future real services
- **Rationale**: Shipping `apps/example-app` and `sdk/example-sdk` with README + manifest exercises workspace discovery, ensures `pnpm install` succeeds even before real services exist, and gives `vitest` a location for RED tests.
- **Alternatives considered**:
  - **Empty globs with no packages**: rejected because pnpm throws when no packages match and developers lack references for structure.

## Decision 3: Python tooling lives in `/python/harness` managed by `uv`
- **Rationale**: Keeps Python dependencies isolated, satisfies Constitution’s `uv` requirement, and provides a predictable virtualenv for future sandbox/verifier services.
- **Alternatives considered**:
  - **Using `pip` + `virtualenv`**: rejected (violates Constitution).
  - **Embedding scripts under `/sdk`**: rejected to avoid cross-language coupling.

## Decision 4: Mock E2E scenarios reference existing prototypes
- **Rationale**: Reusing flows from `../msa-ma-prototype/demo.py` (user feedback + multi-tool) and `demo_two_sessions.py` (async session isolation) accelerates authoring realistic tests while staying deterministic under the mock LLM.
- **Alternatives considered**:
  - **Invent new toy scenarios**: rejected because they would not exercise required behaviors (feedback loops, concurrency) and would increase rework later.

## Decision 5: Telemetry + CI wiring prioritized in harness scripts
- **Rationale**: Scripts will emit OpenTelemetry/OpenLLMetry spans even when tests report “0 passed,” giving observability coverage from day one and satisfying stop-the-line policy with deterministic GitHub Actions jobs.
- **Alternatives considered**:
  - **Add telemetry later**: rejected because Constitution demands telemetry as part of Definition of Done and pipelines must prove readiness immediately.

## Decision 6: `LLM_CLIENT=mock` default with opt-in real client
- **Rationale**: Keeps CI deterministic/offline while still allowing devs to flip to `openai` for exploratory runs once credentials exist.
- **Alternatives considered**:
  - **Always real client**: rejected due to cost, nondeterminism, and Constitution’s requirement for mock default.
  - **Mock only (no toggle)**: rejected because future features must validate against the real interface locally before shipping.
