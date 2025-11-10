#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

LLM_CLIENT="${LLM_CLIENT:-mock}"

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

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is required for unit tests." >&2
  exit 1
fi

emit_span "unit-suite-run" "START" "Installing workspace dependencies"
pnpm install --ignore-scripts >/dev/null 2>&1 || pnpm install --ignore-scripts

emit_span "unit-suite-run" "RUN" "Executing vitest"
pnpm vitest --run --reporter verbose || {
  emit_span "unit-suite-run" "ERROR" "Vitest execution failed"
  exit 1
}

emit_span "unit-suite-run" "OK" "Unit suite completed"
