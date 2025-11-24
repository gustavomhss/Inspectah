#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G5_safety"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G5_safety.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
cd "$ROOT_DIR"
STATUS="PASS"; NOTES="tests/agents/test_s21_1_copiloto_safety.py"
if ! .venv/bin/python -m pytest tests/agents/test_s21_1_copiloto_safety.py -q >"$EVIDENCE_DIR/safety.log" 2>&1; then
  STATUS="FAIL"; NOTES="Falha nos testes de segurança"
fi
python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$NOTES"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G5","status":sys.argv[2],"automated_checks":{"status":sys.argv[2],"details":sys.argv[3]},"reviewers_internal":[],"reviewers_external":[],"risk_level":"low" if sys.argv[2]=="PASS" else "high","notes":sys.argv[3],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); files=[p.name for p in ed.iterdir() if p.is_file()]
(ed/"MANIFEST.json").write_text(json.dumps({"files":sorted(files),"notes":"Log de testes de segurança"}, indent=2), encoding="utf-8")
PY
echo "[S21_1_G5] status=$STATUS"
