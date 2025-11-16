#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "uso: $0 <item_id> [dominio]" >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
ITEM_ID="$1"
DOMAIN="${2:-dominio_piloto}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" "$PYTHON_BIN" -m inspectah.sprint6.cli show-evidence --domain "$DOMAIN" "$ITEM_ID"
