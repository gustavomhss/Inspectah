#!/usr/bin/env bash
set -euo pipefail

cd /Users/gustavoschneiter/Documents/Inspectah

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH=.

echo ">> Starting Inspectah API (inspectah.api:app) on http://127.0.0.1:8000 ..."
uvicorn inspectah.api:app --reload --port 8000
