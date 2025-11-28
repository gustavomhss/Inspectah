#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
EVID_DIR="$OUT/evidence/T5_metrics"
SCORECARD="$OUT/scorecards/T5_metrics.json"
LOG="$EVID_DIR/unittest.log"
METRICS_JSON="$EVID_DIR/metrics.json"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -m unittest tests.integration.test_metrics_d8 >"$LOG" 2>&1
python3 - <<'PY' "$METRICS_JSON" "tests/fixtures/rss_sample.xml"
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from inspectah.config import EVIDENCE_DIR
from inspectah.metrics import get_snapshot, reset_metrics
from inspectah.models import fetch_items_by_source, get_connection, init_db, reset_db
from inspectah.watchers import run_once_for_source
from inspectah.explore.api import query_items

metrics_path = Path(sys.argv[1])
fixture = sys.argv[2]
reset_db()
if EVIDENCE_DIR.exists():
    shutil.rmtree(EVIDENCE_DIR)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
init_db()
reset_metrics()
run_once_for_source('rss_news_minimal', use_fixture=True, fixture_path=fixture)
query_items()
snapshot = get_snapshot()
if snapshot['inspectah_run_latency_ms']['count'] < 1 or snapshot['inspectah_explore_query_latency_ms']['count'] < 1:
    raise SystemExit('metrics incomplete')
for key in snapshot:
    if snapshot[key]['min'] < 0:
        raise SystemExit('negative latency detected')
metrics_path.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
PY
python3 - <<'PY' "$EVID_DIR"
import hashlib
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
files = []
for path in sorted(root.rglob('*')):
    if path.is_file():
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path": rel, "sha256": digest, "bytes": path.stat().st_size})
(root / 'MANIFEST.json').write_text(json.dumps({"files": files}, indent=2), encoding='utf-8')
PY
FINISH=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 - <<'PY' "$SCORECARD" "$START" "$FINISH"
import json
import sys
from pathlib import Path
scorecard_path, started, finished = sys.argv[1:4]
scorecard = {
    "gate": "T5_metrics",
    "version": "1.0",
    "started_at": started,
    "finished_at": finished,
    "passed": True,
    "failures": [],
    "metrics": {},
    "artifacts": [
        {"path": f"{Path(scorecard_path).parent.parent}/evidence/T5_metrics/metrics.json", "sha256": None}
    ],
    "notes": "metrics snapshot"
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
PY
