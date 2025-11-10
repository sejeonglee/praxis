#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

LLM_CLIENT="${LLM_CLIENT:-mock}"
PY_PROJECT="python/harness"

emit_span() {
  python3 - "$1" "$2" "$3" "$LLM_CLIENT" <<'PY'
import json, os, sys, time, uuid
span_name, span_status, notes, llm_client = sys.argv[1:5]
print(json.dumps({
    "trace_id": uuid.uuid4().hex,
    "span_id": uuid.uuid4().hex,
    "name": span_name,
    "status": span_status,
    "notes": notes,
    "llm_client": llm_client,
    "ts": time.time()
}))
PY
}

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required for mock E2E tests." >&2
  exit 1
fi

emit_span "e2e-mock-run" "START" "Synchronizing uv environment"
uv sync --project "$PY_PROJECT" >/dev/null

export PYTHONPATH="$ROOT_DIR/$PY_PROJECT"
emit_span "e2e-mock-run" "RUN" "Executing pytest scenarios"
uv run --project "$PY_PROJECT" pytest "$PY_PROJECT/tests/e2e" -q || {
  emit_span "e2e-mock-run" "ERROR" "Pytest scenarios failed"
  exit 1
}

emit_span "e2e-mock-run" "OK" "Mock E2E suite completed"
