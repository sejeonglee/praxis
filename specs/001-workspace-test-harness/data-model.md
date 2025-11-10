# Data Model: Workspace & Test Harness Bootstrap

## Entity: WorkspacePackage
- **Purpose**: Represents every Node/TypeScript project auto-discovered under `/apps/*` or `/sdk/*`.
- **Fields**:
  - `name` (string, required, unique within workspace)
  - `location` (path, required)
  - `type` (enum: `app` | `sdk`)
  - `version` (semver string, required)
  - `entryPoints` (array of file paths)
- **Relationships**:
  - Belongs to the pnpm workspace manifest.
  - Provides sources/fixtures consumed by `TestHarnessScript`.
- **Validation Rules**:
  - Names must be kebab-case.
  - `type` inferred from path prefix.

## Entity: PythonEnvironment
- **Purpose**: Encapsulates the `uv`-managed virtual environment for harness tooling.
- **Fields**:
  - `pyproject` (toml document path)
  - `uvLock` (lockfile path)
  - `pythonVersion` (string, default `3.11`)
  - `scripts` (list of CLI entry points exposed via `uv tool run`)
- **Relationships**:
  - Supplies dependencies for E2E tests & telemetry emitters.
  - Invoked by `TestHarnessScript` when running `pytest`.
- **Validation Rules**:
  - `pythonVersion` must match `.python-version` (if present).
  - Lockfile checksum recorded in CI logs.

## Entity: TestHarnessScript
- **Purpose**: Shell entry points (`scripts/test.unit.sh`, `scripts/test.e2e.mock.sh`) that orchestrate suites and emit telemetry.
- **Fields**:
  - `name` (enum `unit` | `e2e_mock`)
  - `command` (string)
  - `llmClientMode` (env: `mock` default, `openai` optional)
  - `telemetrySpanName` (string)
- **Relationships**:
  - Executes `WorkspacePackage` tests (unit) or `PythonEnvironment` suites (E2E).
  - Emits `TelemetrySpan` records consumed by observability pipeline.
- **Validation Rules**:
  - Non-zero exit code must halt CI.
  - Scripts verify prerequisites (pnpm install, uv env) before running suites.

## Entity: MockScenario
- **Purpose**: Describes each deterministic E2E test narrative.
- **Fields**:
  - `id` (string, e.g., `tool_feedback_flow`, `concurrent_sessions`)
  - `description` (text)
  - `sourcePrototype` (path to reference demo)
  - `expectedLLMActions` (ordered list: `think`, `tool_call`, `user_feedback`, etc.)
  - `sessionIsolation` (boolean, true for concurrency scenario)
- **Relationships**:
  - Executed within `pytest` e2e suite.
  - Consumes `LLMClientConfig`.

## Entity: LLMClientConfig
- **Purpose**: Captures configuration for mock vs real client selection.
- **Fields**:
  - `mode` (enum `mock` `openai`)
  - `apiKeyRef` (optional secret reference for real client)
  - `mockFixtures` (path to deterministic responses)
- **Relationships**:
  - Read by `TestHarnessScript` before running suites.
  - Referenced by `MockScenario` steps.
- **Validation Rules**:
  - `mockFixtures` required when `mode=mock`.
  - Real mode only allowed when `apiKeyRef` present and egress allowed.

## Entity: TelemetrySpan
- **Purpose**: Represents per-suite observability data emitted by harness scripts.
- **Fields**:
  - `spanId`, `traceId`
  - `name` (string, e.g., `unit-suite-run`)
  - `attributes` (map: tokens, cost, latency_ms, llm_client, scenario_id)
  - `status` (enum `OK`, `ERROR`)
- **Relationships**:
  - Produced by `TestHarnessScript`.
  - Stored in observability pipeline for audits.
- **Validation Rules**:
  - `tokens` and `cost` default to 0 for mock runs.
  - Secrets filtered before emit.
