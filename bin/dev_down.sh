#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

PID_FILE="$ROOT/out/dev/inspectah.pid"
SHUTDOWN_FILE="$ROOT/out/dev/inspectah.shutdown"
LOG_FILE="$ROOT/out/logs/dev_api.log"

if [[ ! -f "$PID_FILE" ]]; then
  echo "[dev_down] Nenhum PID encontrado em $PID_FILE. Nada a fazer."
  exit 0
fi

touch "$SHUTDOWN_FILE"
echo "[dev_down] Sinal de shutdown registrado em $SHUTDOWN_FILE."

for _ in {1..30}; do
  if [[ ! -f "$PID_FILE" ]]; then
    break
  fi
  sleep 1
done

if [[ -f "$PID_FILE" ]]; then
  echo "[dev_down] PID ainda presente após 30s; removendo marcador manualmente."
fi

rm -f "$PID_FILE" "$SHUTDOWN_FILE"

echo "Logs recentes em: $LOG_FILE"
