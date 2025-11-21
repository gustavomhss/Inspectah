#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G4"
PIPELINE_EVIDENCE="$ROOT_DIR/out/evidence/S12_G2"
SCORECARD_PATH="$SCORECARD_DIR/S12_G4_cases_timeline.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
rm -f "$EVIDENCE_DIR"/*.json >/dev/null 2>&1 || true

python3 - <<'PY' "$PIPELINE_EVIDENCE" "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import shutil

from scripts.s12_case_service import validate_cases_snapshot
from scripts.s12_ingest_pipeline import run_ingest_pipeline
from scripts.s12_timeline_service import validate_timeline_snapshot

pipeline_evidence = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
scorecard_path = Path(sys.argv[3])

# Atualiza snapshots do pipeline
run_ingest_pipeline()

cases_src = pipeline_evidence / "cases_snapshot.json"
timelines_src = pipeline_evidence / "timelines_snapshot.json"
if not cases_src.exists() or not timelines_src.exists():
    raise SystemExit("Snapshots do pipeline não encontrados. Rode o G2 primeiro.")

cases_snapshot = json.loads(cases_src.read_text(encoding="utf-8"))
timelines_snapshot = json.loads(timelines_src.read_text(encoding="utf-8"))

# Copia snapshots para a pasta de evidências do G4
shutil.copy2(cases_src, evidence_dir / "cases_snapshot.json")
shutil.copy2(timelines_src, evidence_dir / "timelines_snapshot.json")

cases_report = validate_cases_snapshot(cases_snapshot)
timelines_report = validate_timeline_snapshot(timelines_snapshot)

invariants_report = {
    "cases": cases_report,
    "timelines": timelines_report,
}
(evidence_dir / "invariants_report.json").write_text(json.dumps(invariants_report, indent=2, ensure_ascii=False), encoding="utf-8")

case_ratio = cases_report["case_integrity_ratio"]
timeline_ratio = timelines_report["timeline_integrity_ratio"]
violations = cases_report["violations"] + timelines_report["violations"]

status = "PASS" if case_ratio >= 0.99 and timeline_ratio >= 0.99 and not violations else "FAIL"

scorecard = {
    "gate": "S12-G4",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": {
        "SLI-3": {
            "value": min(case_ratio, timeline_ratio),
            "slo": 0.99,
            "status": "PASS" if case_ratio >= 0.99 and timeline_ratio >= 0.99 else "FAIL",
            "description": "Integridade de casos e timelines (invariantes I1–I3).",
        }
    },
    "details": {
        "case_integrity_ratio": case_ratio,
        "timeline_integrity_ratio": timeline_ratio,
        "violations": violations,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(scorecard["details"], indent=2, ensure_ascii=False))
if status != "PASS":
    raise SystemExit("S12-G4 falhou. Verifique invariantes de casos/timelines.")
PY

echo "S12-G4 OK. Scorecard: $SCORECARD_PATH"
