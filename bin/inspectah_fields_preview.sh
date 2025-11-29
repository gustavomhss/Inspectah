#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
SOURCE_ID="${2:-}"

cd "$REPO_ROOT"
cmd=(PYTHONPATH="$REPO_ROOT" python3 -m inspectah.sprint6.cli fields-preview --domain "$DOMAIN")
if [[ -n "$SOURCE_ID" ]]; then
  cmd+=(--source "$SOURCE_ID")
fi
"${cmd[@]}"
