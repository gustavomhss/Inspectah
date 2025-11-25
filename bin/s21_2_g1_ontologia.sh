#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_2_G1_ontologia"
SCORECARD_PATH="$SCORECARD_DIR/S21_2_G1_ontologia.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

docs_ok=true
for doc in "$ROOT_DIR/docs/sprint_21_modelo_dados_fontes.md" "$ROOT_DIR/docs/sprint_21_2_ontologia_fontes_v2.md"; do
  [[ -f "$doc" ]] || docs_ok=false
done

tests_ok=false
if PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest tests/sources -q >"$EVIDENCE_DIR/tests.log" 2>&1; then
  tests_ok=true
fi

python3 - <<'PY' "$ROOT_DIR" "$EVIDENCE_DIR"
import sqlite3, sys, json
from pathlib import Path
root, evid_dir = sys.argv[1], Path(sys.argv[2])
db = Path(root)/"out/databases/s21_sources.sqlite"
conn = sqlite3.connect(db)
try:
    cur = conn.execute("PRAGMA table_info('sources')")
    cols = [row[1] for row in cur.fetchall()]
finally:
    conn.close()
snapshot = {"columns": cols}
(evid_dir/"schema_snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
PY

refresh_in_model=false
official_type=false
if grep -q "refresh_interval" "$ROOT_DIR/app/sources/models.py"; then refresh_in_model=true; fi
if grep -q "official_open" "$ROOT_DIR/app/sources/validators.py"; then official_type=true; fi

status="PASS"
if [[ "$docs_ok" != true || "$tests_ok" != true || "$refresh_in_model" != true || "$official_type" != true ]]; then
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$docs_ok" "$tests_ok" "$refresh_in_model" "$official_type"
import json, sys
from datetime import datetime, timezone
path, status, docs_ok, tests_ok, refresh_ok, official_ok = sys.argv[1:]
out = {
    "gate_id": "S21_2_G1_ontologia",
    "status": status,
    "docs_aligned": docs_ok == "True",
    "tests_sources_pass": tests_ok == "True",
    "refresh_interval_in_model": refresh_ok == "True",
    "official_open_type_defined": official_ok == "True",
    "notes": "Ontologia v2 verificada (refresh + official_open)",
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}
from pathlib import Path
Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
files = [p.name for p in root.iterdir() if p.is_file()]
manifest = {"files": sorted(files), "notes": "Ontologia v2 (refresh_interval, official_open)"}
(root/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_2_G1] status=$status"
