#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
SOURCE_ID="${2:-}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

cd "$REPO_ROOT"
CMD=("$PYTHON_BIN" -m inspectah.sprint6.cli fields-preview --domain "$DOMAIN")
if [[ -n "$SOURCE_ID" ]]; then
  CMD+=(--source "$SOURCE_ID")
fi
PYTHONPATH="$REPO_ROOT" "${CMD[@]}"
