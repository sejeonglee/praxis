# Quickstart

1. **Install tooling**
   - Ensure Python 3.11+ and Docker/Podman are available.
   - Install `uv` (`pip install uv` or follow https://github.com/astral-sh/uv`).
2. **Bootstrap dependencies**
   ```bash
   cd /home/sejeonglee/workspaces/praxis/apps/cli
   uv sync
   ```
3. **Start local Redis queue**
   ```bash
   cd /home/sejeonglee/workspaces/praxis/infra/local/redis
   docker compose up -d
   ```
4. **Run Litestar control-plane + mocks**
   ```bash
   cd /home/sejeonglee/workspaces/praxis/apps/cli
   uv run litestar --app praxis_cli.api.app:app --port 8090
   ```
5. **Execute the CLI manually**
   ```bash
   cd /home/sejeonglee/workspaces/praxis/apps/cli
   uv run praxis-cli run --instruction-file samples/reference_instruction.yaml
   ```
   - CLI publishes `SessionInstruction` to Redis Streams, subscribes for progress, and prints the final answer.
6. **Run the automated e2e scenario**
   ```bash
   cd /home/sejeonglee/workspaces/praxis/apps/cli
   uv run python -m praxis_cli.scripts.e2e_scenario --scenario reference
   ```
   - Generates a JSON report under `apps/cli/.reports/` and checks event order + dedupe handling.
7. **Execute unit + integration tests**
   ```bash
   cd /home/sejeonglee/workspaces/praxis/apps/cli
   uv run pytest
   ```
8. **Debug with VS Code**
   - Open the repo in VS Code.
   - Use `Run CLI (reference scenario)` or `Run Litestar API` configurations defined in `.vscode/launch.json`.
   - Breakpoints will hit before the first queue response to satisfy the <30s requirement.
