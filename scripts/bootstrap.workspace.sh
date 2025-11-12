#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is required. Install pnpm ^10.13.1 and retry." >&2
  exit 1
fi

echo "[workspace] Installing dependencies via pnpm..."
pnpm install --ignore-scripts

echo "[workspace] Registered packages:"
pnpm ls --depth 0
