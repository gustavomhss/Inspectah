#!/usr/bin/env bash
set -euo pipefail

# ORR de auditabilidade para S36 (G4) — consolida métricas e gera scorecard/evidências.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BIN="${PY_BIN:-$ROOT/.venv/bin/python}"
DB_PATH="${TRACE_DB_PATH:-$ROOT/out/databases/s36_traces.sqlite}"
DECISIONS_FILE="${DECISIONS_FILE:-$ROOT/data/pilot_politics/decision_records_pilot.jsonl}"
TRACE_METRICS_DIR="$ROOT/out/evidence/S36_trace_metrics"
ORR_DIR="$ROOT/out/evidence/S36_ORR"
SCORECARD_PATH="$ROOT/out/scorecards/S36_ORR_audit.json"
SUMMARY_PATH="$ORR_DIR/S36_ORR_summary.txt"

mkdir -p "$TRACE_METRICS_DIR" "$ORR_DIR" "$ROOT/out/scorecards"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"

echo "[s36_g4_audit_orr] usando DB=$DB_PATH decisions=$DECISIONS_FILE"

"$PY_BIN" scripts/metrics/s36_trace_coverage.py --db "$DB_PATH" --decisions-file "$DECISIONS_FILE" --output "$TRACE_METRICS_DIR/coverage.json"
"$PY_BIN" scripts/metrics/s36_trace_depth.py --db "$DB_PATH" --output "$TRACE_METRICS_DIR/depth.json"
"$PY_BIN" scripts/metrics/s36_trace_link_break_rate.py --db "$DB_PATH" --decisions-file "$DECISIONS_FILE" --output "$TRACE_METRICS_DIR/link_break_rate.json"
"$PY_BIN" scripts/metrics/s36_feedback_rate.py --db "$DB_PATH" --decisions-file "$DECISIONS_FILE" --output "$TRACE_METRICS_DIR/feedback_rate.json"
"$PY_BIN" scripts/metrics/s36_feedback_analysis.py --db "$DB_PATH" --output "$TRACE_METRICS_DIR/feedback_analysis.json"

cp "$TRACE_METRICS_DIR/coverage.json" "$ORR_DIR/coverage.json"
cp "$TRACE_METRICS_DIR/depth.json" "$ORR_DIR/depth.json"
cp "$TRACE_METRICS_DIR/link_break_rate.json" "$ORR_DIR/link_break_rate.json"
cp "$TRACE_METRICS_DIR/feedback_rate.json" "$ORR_DIR/feedback_rate.json"
cp "$TRACE_METRICS_DIR/feedback_analysis.json" "$ORR_DIR/feedback_analysis.json"

TRACE_DIR="$TRACE_METRICS_DIR" SUMMARY_PATH="$SUMMARY_PATH" SCORECARD_PATH="$SCORECARD_PATH" "$PY_BIN" - <<'PY'
import datetime
import json
import os
import pathlib

trace_dir = pathlib.Path(os.environ["TRACE_DIR"])
summary_path = pathlib.Path(os.environ["SUMMARY_PATH"])
scorecard_path = pathlib.Path(os.environ["SCORECARD_PATH"])

coverage = json.loads((trace_dir / "coverage.json").read_text())
link = json.loads((trace_dir / "link_break_rate.json").read_text())
fb_rate = json.loads((trace_dir / "feedback_rate.json").read_text())
fb_analysis = json.loads((trace_dir / "feedback_analysis.json").read_text())

coverage_min = min(bucket.get("trace_coverage_rate", 0.0) for bucket in coverage.values())
link_max = max(bucket.get("trace_link_break_rate", 1.0) for bucket in link.values())
decisions_total = sum(bucket.get("decision_count", 0) for bucket in fb_rate.values())
decisions_with_feedback = sum(bucket.get("decisions_with_feedback", 0) for bucket in fb_rate.values())
feedback_entries = fb_analysis.get("totals", {}).get("feedback_entries", 0)

status = "GO" if (coverage_min >= 0.8 and link_max <= 0.01 and feedback_entries >= 20 and decisions_with_feedback >= 10) else "NO-GO"

summary_lines = [
    f"timestamp={datetime.datetime.utcnow().isoformat()}Z",
    f"status={status}",
    f"coverage_min={coverage_min}",
    f"link_break_rate_max={link_max}",
    f"decisions_with_feedback={decisions_with_feedback}/{decisions_total}",
    f"feedback_entries={feedback_entries}",
    f"evidence_dir={trace_dir}",
]
summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

scorecard = {
    "sprint": "S36",
    "programa": "P2",
    "scope": "auditabilidade/logs/feedback (G0-G4)",
    "status": status,
    "metrics": {
        "coverage": coverage,
        "link_break_rate": link,
        "feedback_rate": fb_rate,
        "feedback_analysis": fb_analysis,
    },
    "evidence": {
        "coverage": "out/evidence/S36_trace_metrics/coverage.json",
        "depth": "out/evidence/S36_trace_metrics/depth.json",
        "link_break_rate": "out/evidence/S36_trace_metrics/link_break_rate.json",
        "feedback_rate": "out/evidence/S36_trace_metrics/feedback_rate.json",
        "feedback_analysis": "out/evidence/S36_trace_metrics/feedback_analysis.json",
        "quality_review": "docs/reviews/s36_trace_quality_review.md",
        "feedback_findings": "docs/analysis/s36_feedback_findings.md",
        "overhead_logs": [
            "out/logs/s36_trace_overhead_baseline.log",
            "out/logs/s36_trace_overhead_with_tracing.log",
        ],
    },
    "notes": [
        "Veja docs/runbooks/S36_audit_orr_checklist.md para passos detalhados.",
        "UI prints em Truth Console / Case / Debunker devem acompanhar este scorecard em GO/NO-GO final.",
    ],
}
scorecard_path.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[s36_g4_audit_orr] status={status} summary={summary_path}")
PY
