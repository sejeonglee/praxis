# Research Summary

## Queue & Event Runtime
- **Decision**: Use Redis Streams (via `redis-py`) for the local message queue.
- **Rationale**: Streams natively provide at-least-once delivery, consumer groups, and ordered history while remaining easy to run through a single-node Redis container; perfect for local/offline dev and mirrors production-grade semantics.
- **Alternatives considered**: Python `asyncio.Queue` (too simplistic, no persistence), RabbitMQ (heavier footprint + extra management), MQTT broker (less natural for ordered workflow transcripts).

## CLI Framework & Packaging
- **Decision**: Implement the CLI with Typer and manage dependencies via `uv`.
- **Rationale**: Typer builds on Click for ergonomic commands, async support, and auto docs; `uv` gives reproducible Python 3.11 environments with fast installs and aligns with the team mandate.
- **Alternatives considered**: argparse (minimal but verbose for multi-command CLIs), Poetry/pip-tools (conflicts with explicit `uv` requirement).

## Control-Plane API & Mock Hosting
- **Decision**: Host mock LLM/DB workers plus health/lifecycle endpoints in a Litestar application that runs alongside the CLI for scripted tests.
- **Rationale**: Litestar is lightweight yet production-ready, supports ASGI, and makes it simple to expose REST endpoints the e2e script can call to reset mocks, inject events, or inspect transcripts.
- **Alternatives considered**: FastAPI (more heavyweight; instruction explicitly prefers Litestar), bare ASGI app (more boilerplate for routing + docs).

## Testing & Automation Strategy
- **Decision**: Use pytest (with pytest-asyncio) for unit/integration tests and ship a Python-based `e2e_scenario.py` script that orchestrates CLI + mocks, invoked through `uv`.
- **Rationale**: Pytest integrates smoothly with Typer/async code, provides fixtures for Redis + mocks, and matches the requested stack; embedding e2e orchestration in Python keeps assertions close to business events and avoids shell-portability issues.
- **Alternatives considered**: unittest (less expressive fixtures), shell-based e2e (fragile across OSes), behave/cucumber (overkill for single scenario).

## Observability & Debug Experience
- **Decision**: Emit structured logs via structlog + OpenTelemetry exporters and provide `.vscode/launch.json` targets for CLI, Litestar API, and e2e script.
- **Rationale**: Structured logs make the e2e verifier and developers consume the same telemetry; VS Code launch configs accelerate breakpoints within <30s as required.
- **Alternatives considered**: ad-hoc `print` logging (hard to parse in scripts), manual debugger setup (slower onboarding, violates UX goals).
