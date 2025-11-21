#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${S12_MODE:-test}"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G1"
RAW_EVENTS_DIR="$EVIDENCE_DIR/raw_events"
LOG_FILE="$EVIDENCE_DIR/scheduler_logs.txt"
SOURCES_SNAPSHOT="$EVIDENCE_DIR/sources_config.json"
SCORECARD_PATH="$SCORECARD_DIR/S12_G1_sources_scheduler.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR" "$RAW_EVENTS_DIR"
: > "$LOG_FILE"
rm -f "$RAW_EVENTS_DIR"/*.json 2>/dev/null || true

python3 - <<'PY' "$MODE" "$LOG_FILE" "$RAW_EVENTS_DIR" "$SOURCES_SNAPSHOT" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s12_scheduler import run_scheduler_once
from scripts.s12_sources_registry import export_sources_snapshot

mode = sys.argv[1]
log_path = Path(sys.argv[2])
raw_dir = Path(sys.argv[3])
snapshot_path = Path(sys.argv[4])
scorecard_path = Path(sys.argv[5])

summary = run_scheduler_once(mode=mode, log_path=log_path, raw_events_dir=raw_dir)
export_sources_snapshot(snapshot_path)

total_sources = summary["total_sources"]
successes = summary["successes"]
freshness_ratio = 0.0 if total_sources == 0 else successes / total_sources

sli_status = "PASS" if freshness_ratio >= 0.95 else ("WARN" if freshness_ratio >= 0.90 else "FAIL")
overall_status = "PASS" if sli_status == "PASS" and summary["failures"] == 0 else "FAIL"

scorecard = {
    "gate": "S12-G1",
    "status": overall_status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": {
        "SLI-1": {
            "value": round(freshness_ratio, 3),
            "slo": 0.95,
            "status": sli_status,
            "description": "Freshness ratio for pilot domains during test window.",
        }
    },
    "details": {
        "mode": mode,
        "total_sources": total_sources,
        "successes": successes,
        "failures": summary["failures"],
        "total_events": summary["total_events"],
        "executions": summary["results"],
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({"status": overall_status, "freshness_ratio": freshness_ratio}, indent=2))
if overall_status != "PASS":
    raise SystemExit("S12-G1 falhou. Verifique logs e scorecard.")
PY

echo "S12-G1 OK. Scorecard: $SCORECARD_PATH"
