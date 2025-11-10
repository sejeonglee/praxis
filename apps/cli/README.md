# Praxis CLI

CLI reference client for the Praxis agentic environment. It publishes `SessionInstruction` payloads to Redis Streams, subscribes to progress events, and prints structured telemetry locally.

## Prerequisites

- Python 3.11+ with [uv](https://github.com/astral-sh/uv)
- Docker/Podman for Redis (`infra/local/redis/docker-compose.yml`)

## Setup

```bash
uv sync
```

## Running the CLI

```bash
# Start Redis
cd ../../infra/local/redis
docker compose up -d

# Launch CLI session from project root
cd ../../apps/cli
uv run praxis-cli run --instruction-file samples/reference_instruction.json
```

The CLI publishes the instruction, listens for events, and exits when a `final` stage event arrives. Structured logs stream to stdout.
