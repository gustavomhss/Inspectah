#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"

OUT_DIR="$ROOT/out/evidence/S9_T8_go_no_go"
SCORECARD="$ROOT/out/scorecards/S9_T8_go_no_go.json"
SUMMARY="$OUT_DIR/summary.json"

mkdir -p "$OUT_DIR" "$(dirname "$SCORECARD")"

export ROOT SUMMARY SCORECARD

python3 - <<'PY'
import json
import os
from pathlib import Path
from datetime import datetime, timezone

root = Path(os.environ["ROOT"])
summary_path = Path(os.environ["SUMMARY"])
scorecard_path = Path(os.environ["SCORECARD"])

scorecards = {
    "S9_T0_scope": root / "out" / "scorecards" / "S9_T0_scope.json",
    "S9_T1_static_quality": root / "out" / "scorecards" / "S9_T1_static_quality.json",
    "S9_T2_unit_and_contracts": root / "out" / "scorecards" / "S9_T2_unit_and_contracts.json",
    "S9_T3_property_and_edge_cases": root / "out" / "scorecards" / "S9_T3_property_and_edge_cases.json",
    "S9_T4_golden_flows": root / "out" / "scorecards" / "S9_T4_golden_flows.json",
    "S9_T5_perf_and_limits": root / "out" / "scorecards" / "S9_T5_perf_and_limits.json",
    "S9_T6_logs_and_evidence": root / "out" / "scorecards" / "S9_T6_logs_and_evidence.json",
    "S9_T7_ci_pipeline": root / "out" / "scorecards" / "S9_T7_ci_pipeline.json",
}

gate_status = {}
missing = []
all_pass = True
for gate, path in scorecards.items():
    if not path.exists():
        gate_status[gate] = "MISSING"
        all_pass = False
        missing.append(str(path))
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    status = data.get("status") or data.get("Status") or "UNKNOWN"
    gate_status[gate] = status
    if status != "PASS":
        all_pass = False

summary_doc = root / "docs" / "sprint_9_summary.md"
summary_doc_ok = summary_doc.exists()
if not summary_doc_ok:
    all_pass = False

decision = "GO" if all_pass else "NO_GO"

summary = {
    "gate": "S9_T8_go_no_go",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "gates": gate_status,
    "summary_doc_present": summary_doc_ok,
    "summary_doc_path": str(summary_doc.relative_to(root)),
    "missing_scorecards": missing,
    "decision": decision,
    "risks": [
        "Monitor saúde das fontes reais quando migrarmos das fixtures.",
        "Persistir métricas em backend dedicado (Prometheus/exporter) nas próximas sprints.",
    ],
    "recommendations": [
        "Automatizar demos e checklist da Fase 8 com base nos goldens.",
        "Priorizar conectores dinâmicos e dashboards para observabilidade contínua.",
    ],
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate": "S9_T8_go_no_go",
    "status": "PASS",
    "decision": decision,
    "summary_path": str(summary_path.relative_to(root)),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY
