# Implementation Plan: CLI Event-Driven Environment Setup

**Branch**: `[001-cli-env-setup]` | **Date**: 2025-11-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cli-env-setup/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deliver a Python-based CLI client that drives the agentic workflow over a local Redis Streams queue with mocked LLM/DB workers, plus an automated e2e script, pytest suite, and VS Code debugging profiles. The entire toolchain uses `uv`, exposes a Litestar control-plane API for health and mock orchestration, and keeps all artifacts local/offline for reproducible validation.

## Technical Context

**Language/Version**: Python 3.11 (managed via `uv`)
**Primary Dependencies**: Litestar (control API + mocks), redis-py (Redis Streams queue), Pydantic (event contracts), Typer (CLI UX), structlog/OpenTelemetry exporters, pytest/pytest-asyncio
**Storage**: N/A (state lives in Redis Streams and in-memory deterministic mocks)
**Testing**: pytest executed through `uv run pytest`, plus scripted e2e scenario invoked via `uv run python -m praxis_cli.scripts.e2e_scenario`
**Target Platform**: Local developer laptops (Linux/macOS) with Docker/Podman to host Redis and POSIX shell for scripts
**Project Type**: Monorepo `apps/cli` Python project containing CLI + mock services
**Performance Goals**: Reference scenario completes <3 minutes; debugger attaches <30s before first queue response; CLI processes queue events within 500 ms of publication; e2e script must pass 3 consecutive runs without failure
**Constraints**: Offline-friendly; at-least-once delivery with event-ID dedupe; package manager fixed to `uv`; no reliance on external LLMs/DBs; structured logging for every event
**Scale/Scope**: Single-operator focus but support concurrent sessions via UUIDs; footprint limited to local machine resources (<=512 MB RAM for tooling)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` still holds placeholder text, so no explicit principles were ratified. Documented this gap; defaulting to standard expectations (test-first, observability, simplicity) and proceeding. No violations identified pre-Phase 0. After Phase 1 the plan still honors those defaults (tests defined up front, observability captured in telemetry module), so gate remains green.

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-env-setup/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md (created later by /speckit.tasks)
```

### Source Code (repository root)

```text
apps/
  cli/
    pyproject.toml
    uv.lock
    src/praxis_cli/
      __init__.py
      cli.py               # Typer entrypoint + CLI glue
      config.py            # env parsing + default paths
      events.py            # Pydantic data contracts shared by CLI/mocks/tests
      queue.py             # Redis Streams helpers (publish, subscribe, dedupe)
      telemetry.py         # Structured logging + OpenTelemetry spans
      api/
        __init__.py
        app.py             # Litestar app controlling mock workers + health
      mocks/
        llm.py             # Deterministic mock LLM worker
        database.py        # Deterministic mock DB worker
        orchestrator.py    # Simulated agent state machine publishing events
      scripts/
        e2e_scenario.py    # End-to-end scenario runner invoked via uv
    tests/
      unit/
        test_cli_args.py
        test_queue_flow.py
        test_mock_responses.py
      integration/
        test_cli_to_mocks_roundtrip.py
      e2e/
        test_reference_scenario.py

infra/
  local/
    redis/
      docker-compose.yml   # Single-node Redis for queue semantics

.vscode/
  launch.json              # CLI + Litestar debugging presets
```

**Structure Decision**: Keep everything related to the CLI feature inside `apps/cli` to align with the monorepo layout from OBJECTIVE. Shared infra helpers (Redis compose), VS Code configuration, and scripts live at predictable top-level paths so future adapters (web/IDE) can reuse the same queue contracts and tooling.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _None_ | | |
