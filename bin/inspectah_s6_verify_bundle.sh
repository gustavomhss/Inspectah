#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" "$PYTHON_BIN" -m inspectah.sprint6.cli verify-bundle
