---

description: "Task list for Workspace & Test Harness Bootstrap feature"
---

# Tasks: Workspace & Test Harness Bootstrap

**Input**: Design documents from `/specs/001-workspace-test-harness/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per the constitution. Every story starts with the
failing unit + mocking E2E tasks before any implementation work.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish repository skeleton, tooling metadata, and documentation anchors required before implementing story-specific work.

- [ ] T001 Create base directories (`apps/`, `sdk/`, `python/harness/`, `scripts/`, `.github/workflows/`) with `.gitkeep` files and update `.gitignore` to cover Node/Python artifacts.
- [ ] T002 Record engine requirements by adding `.node-version` (20.x) and `.python-version` (3.11.x) at repo root.
- [ ] T003 Add a “Workspace & Harness Bootstrap” section to `README.md` summarizing prerequisites and pointing to `specs/001-workspace-test-harness/quickstart.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Global configuration needed before any story-specific work (workspace manifest, shared configs, CI scaffold).

- [ ] T004 Create `pnpm-workspace.yaml` globs for `/apps/*` and `/sdk/*`, plus future nested packages.
- [ ] T005 Add root `package.json` with `scripts` (`bootstrap`, `lint`, `test:unit`) that defer to pnpm workspace commands.
- [ ] T006 Create `tsconfig.base.json` consumed by `apps/example-app` and `sdk/example-sdk`.
- [ ] T007 Add `.npmrc` enforcing pnpm, `lockfile=true`, and workspace hoist settings.
- [ ] T008 Scaffold `.github/workflows/ci.yml` invoking `scripts/test.unit.sh` and `scripts/test.e2e.mock.sh` placeholders (jobs marked TODO).

---

## Phase 3: User Story 1 - Monorepo Workspace Skeleton (Priority: P1) 🎯 MVP

**Goal**: Auto-discover `/apps/*` and `/sdk/*` packages via pnpm workspace so maintainers can add modules without editing global config.

**Independent Test**: On a clean clone, run `pnpm install` followed by `pnpm ls --depth 0` and confirm example packages appear; dropping a new folder under `/sdk/` should register automatically.

### Tests for User Story 1 (MANDATORY — write first, must fail) ⚠️

- [ ] T009 [P] [US1] Add failing Vitest spec `sdk/example-sdk/__tests__/workspace.discovery.spec.ts` that asserts `/apps/example-app` and `/sdk/example-sdk` appear in `pnpm ls`.
- [ ] T010 [P] [US1] Add failing Vitest spec `sdk/example-sdk/__tests__/workspace.auto_register.spec.ts` simulating creation of `/sdk/new-module` and expecting workspace config to pick it up automatically.

### Implementation for User Story 1

- [ ] T011 [US1] Scaffold `apps/example-app` (package.json, README.md, src/index.ts) as the canonical workspace app example.
- [ ] T012 [US1] Scaffold `sdk/example-sdk` (package.json, README.md, src/index.ts, __tests__/README.md) as the canonical SDK example.
- [ ] T013 [US1] Create `docs/workspace.md` documenting how to add/remove packages plus troubleshooting for missing discoveries.
- [ ] T014 [US1] Add `scripts/bootstrap.workspace.sh` that runs `pnpm install`, `pnpm ls`, and emits helpful errors when packages fail to register; reference it in `README.md`.

**Checkpoint**: At this point, workspace install should succeed and the Vitest specs can be flipped to GREEN.

---

## Phase 4: User Story 2 - Python Tooling Baseline (Priority: P2)

**Goal**: Provide a reproducible Python environment managed via `uv`, including placeholder tests that run cleanly once the environment is bootstrapped.

**Independent Test**: From a clean machine, run `uv sync -p python/harness` and `uv run pytest python/harness/tests/unit`; expect environment creation plus a passing “0 tests” or placeholder output.

### Tests for User Story 2 (MANDATORY — write first, must fail) ⚠️

- [ ] T015 [P] [US2] Add failing pytest `python/harness/tests/unit/test_env_bootstrap.py` asserting `pyproject.toml` + `uv.lock` exist and `uv python --version` matches 3.11.
- [ ] T016 [P] [US2] Add failing pytest `python/harness/tests/unit/test_dependency_manifest.py` verifying required packages (`pytest`, `anyio`, `opentelemetry-sdk`) are present in the lockfile.

### Implementation for User Story 2

- [ ] T017 [US2] Create `python/harness/pyproject.toml` defining dependencies (`pytest`, `anyio`, `opentelemetry-sdk`, `rich`) and `tool.uv` metadata.
- [ ] T018 [US2] Generate and commit `python/harness/uv.lock` by running `uv sync`, ensuring deterministic hashes.
- [ ] T019 [US2] Add `python/harness/tests/unit/conftest.py` plus placeholder tests that import harness modules and return GREEN once environment exists.
- [ ] T020 [US2] Update `specs/001-workspace-test-harness/quickstart.md` and `README.md` with exact `uv` commands (`uv sync -p python/harness`, `uv run pytest ...`).

**Checkpoint**: Python environment ready; unit tests can be converted to GREEN with “0 passed” output.

---

## Phase 5: User Story 3 - Continuous Validation Harness (Priority: P3)

**Goal**: Deliver repo-level scripts for unit + mocking E2E suites, leveraging mock LLM flows from the prototype demos and ensuring telemetry + CI wiring enforce RED→GREEN.

**Independent Test**: Run `scripts/test.unit.sh` and `scripts/test.e2e.mock.sh` locally (mock client) and in CI; expect telemetry spans, deterministic exit codes, and scenario logs referencing `demo.py` + `demo_two_sessions.py`.

### Tests for User Story 3 (MANDATORY — write first, must fail) ⚠️

- [ ] T021 [P] [US3] Add failing pytest `python/harness/tests/e2e/test_tool_feedback_flow.py` replicating `../msa-ma-prototype/demo.py` (user feedback + multiple tool calls).
- [ ] T022 [P] [US3] Add failing pytest `python/harness/tests/e2e/test_concurrent_sessions.py` modeled after `../msa-ma-prototype/demo_two_sessions.py` to prove async session isolation.
- [ ] T023 [P] [US3] Add failing pytest `python/harness/tests/e2e/test_telemetry_spans.py` asserting harness emits OpenTelemetry/OpenLLMetry spans (tokens=0, cost=0, scenario IDs).

### Implementation for User Story 3

- [ ] T024 [US3] Implement `scripts/test.unit.sh` to run `pnpm vitest --run`, enforce `LLM_CLIENT=${LLM_CLIENT:-mock}`, and emit telemetry spans via `otel-cli` or Python helper.
- [ ] T025 [US3] Implement `scripts/test.e2e.mock.sh` to source `uv` environment, run `pytest python/harness/tests/e2e`, set `LLM_CLIENT=mock`, and stream scenario logs.
- [ ] T026 [US3] Add `python/harness/tests/e2e/fixtures/mock_llm.py` reusing responses from `demo.py` and injecting deterministic budgets + user feedback prompts.
- [ ] T027 [US3] Add concurrency utilities `python/harness/tests/e2e/utils/session_bus.py` ensuring async session isolation with `anyio`.
- [ ] T028 [US3] Update `.github/workflows/ci.yml` to cache pnpm modules + uv wheels, run both scripts, and upload telemetry artifacts (span JSON).
- [ ] T029 [US3] Expand `quickstart.md` and `README.md` with detailed instructions for running harness scripts, switching `LLM_CLIENT`, and interpreting CI telemetry links.

**Checkpoint**: Both scripts exit GREEN locally/CI, telemetry captured, and demo-derived scenarios pass with mock LLM.

---

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T030 [P] Refresh `docs/workspace.md` & `quickstart.md` with screenshots of passing RED→GREEN runs and troubleshooting tips (Node version, uv cache).
- [ ] T031 Run `scripts/test.unit.sh` and `scripts/test.e2e.mock.sh` on a clean container image to validate ≤10 minute bootstrap, update logs in `docs/workspace.md`.
- [ ] T032 Finalize observability configuration by documenting OTLP endpoint/env vars in `README.md` and verifying secrets filters.

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2**: Directory skeleton and metadata must exist before configuring pnpm/CI.
- **Phase 2 → Phase 3**: Workspace manifest + root configs block User Story 1 tests.
- **User Stories**: Execute sequentially by priority (US1 → US2 → US3) to keep RED→GREEN traceable.
- **CI wiring** (T028) depends on scripts from T024–T025.

### User Story Dependencies

- **US1**: Depends on Phase 2 completion; no other story prerequisites.
- **US2**: Depends on Phase 2 and `apps/sdks` folders (from US1 Setup) only for shared docs.
- **US3**: Depends on US1 (unit suites exist) and US2 (python harness available).

### Parallel Opportunities

- Tests within each story (e.g., T009/T010 or T021–T023) are parallelizable once prerequisite directories exist.
- Implementation tasks T011–T012 can proceed in parallel (different folders).
- In US3, T024–T027 touch scripts vs Python fixtures, so separate contributors can split work.

---

## Implementation Strategy

1. Finish Phase 1–2 to keep repo installable.
2. Deliver **MVP** by completing User Story 1 (workspace skeleton + passing Vitest).
3. Layer in Python tooling (US2) to unblock future verifier/sandbox work.
4. Conclude with harness scripts + CI telemetry (US3), then polish documentation.
