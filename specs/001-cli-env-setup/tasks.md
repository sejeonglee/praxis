# Tasks: CLI Event-Driven Environment Setup

**Input**: Design documents from `/specs/001-cli-env-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python/uv project, directory layout, and local dependencies so later phases have a stable workspace.

- [X] T001 Scaffold `apps/cli` directory tree (src/, tests/, scripts/, mocks/, api/) per plan.md
- [X] T002 Initialize uv project (`apps/cli/pyproject.toml`, `uv.lock`) with Python 3.11 settings
- [X] T003 Add core dependencies (Typer, Litestar, redis-py, Pydantic, structlog, OpenTelemetry, pytest) to `apps/cli/pyproject.toml`
- [X] T004 Provision local Redis via `infra/local/redis/docker-compose.yml` with Streams defaults
- [X] T005 Add repo-level `.env.example` documenting required CLI variables in `/home/sejeonglee/workspaces/praxis/.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core modules shared by all stories—event contracts, configuration, queue utilities, telemetry, and Litestar skeleton.

- [X] T006 Define Pydantic event contracts in `apps/cli/src/praxis_cli/events.py` (SessionInstruction, EventEnvelope, MidEvent)
- [X] T007 Implement configuration loader + validation in `apps/cli/src/praxis_cli/config.py`
- [X] T008 Build Redis Streams publisher/subscriber utilities with at-least-once dedupe in `apps/cli/src/praxis_cli/queue.py`
- [X] T009 Implement structured logging + OpenTelemetry helpers in `apps/cli/src/praxis_cli/telemetry.py`
- [X] T010 Create Litestar application skeleton with health route in `apps/cli/src/praxis_cli/api/app.py`
- [X] T011 Stub deterministic mock components (`mocks/llm.py`, `mocks/database.py`, `mocks/orchestrator.py`) with seeded responses

**Checkpoint**: Shared infrastructure ready—user stories can proceed independently.

---

## Phase 3: User Story 1 – Run CLI-driven session locally (Priority: P1) 🎯 MVP

**Goal**: Operators can run the CLI, publish a `SessionInstruction`, stream progress, and view the final answer entirely locally.
**Independent Test**: `uv run praxis-cli run --instruction-file samples/reference_instruction.yaml` publishes/receives events and exits successfully using mocked responders.

### Tests for User Story 1

- [X] T012 [P] [US1] Author CLI argument + config unit tests in `apps/cli/tests/unit/test_cli_args.py`
- [X] T013 [P] [US1] Add integration test validating queue round-trip in `apps/cli/tests/integration/test_cli_to_mocks_roundtrip.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement Typer command entrypoint (`apps/cli/src/praxis_cli/cli.py`) invoking queue + telemetry modules
- [X] T015 [P] [US1] Wire SessionInstruction builder + validation in `apps/cli/src/praxis_cli/cli.py`
- [X] T016 [US1] Implement subscriber loop for progress/final events in `apps/cli/src/praxis_cli/cli.py`
- [X] T017 [US1] Emit structured progress logs + summaries in `apps/cli/src/praxis_cli/telemetry.py`
- [X] T018 [US1] Document manual CLI run steps in `apps/cli/README.md`

**Checkpoint**: CLI can drive a full session locally; tests cover args + round-trip flow.

---

## Phase 4: User Story 2 – Scripted end-to-end verification (Priority: P2)

**Goal**: QA can run an automated script that launches mocks, the CLI, and validates the documented event sequence with a single command.
**Independent Test**: `uv run python -m praxis_cli.scripts.e2e_scenario --scenario reference` produces a PASS report after verifying ordered events via Litestar endpoints.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add e2e regression test harness in `apps/cli/tests/e2e/test_reference_scenario.py`
- [ ] T020 [P] [US2] Create control-plane contract tests in `apps/cli/tests/integration/test_control_plane_api.py`

### Implementation for User Story 2

- [ ] T021 [US2] Implement Litestar session + scenario endpoints in `apps/cli/src/praxis_cli/api/app.py`
- [ ] T022 [P] [US2] Flesh out deterministic mock LLM + DB behaviors (`apps/cli/src/praxis_cli/mocks/llm.py`, `mocks/database.py`)
- [ ] T023 [US2] Implement orchestrator loop publishing staged events in `apps/cli/src/praxis_cli/mocks/orchestrator.py`
- [ ] T024 [US2] Build `apps/cli/src/praxis_cli/scripts/e2e_scenario.py` coordinating Redis, CLI, and Litestar endpoints
- [ ] T025 [US2] Update `specs/001-cli-env-setup/quickstart.md` with e2e script instructions + sample report

**Checkpoint**: Automated scenario passes consistently and produces machine-readable reports.

---

## Phase 5: User Story 3 – Debugging & unit-test ergonomics (Priority: P3)

**Goal**: Developers can attach VS Code debug sessions quickly and extend pytest coverage for error paths.
**Independent Test**: Running the VS Code launch profiles hits breakpoints before queue replies, and pytest suite reports >80% statement coverage with new failure-case tests.

### Tests for User Story 3

- [ ] T026 [P] [US3] Expand failure-path tests in `apps/cli/tests/unit/test_queue_error_paths.py`

### Implementation for User Story 3

- [ ] T027 [US3] Create `.vscode/launch.json` with CLI, Litestar API, and e2e script targets
- [ ] T028 [P] [US3] Emit OpenTelemetry spans for mock + CLI events in `apps/cli/src/praxis_cli/telemetry.py`
- [ ] T029 [US3] Add debugging + coverage guidance to `specs/001-cli-env-setup/quickstart.md`

**Checkpoint**: Debug sessions load in <30s, and developers have clear guidance/tests for diagnosing failures.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, docs, and hardening after all user stories are functional.

- [ ] T030 Run end-to-end quickstart validation and capture artifacts in `apps/cli/.reports/validation/latest`
- [ ] T031 Update repository-level documentation (`OBJECTIVE.md` cross-links, `AGENTS.md`, `apps/cli/README.md`) with final instructions

---

## Dependencies & Execution Order

1. Phase 1 → Phase 2 → (Phase 3 | Phase 4 | Phase 5 in priority order, but can run in parallel once Phase 2 completes) → Phase 6.
2. User Story dependencies:
   - US1 (P1) depends on foundational modules only.
   - US2 (P2) depends on US1 queue/contracts for reuse but can start once Phase 2 ensures mocks skeleton; recommended order US1 → US2 for stability.
   - US3 (P3) depends on US1 functionality (for debugger attach tests) but not on US2.
3. Tests within each story should be authored before implementation tasks in the same story.

## Parallel Execution Examples

- **US1**: Develop CLI argument tests (T012) and progress subscriber implementation (T016) in parallel because they target different files; queue round-trip test (T013) can run concurrently once Redis helpers (T008) exist.
- **US2**: Contract tests (T020) can run while deterministic mocks (T022) are built, and the orchestrator (T023) can proceed in parallel with the e2e script (T024) once Litestar endpoints (T021) exist.
- **US3**: VS Code launch config (T027) and telemetry span work (T028) touch different files and can run simultaneously after foundational telemetry (T009) is in place.

## Implementation Strategy

1. **MVP (US1)**: Finish Phases 1-3 so operators can run the CLI end-to-end manually. Validate manually + with US1 tests.
2. **Incremental Additions**: Layer US2 automated scripts/tests next, providing regression safety. Then tackle US3 developer-experience upgrades.
3. **Parallelization**: After Phase 2, separate owners can pursue US1/US2/US3 provided they respect shared module dependencies outlined above.
4. **Definition of Done**: Each user story must meet its independent test plus pass pytest/e2e suites before merging; Phase 6 ensures documentation and validation remain current.
