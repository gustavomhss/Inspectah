#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi
UVICORN_BIN="$REPO_ROOT/.venv/bin/uvicorn"
if [[ ! -x "$UVICORN_BIN" ]]; then
  UVICORN_BIN="$(command -v uvicorn)"
fi
if [[ -z "$UVICORN_BIN" ]]; then
  echo "uvicorn não encontrado." >&2
  exit 1
fi

read -r HOST PORT DEBUG <<<"$($PYTHON_BIN - <<'PY'
from inspectah.ui.config import get_settings
s = get_settings()
print(s.host, s.port, int(s.debug))
PY
)"


PID_DIR="$REPO_ROOT/out/ui"
LOG_DIR="$REPO_ROOT/out/logs"
PID_FILE="$PID_DIR/inspectah_ui.pid"
LOG_FILE="$LOG_DIR/inspectah_ui.log"
mkdir -p "$PID_DIR" "$LOG_DIR"

if [[ -f "$PID_FILE" ]]; then
  existing_pid="$(cat "$PID_FILE")"
  if ps -p "$existing_pid" >/dev/null 2>&1; then
    echo "Inspectah UI já está em execução (PID $existing_pid)." >&2
    exit 0
  fi
fi

echo "Iniciando Inspectah UI em http://$HOST:$PORT (log: $LOG_FILE)"
set +e
nohup "$UVICORN_BIN" "inspectah.ui:app" --host "$HOST" --port "$PORT" >"$LOG_FILE" 2>&1 &
pid=$!
set -e
echo "$pid" >"$PID_FILE"
echo "PID $pid registrado em $PID_FILE"
