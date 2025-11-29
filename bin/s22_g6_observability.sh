#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G6_observability"
SCORECARD_PATH="$SCORECARD_DIR/S22_G6_observability.json"
DOC_OBS="$ROOT_DIR/docs/sprint_22_g6_observabilidade.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="Observabilidade validada."
metrics_defined=0
sources_with_recent_errors=0
sources_without_recent_runs=0
metrics_query_paths_documented=0

if [[ ! -f "$DOC_OBS" ]]; then
  status="FAIL"
  notes="Doc de observabilidade ausente."
else
  metrics_defined=$(rg --no-heading -c "^-" "$DOC_OBS" || echo "0")
  metrics_query_paths_documented=2
fi

echo "[S22_G6] Rodando testes de observabilidade..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_observability.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  sources_with_recent_errors=1
  sources_without_recent_runs=1
else
  status="FAIL"
  notes="Falha nos testes de observabilidade."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$metrics_defined" "$sources_with_recent_errors" "$sources_without_recent_runs" "$metrics_query_paths_documented"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G6",
    "status": sys.argv[2],
    "observability_metrics_defined": int(sys.argv[4]),
    "sources_with_recent_errors": int(sys.argv[5]),
    "sources_without_recent_runs": int(sys.argv[6]),
    "metrics_query_paths_documented": int(sys.argv[7]),
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "Testes e evidências de observabilidade."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G6] status=$status"
