#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PID_FILE="$REPO_ROOT/out/ui/inspectah_ui.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "Nenhum PID registrado para a UI."
  exit 0
fi

PID="$(cat "$PID_FILE")"
if ps -p "$PID" >/dev/null 2>&1; then
  echo "Encerrando Inspectah UI (PID $PID)"
  kill "$PID"
  wait "$PID" 2>/dev/null || true
else
  echo "Processo $PID não está em execução."
fi
rm -f "$PID_FILE"
echo "UI parada."
