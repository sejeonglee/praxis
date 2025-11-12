# Quickstart: Workspace & Test Harness Bootstrap

## 1. Prerequisites
- Node.js 24+, pnpm ^10.13.1
- Python 3.11 + `uv` CLI (^0.7.22)
- GitHub CLI/login optional for CI checks
- `LLM_CLIENT` defaults to `mock` (no secrets required)

## 2. Install Dependencies
```bash
pnpm install            # auto-discovers /apps/* and /sdk/*
uv sync --project python/harness
```

## 3. Run RED Suites
```bash
scripts/test.unit.sh     # fails until placeholder vitest suite exists
scripts/test.e2e.mock.sh # fails until pytest scaffolding added
```

## 4. GREEN Paths
1. Add placeholder `vitest` spec under `sdk/example-sdk/__tests__/`.
2. Add `pytest` files:
   - `test_tool_feedback_flow.py` (user-feedback + multi-tool, modeled after `../msa-ma-prototype/demo.py`)
   - `test_concurrent_sessions.py` (async session isolation, modeled after `../msa-ma-prototype/demo_two_sessions.py`)
3. Re-run both scripts; expect `0 passed` and telemetry span logs.

## 5. CI Expectations
- `.github/workflows/ci.yml` calls both scripts on push/PR.
- Pipelines fail fast on non-zero exit codes.
- Logs include RED→GREEN evidence and span IDs.

## 6. Switching LLM Client (optional)
```bash
LLM_CLIENT=openai OPENAI_API_KEY=... scripts/test.e2e.mock.sh
```
- Requires egress + credentials; otherwise stay in mock mode.

## 7. Troubleshooting
- Missing packages? Ensure `pnpm-workspace.yaml` globs `/apps/*` and `/sdk/*`.
- Python mismatch? Run `uv python pin 3.11`.
- Telemetry absent? Check `OTEL_EXPORTER_OTLP_ENDPOINT` env and confirm scripts not filtered by sampling.
