#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

URL="$($PYTHON_BIN - <<'PY'
from inspectah.ui.config import get_settings
s = get_settings()
print(f"http://{s.host}:{s.port}")
PY
)"

echo "Abrindo $URL"
if command -v open >/dev/null 2>&1; then
  open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL"
else
  echo "Abra manualmente: $URL"
fi
