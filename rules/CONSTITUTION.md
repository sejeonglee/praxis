# Engineering Constitution

This document codifies the rules of development for this repository. It is binding for all contributors. The Constitution aligns with OBJECTIVE.md and enforces Spec Driven Development (SDD), strict TDD, and release discipline across Local-Solo, Local-Multi, and K8s-Multi deployment profiles.

## Fundamentals

- Spec Driven Development (SDD)
  - OBJECTIVE.md is normative. Ambiguities must be resolved by amending specs before implementation.
  - Contracts (schemas/types) govern boundaries; code must conform to contracts.
- Test-Driven Development (TDD)
  - RED → GREEN → REFACTOR, with an atomic commit at each RED→GREEN boundary.
  - No production code without failing tests first.

## Mandatory Test Gates

- Always run the full unit suite and the mocking E2E suite before pushing.
- Pipelines and local hooks must block merges on test failures.
- Both real and mock LLM clients must remain functional; default to mock in CI.

## Package Management and Tooling

- Python uses `uv` exclusively for environments and dependency resolution.
- Node/TypeScript uses `pnpm` for workspaces and scripts.
- Lockfiles are mandatory; changes must be reviewed.

## Commits and Branch Hygiene

- Prefer tiny, frequent commits. Each commit must:
  - Include only one conceptual change.
  - Transition a test from RED→GREEN or perform a focused refactor.
  - Keep the repository in a green state (all tests passing) except during an active RED commit.
- Conventional commit style is recommended: `feat:`, `fix:`, `test:`, `chore:`, `docs:`, `refactor:`.

## Clients and Mocks

- Implement and maintain both:
  - A real OpenAI-compatible LLM client.
  - A mock LLM client (deterministic) with equivalent interface.
- Switching is controlled by `LLM_CLIENT=mock|openai`. CI uses `mock`.
- Tests that need network egress must be opt-in via env flags and skipped otherwise.

## Observability and Telemetry

- Instrument prompts, tool calls, sandbox executions, and network calls with OpenTelemetry + OpenLLMetry.
- Spans must include tokens, cost, latency, model/tool names, budgets, and event IDs.
- Telemetry must never leak secrets. Apply attribute filters and sampling as needed.

## Security and Safety

- Secrets are scoped by `secretsScope` and never logged. Egress must be allowlisted when sandbox `net=on`.
- MCP servers and other external integrations must be version-pinned.
- Artifacts should be content-addressable where feasible.

## Deployment Profiles (Binding)

- Local-Solo: Single node, single process. Optimized for CLI, debugging, and evaluations.
- Local-Multi: Single node, multi process via Docker Compose. API-exposed, processes communicate over the compose network.
- K8s-Multi: Multi-node, multi process via K8s Pods. Communicate within cluster networking. Autoscaling is required for horizontal scale-out.

All profiles must satisfy the same contract and test gates. Profile-specific overrides must not change canonical behavior.

## Stop-the-Line Policy

- If either unit or mocking E2E tests fail on `main` or the release branch, all feature work halts until the build is green.
- Regression tests must be added for any bug fixed.

## Definition of Done (DoD)

- Build succeeds; full unit and mocking E2E tests pass.
- VSCode debugging works (breakpoints hit in both Python and Node test runners).
- Telemetry spans exist for prompts/tool calls/sandbox runs.
- HIL actions respond within the specified SLA (≤ 500 ms) in mock E2E.
- Changes align with OBJECTIVE.md and Deployment Profiles.

## Governance of Specs

- Changes to OBJECTIVE.md require a PR updating tests first (RED), then implementation (GREEN).
- Any deviation discovered in code vs. spec must result in either:
  - Fix the code to match the spec, or
  - Update the spec and tests, with explicit rationale.

