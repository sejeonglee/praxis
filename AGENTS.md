# praxis Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-10

## Active Technologies

- Python 3.11 (managed via `uv`) + Litestar (control API + mocks), redis-py (Redis Streams queue), Pydantic (event contracts), Typer (CLI UX), structlog/OpenTelemetry exporters, pytest/pytest-asyncio (001-cli-env-setup)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11 (managed via `uv`): Follow standard conventions

## Recent Changes

- 001-cli-env-setup: Added Python 3.11 (managed via `uv`) + Litestar (control API + mocks), redis-py (Redis Streams queue), Pydantic (event contracts), Typer (CLI UX), structlog/OpenTelemetry exporters, pytest/pytest-asyncio

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
