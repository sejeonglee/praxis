# Implementation Plan: Workspace & Test Harness Bootstrap

**Branch**: `001-workspace-test-harness` | **Date**: 2025-11-10 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-workspace-test-harness/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Stand up the infrastructure mandated by OBJECTIVE.md: a pnpm workspace that auto
discovers `/apps/*` and `/sdk/*`, a root Python project managed via `uv`, and
repo-level unit + mocking E2E runners. The mock E2E harness must include two
canonical scenarios: (1) tool-intensive, user-feedback flows similar to
`../msa-ma-prototype/demo.py`, and (2) async session isolation modeled after
`../msa-ma-prototype/demo_two_sessions.py`. RED commits introduce empty suites;
GREEN commits make both scripts exit cleanly (reporting “0 passed”) while
emitting telemetry and wiring CI. No product logic deploys in this feature.

## Technical Context

**Language/Version**: Node.js 24 + TypeScript workspace, Python 3.11 via `uv`
**Primary Dependencies**: `pnpm`, `typescript`, `vitest`, `eslint`, `pytest`,
`anyio`, `opentelemetry-sdk`, `uv`  
**Storage**: N/A (no databases; file system artifacts only)  
**Testing**: `vitest` for TypeScript unit placeholders, `pytest` + `anyio` for
mock E2E & concurrency cases, shell wrappers under `scripts/`  
**Target Platform**: Developer laptops (macOS/Linux) and GitHub Actions Ubuntu runners; must behave identically in Local-Solo CLI, Local-Multi (Compose), and K8s-Multi jobs  
**Project Type**: Multi-language monorepo with `/apps`, `/sdk`, `/python/harness`, shared scripts  
**Performance Goals**: Workspace + Python bootstrap ≤10 minutes on a clean clone; combined unit + mock E2E runtime ≤5 minutes in CI  
**Constraints**: Offline-first (`LLM_CLIENT=mock` default, no external egress),
autoscaling hooks pre-declared for future K8s jobs, telemetry spans on every
script run, secrets filtered from logs/spans  
**Scale/Scope**: Initial placeholder packages (1 in `/apps`, 1 in `/sdk`) +
Python harness; design must scale to dozens of packages without editing root
config

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Spec Alignment**: OBJECTIVE.md §1 (Repository Layout) + §0 (Purpose & Scope)
  fully cover this work; no ambiguities remain so no pre-implementation amendments.
- **RED→GREEN Plan**: RED commits add empty `vitest` suite and `pytest` suites
  (tool-feedback + concurrency). GREEN once `scripts/test.unit.sh` and
  `scripts/test.e2e.mock.sh` exit 0 and print “0 passed”, with CI wiring proven.
- **LLM Clients**: Harness accepts `LLM_CLIENT=mock|openai`. CI sets `mock`
  (deterministic). Docs explain how to run `openai` locally when creds exist.
- **Deployment Profiles**: Scripts run identically via CLI, Docker Compose jobs,
  and K8s Jobs; Compose/K8s manifests include autoscaling stubs though replicas
  default to 1.
- **Observability**: Both scripts emit OpenTelemetry/OpenLLMetry spans per run
  (tokens=0, cost=0, latency, tool/model IDs, event IDs). Attribute filters keep
  secrets out; spans stored even when suites are empty.
- **Security & Tooling**: Dependency installs limited to `pnpm` + `uv`. Lockfiles
  reviewed in PRs. MCP integrations (if any) pinned. Egress stays disabled unless
  developers opt in via documented env flag.

## Project Structure

### Documentation (this feature)

```text
specs/001-workspace-test-harness/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── harness.openapi.yaml
└── tasks.md              # produced later by /speckit.tasks
```

### Source Code (repository root)

```text
apps/
└── example-app/
    ├── package.json
    └── src/index.ts

sdk/
└── example-sdk/
    ├── package.json
    ├── src/index.ts
    └── __tests__/example.spec.ts

python/
└── harness/
    ├── pyproject.toml
    ├── uv.lock
    └── tests/
        ├── unit/
        └── e2e/
            ├── test_tool_feedback_flow.py
            └── test_concurrent_sessions.py

scripts/
├── test.unit.sh
└── test.e2e.mock.sh

.github/workflows/
└── ci.yml
```

**Structure Decision**: The monorepo keeps language domains separated: `/apps`
and `/sdk` house Node/TypeScript packages discovered by pnpm; Python tooling
lives in `/python/harness`. Tests stay near their ecosystems (TypeScript unit
tests under `sdk`, Python mock E2E under `python/harness`). Scripts and CI live
at the root for consistent entry points across deployment profiles.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| _None_ | | |
