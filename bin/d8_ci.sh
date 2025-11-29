#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
TIMESTAMP=$(date -u +"%Y%m%d-%H%M%S")
RUN_DIR="$OUT/evidence/D8_smoke_run_$TIMESTAMP"
BUNDLE_ZIP="$OUT/evidence/D8_smoke_bundle_$TIMESTAMP.zip"
LATEST_INFO="$OUT/evidence/D8_latest_bundle.json"
LATEST_METRICS="$OUT/evidence/D8_latest_metrics.json"
METRICS_PATH="$RUN_DIR/metrics.json"
SUMMARY_PATH="$RUN_DIR/summary.json"
FIXTURE="tests/fixtures/rss_sample.xml"
SCORECARD="$OUT/scorecards/D8_ci.json"
mkdir -p "$RUN_DIR" "$OUT/scorecards"
START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
bin/orr_t0.sh
bin/orr_t1.sh
bin/orr_t2.sh
bin/orr_t3.sh
python3 - <<'PY' "$RUN_DIR" "$METRICS_PATH" "$SUMMARY_PATH" "$LATEST_METRICS" "$FIXTURE"
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from inspectah.config import EVIDENCE_DIR
from inspectah.metrics import get_snapshot, reset_metrics
from inspectah.models import fetch_items_by_source, get_connection, init_db, reset_db
from inspectah.watchers import run_once_for_source
from inspectah.explore.api import query_items

run_dir, metrics_path, summary_path, latest_metrics_path, fixture = [Path(arg) if i < 4 else Path(arg) for i, arg in enumerate(__import__('sys').argv[1:5])] + [__import__('sys').argv[5]]
reset_db()
if EVIDENCE_DIR.exists():
    shutil.rmtree(EVIDENCE_DIR)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
init_db()
reset_metrics()
created = run_once_for_source('rss_news_minimal', use_fixture=True, fixture_path=str(fixture))
query = query_items()
snapshot = get_snapshot()
metrics_path.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
latest_metrics_path.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
with get_connection() as conn:
    items = fetch_items_by_source(conn, 'rss_news_minimal')
manifest_path = None
if items:
    manifest_path = Path(items[0]['manifest_path'])
summary = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'items_created': created,
    'total_items': len(items),
    'sample_manifest': manifest_path.as_posix() if manifest_path else None,
}
summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
if manifest_path:
    target = run_dir / 'sample_manifest'
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for file_path in manifest_path.parent.iterdir():
        if file_path.is_file():
            shutil.copy(file_path, target / file_path.name)
PY
cp out/evidence/T2_unit/unittest.log "$RUN_DIR/T2_unit.log"
cp out/evidence/T3_contract/unittest.log "$RUN_DIR/T3_contract.log"
SAMPLE_MANIFEST=$(find data/evidence/rss_news_minimal -name manifest.json | head -n 1 || true)
if [[ -n "$SAMPLE_MANIFEST" ]]; then
  cp "$SAMPLE_MANIFEST" "$RUN_DIR/rss_manifest.json"
fi
python3 - <<'PY' "$RUN_DIR"
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
(cd "$RUN_DIR" && zip -qr "$BUNDLE_ZIP" .)
BUNDLE_SHA=$(shasum -a 256 "$BUNDLE_ZIP" | awk '{print $1}')
FINISH=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 - <<'PY' "$LATEST_INFO" "$BUNDLE_ZIP" "$BUNDLE_SHA" "$RUN_DIR" "$SUMMARY_PATH" "$METRICS_PATH"
import json
from pathlib import Path
info_path, bundle_path, bundle_sha, run_dir, summary_path, metrics_path = [Path(arg) if i!=1 else arg for i, arg in enumerate(__import__('sys').argv[1:7])]
data = {
    "bundle_zip": bundle_path,
    "bundle_sha256": bundle_sha,
    "bundle_dir": run_dir,
    "summary_path": summary_path,
    "metrics_path": metrics_path,
}
info_path.write_text(json.dumps({k: str(v) if isinstance(v, Path) else v for k, v in data.items()}, indent=2), encoding='utf-8')
PY
python3 - <<'PY' "$SCORECARD" "$BUNDLE_ZIP" "$BUNDLE_SHA" "$START" "$FINISH"
import json
import sys
from pathlib import Path
scorecard_path, bundle_zip, bundle_sha, started, finished = sys.argv[1:6]
scorecard = {
    "gate": "D8_ci",
    "version": "1.0",
    "started_at": started,
    "finished_at": finished,
    "passed": True,
    "failures": [],
    "metrics": {},
    "artifacts": [
        {"path": bundle_zip, "sha256": bundle_sha}
    ],
    "notes": "D8 smoke run"
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
PY
