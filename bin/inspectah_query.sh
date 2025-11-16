#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="dominio_piloto"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

if [[ $# -gt 0 && "$1" != --* ]]; then
  DOMAIN="$1"
  shift
fi

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" "$PYTHON_BIN" -m inspectah.sprint6.cli query --domain "$DOMAIN" "$@"
