#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G2"
SCORECARD_PATH="$SCORECARD_DIR/S12_G2_ingest_pipeline.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
rm -f "$EVIDENCE_DIR"/*.json >/dev/null 2>&1 || true

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s12_ingest_pipeline import run_ingest_pipeline

evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

summary = run_ingest_pipeline(evidence_dir=evidence_dir)

case_ratio = summary["case_integrity_ratio"]
timeline_ratio = summary["timeline_integrity_ratio"]
coverage = summary["debunker_coverage"]

slis = {
    "SLI-1": {
        "value": coverage,
        "slo": 0.95,
        "status": "PASS" if coverage >= 0.95 else "FAIL",
        "description": "Cobertura mínima esperada do Debunker dentro do pipeline.",
    },
    "SLI-3": {
        "value": case_ratio,
        "slo": 0.99,
        "status": "PASS" if case_ratio >= 0.99 else ("WARN" if case_ratio >= 0.97 else "FAIL"),
        "description": "Integridade de casos/timelines no pipeline.",
    },
}

overall_status = "PASS" if slis["SLI-1"]["status"] == "PASS" and case_ratio >= 0.99 and timeline_ratio >= 0.99 else "FAIL"

scorecard = {
    "gate": "S12-G2",
    "status": overall_status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": slis,
    "details": summary,
}

scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({"status": overall_status, "details": summary}, indent=2, ensure_ascii=False))
if overall_status != "PASS":
    raise SystemExit("S12-G2 falhou. Verifique o scorecard e as evidências.")
PY

echo "S12-G2 OK. Scorecard: $SCORECARD_PATH"
