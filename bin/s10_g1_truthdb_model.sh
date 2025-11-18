#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G1"
SCORECARD="$SCORECARD_DIR/S10_G1_truthdb_model.json"
LOG_FILE="$EVIDENCE_DIR/tests.log"
DB_PATH="$ROOT_DIR/out/databases/s10_truthdb.sqlite"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR" "$(dirname "$DB_PATH")"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

status="PASS"
migration_status="PASS"
migration_details="Migration aplicada com sucesso"
test_status="PASS"
test_details="Testes executados via shim"
future_ready_status="PASS"
future_ready_value="0.0"

if ! python3 "$ROOT_DIR/migrations/versions/0001_s10_truthdb_core.py" "$DB_PATH" >/dev/null 2>&1; then
  migration_status="FAIL"
  migration_details="Falha ao aplicar migration Truth-DB"
  status="FAIL"
fi

set +e
python3 "$ROOT_DIR/bin/s5_pytest_shim.py" \
  "$ROOT_DIR/tests/truthdb/test_models.py" \
  >"$LOG_FILE" 2>&1
shim_exit=$?
set -e
if [[ $shim_exit -ne 0 ]]; then
  test_status="FAIL"
  test_details="Falha ao rodar tests/truthdb/test_models.py (ver tests.log)"
  status="FAIL"
fi

future_ready_value="$(python3 - <<'PY'
from inspectah.truthdb.models import build_pilot_truthdb
db = build_pilot_truthdb()
print(f"{db.future_ready_completeness():.4f}")
PY
)"

python3 - <<'PY' "$EVIDENCE_DIR/pilot_snapshot.json"
import json
import sys
from inspectah.truthdb.models import build_pilot_truthdb
path = sys.argv[1]
snapshot = build_pilot_truthdb().snapshot()
with open(path, "w", encoding="utf-8") as fp:
    json.dump(snapshot, fp, default=str, indent=2)
PY

future_ready_bucket=$(python3 - <<PY
value = float("$future_ready_value")
if value < 0.90:
    print("fail")
elif value < 0.95:
    print("warn")
else:
    print("pass")
PY
)

if [[ "$future_ready_bucket" == "fail" ]]; then
  future_ready_status="FAIL"
  status="FAIL"
elif [[ "$future_ready_bucket" == "warn" ]] && [[ "$status" != "FAIL" ]]; then
  future_ready_status="WARN"
  status="WARN"
fi

cat >"$SCORECARD" <<JSON
{
  "gate_id": "S10_G1",
  "name": "Truth-DB canonical model",
  "status": "$status",
  "slis": {
    "future_ready_completeness": $future_ready_value
  },
  "checks": [
    {
      "id": "migration",
      "description": "Aplicar migrations/versions/0001_s10_truthdb_core.py",
      "status": "$migration_status",
      "details": "$migration_details"
    },
    {
      "id": "models-tests",
      "description": "Rodar tests/truthdb/test_models.py via shim",
      "status": "$test_status",
      "details": "$test_details"
    },
    {
      "id": "future-ready",
      "description": "Calcular future_ready_completeness",
      "status": "$future_ready_status",
      "details": "Valor medido: $future_ready_value"
    }
  ],
  "meta": {
    "ts": "$ts",
    "git_commit": "$git_commit",
    "branch": "$git_branch"
  }
}
JSON

if [[ "$status" == "FAIL" ]]; then
  exit 1
fi
exit 0
