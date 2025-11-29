#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
SEED="${ORR_SEED:-1337}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT="$2"
      shift 2
      ;;
    --seed)
      SEED="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done
EVID_DIR="$OUT/evidence/T3_contract"
SCORECARD="$OUT/scorecards/T3_contract.json"
LOG="$EVID_DIR/unittest.log"
MANIFEST="$EVID_DIR/MANIFEST.json"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
set +e
python3 -m unittest discover -s tests/contract -p 'test_watcher_rss_news_minimal.py' >"$LOG" 2>&1
RC=$?
python3 -m unittest discover -s tests/integration -p 'test_explore_api.py' >>"$LOG" 2>&1
RC2=$?
RC=$((RC | RC2))
set -e
FINISH=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 - <<'PY2' "$LOG" "$MANIFEST" "$SCORECARD" "$START" "$FINISH" "$RC"
import hashlib
import json
import sys
from pathlib import Path
log_path, manifest_path, scorecard_path, started, finished, rc = sys.argv[1:7]
rc = int(rc)
log = Path(log_path)
log_sha = hashlib.sha256(log.read_bytes()).hexdigest()
manifest = {
    "files": [
        {"path": log.as_posix(), "sha256": log_sha, "bytes": log.stat().st_size}
    ]
}
Path(manifest_path).write_text(json.dumps(manifest, indent=2))
passed = rc == 0
scorecard = {
    "gate": "T3_contract",
    "version": "1.0",
    "started_at": started,
    "finished_at": finished,
    "passed": passed,
    "failures": [] if passed else ["contract-tests-failed"],
    "metrics": {"exit_code": rc},
    "artifacts": manifest["files"],
    "notes": ""
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2))
if not passed:
    sys.exit(1)
PY2
