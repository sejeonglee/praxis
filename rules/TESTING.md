# Testing Strategy and How-To

This document describes how we test the system while following Spec Driven Development (SDD) and strict TDD. It defines the two canonical test entrypoints you will run on every change: full unit tests and mocking end-to-end (E2E) tests. It also standardizes tooling with `uv` (Python) and `pnpm` (TypeScript/Node), switching between a real OpenAI-compatible LLM client and a mock client.

## Test Types

- Unit tests
  - Scope: Schema validation, pure functions, adapters, orchestration state transitions, simple policy logic, serialization (CloudEvents), and basic IO boundaries under mocks.
  - Tools: `pytest` (+`pytest-asyncio`) for Python; `vitest` for TypeScript/Node.
- Mocking E2E tests
  - Scope: Agent-Client Protocol (ACP) flow under mocked services. Validates SSE/WS streaming of CloudEvents, non-blocking HIL (`cancel`/`truncate`/`inject`), and observation/action envelopes. No real egress; runs against a mock API + mock orchestrator + mock LLM client.
  - Tools: `vitest` or `jest` client + lightweight mock server (Node) or `pytest` with `anyio` and `httpx` for SSE.

## Rules (Always On)

- Run both test suites on every step (commit or pre-commit): unit and mocking E2E.
- The unit suite must include all subpackages; do not subset.
- TDD: write failing test (RED), implement minimal change, make it pass (GREEN), refactor. Commit each RED→GREEN transition.
- Tests must be deterministic: no network access unless explicitly enabled via env flags.
- Both real and mock LLM clients must be supported. Default to mock in CI.

## Tooling and Package Managers

- Python: `uv` for environment and dependency management.
- Node/TypeScript: `pnpm` for workspaces and scripts.

### Python setup (uv)

```bash
# From repo root
uv venv
uv pip install -U pip
uv pip install -e .[dev]

# Run unit tests with coverage
uv run -m pytest -q --maxfail=1 --disable-warnings --cov --cov-report=term-missing
```

Expect a `pyproject.toml` with `pytest`, `pytest-asyncio`, `pydantic` or `jsonschema` dev deps, and `opentelemetry-*` where relevant. Unit tests live under `*/tests`.

### Node/TypeScript setup (pnpm)

```bash
pnpm -v
pnpm install

# Run unit tests (all packages)
pnpm -w test

# Run mocking E2E tests
pnpm -w test:e2e:mock
```

Expect a PNPM workspace rooted at the repo with per-package test scripts. Use `vitest` for speed and TS-first DX.

## Standard Environment Variables

- `LLM_CLIENT`: `mock` (default) or `openai` (OpenAI-compatible API).
- `OPENAI_API_BASE`: base URL for OpenAI-compatible servers (only when `LLM_CLIENT=openai`).
- `OPENAI_API_KEY`: required when `LLM_CLIENT=openai`.
- `DEPLOY_PROFILE`: `local-solo` | `local-multi` | `k8s-multi`.
- `LOG_LEVEL`: `debug|info|warn|error`.
- `NET_EGRESS`: `off|on` for sandbox/network tests.

CI defaults: `LLM_CLIENT=mock`, `NET_EGRESS=off`.

## Canonical Test Entry Scripts

While these scripts may live under `scripts/`, their content is shown here for clarity. They must run at the repo root and exercise all packages.

### Unit tests (scripts/test.unit.sh)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Python
uv run -m pytest -q --maxfail=1 --disable-warnings

# Node/TypeScript
pnpm -w test
```

### Mocking E2E (scripts/test.e2e.mock.sh)

```bash
#!/usr/bin/env bash
set -euo pipefail

export LLM_CLIENT=mock
export NET_EGRESS=off

# Option A: Node mock server + vitest client
pnpm -w --filter @apps/api run start:mock &
SERVER_PID=$!
trap 'kill ${SERVER_PID} || true' EXIT
sleep 1
pnpm -w test:e2e:mock

# Option B (alternative): pytest e2e under mock
# uv run -m pytest -q tests_e2e_mock
```

## Mock E2E Requirements

- Transport: CloudEvents JSON over SSE (preferred for web) or WS.
- Event types under test:
  - `agent.progress.created|updated`
  - `agent.action.proposed`
  - `agent.observation.appended`
  - `agent.event.received` (inbound mid_events)
  - `agent.final.ready`
- Ordering: progress → actions/observations (interleaved) → final_answer. HIL actions must interrupt within ≤ 500 ms.

### Minimal SSE contract (example)

```http
event: message
data: {"specversion":"1.0","type":"agent.progress.created","time":"2025-01-01T00:00:00Z","datacontenttype":"application/json","data":{"ts":"...","stage":"plan","note":"boot"}}

event: message
data: {"specversion":"1.0","type":"agent.final.ready","time":"...","data":{"text":"ok"}}
```

### Example E2E assertion (Vitest)

```ts
import { expect, test } from 'vitest'
import { readSSE } from './helpers/sse'

test('streams progress then final', async () => {
  const events = await readSSE('http://localhost:3000/stream', { timeoutMs: 2000 })
  const types = events.map(e => e.type)
  expect(types[0]).toMatch(/agent\.progress\./)
  expect(types.at(-1)).toBe('agent.final.ready')
})
```

## Real vs Mock LLM Client

- Default is `LLM_CLIENT=mock` for reproducibility.
- To use a real OpenAI-compatible client, set `LLM_CLIENT=openai`, `OPENAI_API_KEY`, and optionally `OPENAI_API_BASE`.
- Tests that require network must be skipped unless `NET_EGRESS=on`.

## Running in Each Deployment Profile

- Local-Solo: run tests directly; mock API may be an in-process server.
- Local-Multi: use Docker Compose to bring up `api`, `orchestrator`, `sandbox`, `memory` containers; run tests against `api` container.
- K8s-Multi: run tests against cluster `Service` endpoints; use a test namespace; provide `kubectl port-forward` during local execution.

## VSCode Debugging

Create `.vscode/launch.json` with these starters:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: pytest (uv)",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-q"],
      "env": { "LLM_CLIENT": "mock" }
    },
    {
      "name": "Node: vitest",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "pnpm",
      "runtimeArgs": ["vitest", "run", "--inspect-brk"],
      "cwd": "${workspaceFolder}",
      "env": { "LLM_CLIENT": "mock" }
    }
  ]
}
```

## CI Recommendations

- Pipeline order: lint → unit → mock E2E → package builds.
- Cache `~/.cache/uv` and `~/.pnpm-store`.
- Fail-fast on unit failures; always collect coverage and artifacts from E2E logs.

## Troubleshooting

- Flaky SSE timing: increase client timeout slightly (never exceed 5s in CI).
- Port collisions: choose ports via env (`PORT_API`, `PORT_WEB`) and randomize in CI.
- Missing OpenAI key: ensure `LLM_CLIENT=mock` in CI.

