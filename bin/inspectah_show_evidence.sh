#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "uso: $0 <item_id> [dominio]" >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
ITEM_ID="$1"
DOMAIN="${2:-dominio_piloto}"

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" python3 -m inspectah.sprint6.cli show-evidence --domain "$DOMAIN" "$ITEM_ID"
