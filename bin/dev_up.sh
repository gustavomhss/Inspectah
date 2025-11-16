#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

VENV_DIR="$ROOT/.venv"
PID_DIR="$ROOT/out/dev"
LOG_DIR="$ROOT/out/logs"
PID_FILE="$PID_DIR/inspectah.pid"
LOG_FILE="$LOG_DIR/dev_api.log"
SHUTDOWN_FILE="$PID_DIR/inspectah.shutdown"
UVICORN_HOST="127.0.0.1"
UVICORN_PORT="8000"

mkdir -p "$PID_DIR" "$LOG_DIR"
rm -f "$SHUTDOWN_FILE"

if [[ -f "$PID_FILE" ]]; then
  echo "[dev_up] Encontrado PID anterior em $PID_FILE. Execute bin/dev_down.sh antes de subir novamente." >&2
  exit 1
fi

PYTHON_BIN="python3"
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  PYTHON_BIN="python"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

if ! "$PYTHON" -m pip install --upgrade pip >/dev/null 2>&1; then
  echo "[dev_up] Aviso: falha ao atualizar pip (possível ambiente offline)." >&2
fi
if ! "$PYTHON" -m pip install -e .[dev] >/dev/null 2>&1; then
  echo "[dev_up] Aviso: 'pip install -e .[dev]' falhou (possível ambiente offline)." >&2
fi

"$PYTHON" - <<'PY'
from inspectah import models
models.reset_db()
models.init_db()
PY

nohup "$PYTHON" -m inspectah.devserver --host "$UVICORN_HOST" --port "$UVICORN_PORT" \
  --shutdown-file "$SHUTDOWN_FILE" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

echo "Inspectah dev server iniciado (PID $SERVER_PID)"
echo "Logs: $LOG_FILE"
echo "DB: $($PYTHON - <<'PY'
from inspectah.config import DB_PATH
print(DB_PATH)
PY
)"
echo "API: http://$UVICORN_HOST:$UVICORN_PORT/"
