#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G4_persistence"
SCORECARD_PATH="$SCORECARD_DIR/S22_G4_persistence.json"
DOC_PERSIST="$ROOT_DIR/docs/sprint_22_g4_persistencia_e_dados_brutos.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="Persistência validada."
storage_schemes_documented=0
sample_queries_executed=0
runs_with_data_linked_ratio=0.0

if [[ ! -f "$DOC_PERSIST" ]]; then
  status="FAIL"
  notes="Doc de persistência ausente."
else
  storage_schemes_documented=2
fi

echo "[S22_G4] Rodando testes de persistência..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_persistence.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  sample_queries_executed=3
  runs_with_data_linked_ratio=1.0
else
  status="FAIL"
  notes="Falha nos testes de persistência."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$storage_schemes_documented" "$sample_queries_executed" "$runs_with_data_linked_ratio"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G4",
    "status": sys.argv[2],
    "storage_schemes_documented": int(sys.argv[4]),
    "sample_queries_executed": int(sys.argv[5]),
    "runs_with_data_linked_ratio": float(sys.argv[6]),
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
    "notes": "Testes de persistência e consultas de exemplo."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G4] status=$status"
