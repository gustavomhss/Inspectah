#!/usr/bin/env bash
set -euo pipefail

# Smoke test for the Evidence Vault v0 (write -> read).
# Assumes dependencies are installed and the local stub backend is active.
# If the DB is empty, this script will initialise it automatically.

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

PAYLOAD_FILE="$(mktemp)"
trap 'rm -f "$PAYLOAD_FILE"' EXIT

cat > "$PAYLOAD_FILE" <<'JSON'
{"smoke":"evidence","timestamp":"2025-11-14T03:55:00Z"}
JSON

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[evidence_vault_smoke] python interpreter not found" >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
from inspectah import models
models.init_db()
PY

WRITE_OUTPUT="$("$PYTHON_BIN" -m inspectah.evidence_vault.cli write \
  --file "$PAYLOAD_FILE" \
  --source-id smoke_source \
  --evidence-type smoke_test \
  --lgpd-tag lgpd.personal)"

export WRITE_OUTPUT

EVIDENCE_ID="$("$PYTHON_BIN" - <<'PY'
import json, os
data = json.loads(os.environ["WRITE_OUTPUT"])
print(data["evidence_id"])
PY)"

READ_OUTPUT="$("$PYTHON_BIN" -m inspectah.evidence_vault.cli read --id "$EVIDENCE_ID")"

echo "Evidence Vault smoke: write -> read successful"
echo "Write response: $WRITE_OUTPUT"
echo "Read response : $READ_OUTPUT"
