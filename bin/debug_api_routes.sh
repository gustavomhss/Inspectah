#!/usr/bin/env bash
set -euo pipefail

cd /Users/gustavoschneiter/Documents/Inspectah

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH=.

python -m scripts.print_api_routes
