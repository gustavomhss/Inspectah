#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G3"
SCORECARD_PATH="$SCORECARD_DIR/S12_G3_debunker_coverage.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
rm -f "$EVIDENCE_DIR"/*.json >/dev/null 2>&1 || true

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s12_debunker_runner import evaluate_batch, summarize_decisions
from scripts.s12_ingest_pipeline import load_normalized_events, run_ingest_pipeline

evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

# Garante que os dados estejam atualizados
run_ingest_pipeline()
normalized_events = load_normalized_events()
eligible_events = [evt for evt in normalized_events if evt.get("eligible", True)]

if not eligible_events:
    raise SystemExit("S12-G3 não possui eventos elegíveis para medir cobertura.")

decisions = evaluate_batch(eligible_events)
coverage = len(decisions) / len(eligible_events)
decision_breakdown = summarize_decisions(decisions)

coverage_report = {
    "eligible_events": len(eligible_events),
    "decisions_recorded": len(decisions),
    "coverage": round(coverage, 3),
    "decision_breakdown": decision_breakdown["by_decision"],
}

(evidence_dir / "coverage_report.json").write_text(json.dumps(coverage_report, indent=2, ensure_ascii=False), encoding="utf-8")
sample = decisions[:5]
(evidence_dir / "debunker_decisions_sample.json").write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")

status = "PASS" if abs(coverage - 1.0) < 1e-9 else "FAIL"
scorecard = {
    "gate": "S12-G3",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": {
        "SLI-2": {
            "value": round(coverage, 3),
            "slo": 1.0,
            "status": status,
            "description": "Cobertura total do Debunker v0 para eventos elegíveis.",
        }
    },
    "details": coverage_report,
}

scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"status": status, "coverage": round(coverage, 3)}, indent=2, ensure_ascii=False))
if status != "PASS":
    raise SystemExit("S12-G3 falhou. verifique cobertura do Debunker.")
PY

echo "S12-G3 OK. Scorecard: $SCORECARD_PATH"
