# Praxis Monorepo

This repository hosts the Praxis agent platform. The initial scope of this branch bootstrap focuses on delivering the shared workspace, Python harness, and continuous validation scripts defined in `specs/001-workspace-test-harness`.

## Workspace & Harness Bootstrap

Follow the detailed instructions in [`specs/001-workspace-test-harness/quickstart.md`](specs/001-workspace-test-harness/quickstart.md) to:

1. Install prerequisites (Node.js 20 + pnpm 9, Python 3.14 + `uv`).
2. Run `pnpm install` to register packages under `/apps/*` and `/sdk/*`.
3. Create the Python environment with `uv sync -p python/harness`.
4. Execute the validation scripts:
   - `scripts/test.unit.sh` (workspace + unit harness)
   - `scripts/test.e2e.mock.sh` (mocking E2E flows, defaulting to `LLM_CLIENT=mock`)

These steps keep the repository in compliance with the Engineering Constitution—tests are mandatory, telemetry spans are emitted for each harness run, and no product logic ships until the infrastructure is green.
