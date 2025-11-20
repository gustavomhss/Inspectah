#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G7"
SCORECARD_PATH="$SCORECARD_DIR/S12_G7_observabilidade.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$ROOT_DIR" "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
scorecard_path = Path(sys.argv[3])

scorecard_files = {
    "SLI-1": root / "out/scorecards/S12_G1_sources_scheduler.json",
    "SLI-2": root / "out/scorecards/S12_G3_debunker_coverage.json",
    "SLI-3": root / "out/scorecards/S12_G4_cases_timeline.json",
    "SLI-4": root / "out/scorecards/S12_G5_explorer_e2e.json",
    "SLI-5": root / "out/scorecards/S12_G6_feedback_flow.json",
}

missing = [name for name, path in scorecard_files.items() if not path.exists()]
if missing:
    raise SystemExit(f"Scorecards ausentes para G7: {missing}")

metrics = {}
for sli_id, path in scorecard_files.items():
    data = json.loads(path.read_text(encoding="utf-8"))
    sli_block = data.get("slis", {}).get(sli_id)
    if not sli_block:
        raise SystemExit(f"Scorecard {path.name} não contém métricas para {sli_id}")
    metrics[sli_id] = {
        "value": sli_block.get("value"),
        "slo": sli_block.get("slo"),
        "status": sli_block.get("status"),
        "source_gate": data.get("gate"),
        "description": sli_block.get("description"),
    }

metrics_snapshot = {
    "sli_1_freshness": metrics["SLI-1"],
    "sli_2_debunker_coverage": metrics["SLI-2"],
    "sli_3_case_timeline_integrity": metrics["SLI-3"],
    "sli_4_explorer_success_rate": metrics["SLI-4"],
    "sli_5_feedback_delivery_ratio": metrics["SLI-5"],
}

metrics_snapshot_path = evidence_dir / "metrics_snapshot.json"
metrics_snapshot_path.write_text(json.dumps(metrics_snapshot, indent=2, ensure_ascii=False), encoding="utf-8")

log_files = [
    root / "out/evidence/S12_G1/scheduler_logs.txt",
    root / "out/evidence/S12_G2/pipeline_report.json",
    root / "out/evidence/S12_G5/flows_log.json",
    root / "out/evidence/S12_G6/feedback_list_final.json",
]
logs_output = evidence_dir / "logs_sample.txt"
with logs_output.open("w", encoding="utf-8") as handle:
    for log_path in log_files:
        if not log_path.exists():
            continue
        handle.write(f"===== {log_path.relative_to(root)} =====\n")
        handle.write(log_path.read_text(encoding="utf-8")[:4000])
        handle.write("\n\n")

overall_status = "PASS" if all(entry["status"] == "PASS" for entry in metrics.values()) else "FAIL"

scorecard = {
    "gate": "S12-G7",
    "status": overall_status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": metrics,
    "details": {
        "metrics_snapshot": str(metrics_snapshot_path),
        "logs_snapshot": str(logs_output),
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
if overall_status != "PASS":
    raise SystemExit("S12-G7 falhou. Verifique métricas consolidadas.")
PY

echo "S12-G7 OK. Scorecard: $SCORECARD_PATH"
