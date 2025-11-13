# Workspace & Test Harness Bootstrap (001)

## Summary
- Implemented the pnpm workspace skeleton with example app + SDK packages, shared TS base config, and repo-wide scripts for unit/E2E harnesses.
- Added the uv-managed Python harness with deterministic mock LLM scenarios (tool-feedback flow + concurrent sessions) plus unit/e2e tests and telemetry helpers.
- Wired CI to run both scripts, upload telemetry artifacts, and documented the bootstrap/quickstart process across spec, plan, data-model, contracts, research, tasks, and checklists.

## Testing
- `./scripts/test.unit.sh`
- `./scripts/test.e2e.mock.sh`
