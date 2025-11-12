# Feature Specification: Workspace & Test Harness Bootstrap

**Feature Branch**: `001-workspace-test-harness`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "- Deliverables - PNPM workspace root (packages under `/apps/*` and `/sdk/*`). - Python project layout with `uv` (virtualenv, `pyproject.toml`). - Repo scripts: `scripts/test.unit.sh`, `scripts/test.e2e.mock.sh` (see TESTING.md). - Tests (RED→GREEN) - RED: Empty test skeletons for unit and mock E2E. - GREEN: Runners execute and report “0 passed” without failure; CI jobs wired. - Notes: No product logic; just infra and test harness."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Monorepo Workspace Skeleton (Priority: P1)

Repository maintainers need a single workspace root that automatically includes
packages under `/apps/*` and `/sdk/*` so new services or SDK modules can be
added without touching global config.

**Why this priority**: Without a workspace manifest aligned to OBJECTIVE.md’s
layout, no downstream development can install dependencies or share tooling.

**Independent Test**: On a clean clone, running the workspace bootstrap command
must complete without error and list placeholder packages for `/apps` and
`/sdk`.

**Acceptance Scenarios**:

1. **Given** a clean clone, **When** maintainers run the workspace install
   command, **Then** the command finishes without error and registers placeholder
   packages under `/apps/example` and `/sdk/example`.
2. **Given** a new module placed in `/sdk/new-module`, **When** the workspace
   manifest reloads, **Then** the module appears automatically with no manual
   edits to the root file.

---

### User Story 2 - Python Tooling Baseline (Priority: P2)

Infrastructure engineers need a reproducible Python environment managed by `uv`
so shared tooling (e.g., verifier, sandbox runner) can be developed without
guesswork about interpreter versions or dependencies.

**Why this priority**: OBJECTIVE.md calls for Python-based components; providing
the environment now unblocks future work and proves strict dependency control.

**Independent Test**: Running the documented `uv` command on a fresh machine
must create the virtual environment, lock dependencies, and allow the empty test
suite to execute without failure.

**Acceptance Scenarios**:

1. **Given** no existing `.venv`, **When** a contributor runs the bootstrap
   script, **Then** `pyproject.toml`, `uv.lock`, and a managed virtual
   environment appear with no manual editing.
2. **Given** the environment is active, **When** placeholder Python unit tests
   run, **Then** the runner reports “0 passed” without failing, showing the
   harness is GREEN-ready.

---

### User Story 3 - Continuous Validation Harness (Priority: P3)

Build engineers need repo-level scripts for unit and mocking E2E suites so the
RED→GREEN cycle is enforceable locally and in CI before product logic exists.

**Why this priority**: Without scripted runners and CI wiring, no one can
capture RED states or prove GREEN transitions, undermining the Constitution.

**Independent Test**: Invoking `scripts/test.unit.sh` or
`scripts/test.e2e.mock.sh` must exit non-zero while tests are missing (RED) and
zero after placeholders are added (GREEN), with CI reflecting both states.

**Acceptance Scenarios**:

1. **Given** empty test files, **When** CI executes the unit script, **Then** the
   job fails and surfaces the missing tests, proving RED enforcement.
2. **Given** placeholder tests that intentionally pass without assertions,
   **When** both scripts run locally and via CI, **Then** they exit successfully,
   emit telemetry markers, and display “0 passed” in logs.

---

### Edge Cases

- Workspace install must succeed even when `/apps` or `/sdk` folders contain no
  packages yet (fall back to placeholder packages).
- Test scripts must operate in offline mode with `LLM_CLIENT=mock` by default,
  ensuring deterministic runs when network egress is blocked.
- Bootstrap commands must detect unsupported Node.js or Python versions and
  exit gracefully without corrupting lockfiles.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A workspace manifest MUST automatically include `/apps/*` and
  `/sdk/*`, discovering additions/removals without hand-editing central config.
- **FR-002**: Placeholder packages MUST exist under `/apps/` and `/sdk/`
  (README + manifest) so tooling can validate structure even before product
  services ship.
- **FR-003**: A Python project managed purely by `uv` MUST exist at the root
  with `pyproject.toml`, `uv.lock`, and documented steps for creating the
  virtual environment on any machine.
- **FR-004**: Scripts `scripts/test.unit.sh` and `scripts/test.e2e.mock.sh` MUST
  orchestrate respective suites, respect `LLM_CLIENT=mock|openai`, and fail fast
  if prerequisites (workspace install, virtualenv) are missing.
- **FR-005**: CI jobs MUST call both scripts on every push/PR, fail the pipeline
  on any non-zero exit, and surface RED→GREEN transitions in logs.
- **FR-006**: Placeholder unit and mock E2E tests MUST begin as RED (missing or
  failing) and be promoted to GREEN once harness scripts run cleanly and display
  “0 passed”.

### Key Entities *(include if feature involves data)*

- **Workspace Package**: Represents each service/library under `/apps/*` or
  `/sdk/*`; defines name, version, and dependency boundaries for tooling.
- **Test Harness Script**: Canonical entry point (`test.unit`, `test.e2e.mock`)
  that prepares environments, selects LLM client mode, emits telemetry, and
  signals RED/GREEN state via exit codes.

### Constitutional Constraints *(MANDATORY)*

- **Spec Alignment**: Implements OBJECTIVE.md §1 (Repository Layout) by
  instantiating `/apps` + `/sdk` namespaces and §0 (Purpose & Scope) by enabling
  Spec Driven Development before feature logic appears; no amendments required.
- **Test Strategy**: First commit adds empty unit + mock E2E suites (RED). GREEN
  occurs once scripts execute end-to-end producing “0 passed” under both
  `LLM_CLIENT` modes. CI must default to `mock`.
- **Deployment Parity**: Workspace tooling and scripts MUST behave identically
  on Local-Solo (CLI), Local-Multi (Compose), and K8s-Multi environments, with
  autoscaling hooks defined for future replicas even if set to 1 initially.
- **Observability**: Each script invocation MUST emit OpenTelemetry/OpenLLMetry
  spans capturing latency, tokens (0), and cost placeholders so that pipelines
  show deterministic traces despite absent product logic.
- **Security & Tooling**: Dependency operations are limited to `pnpm` and `uv`;
  secrets respect `secretsScope`, egress stays off by default, and any MCP
  integrations referenced are version-pinned in lockfiles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New contributors complete the combined workspace + Python
  bootstrap in ≤10 minutes from clean clone, without editing config files.
- **SC-002**: Running both harness scripts in CI completes within 5 minutes and
  yields deterministic GREEN results after the initial RED commit.
- **SC-003**: Adding a new `/apps/*` or `/sdk/*` package requires zero changes
  outside that package directory 100% of the time.
- **SC-004**: CI captures telemetry spans for every unit and mock E2E run with
  100% sample rate, proving observability coverage for the harness itself.

## Assumptions

- Contributors have Node.js 24+ and Python 3.11+ installed; bootstrap scripts
  only validate versions, not install runtimes.
- No production workloads are shipped in this feature—only scaffolding and test
  harness assets.
- Existing CI infrastructure (e.g., GitHub Actions) is available to run the new
  scripts without procurement or billing changes.
