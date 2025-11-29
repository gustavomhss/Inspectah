#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" python3 -m inspectah.sprint6.cli metrics --domain "$DOMAIN"
