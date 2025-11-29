#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="dominio_piloto"

if [[ $# -gt 0 && "$1" != --* ]]; then
  DOMAIN="$1"
  shift
fi

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" python3 -m inspectah.sprint6.cli query --domain "$DOMAIN" "$@"
