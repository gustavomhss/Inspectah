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
EVID_DIR="$OUT/evidence/T0_spec"
SCORECARD="$OUT/scorecards/T0_spec.json"
REPORT="$EVID_DIR/report.json"
MANIFEST="$EVID_DIR/MANIFEST.json"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
SPEC_PATH="docs/d8_spec.md"
STATUS="ok"
if [[ ! -s "$SPEC_PATH" ]]; then
  STATUS="missing"
fi
python3 - <<'PY' "$SPEC_PATH" "$REPORT" "$MANIFEST" "$SCORECARD" "$STATUS"
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
spec_path, report_path, manifest_path, scorecard_path, status = sys.argv[1:6]
passed = status == "ok"
items = []
if status == "ok":
    data = Path(spec_path).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    bytes_count = len(data)
    Path(report_path).write_text(json.dumps({"spec_sha256": sha, "bytes": bytes_count}, indent=2))
    items.append({"path": spec_path, "sha256": sha, "bytes": bytes_count})
else:
    Path(report_path).write_text(json.dumps({"error": "spec missing or empty"}, indent=2))
    items.append({"path": spec_path, "sha256": None, "bytes": 0})
items.append({"path": str(Path(report_path).as_posix()), "sha256": hashlib.sha256(Path(report_path).read_bytes()).hexdigest(), "bytes": Path(report_path).stat().st_size})
Path(manifest_path).write_text(json.dumps({"files": items}, indent=2))
now = datetime.now(timezone.utc).isoformat()
scorecard = {
    "gate": "T0_spec",
    "version": "1.0",
    "started_at": now,
    "finished_at": now,
    "passed": passed,
    "failures": [] if passed else ["spec-missing"],
    "metrics": {},
    "artifacts": [
        {"path": str(Path(report_path).as_posix()), "sha256": hashlib.sha256(Path(report_path).read_bytes()).hexdigest(), "bytes": Path(report_path).stat().st_size}
    ],
    "notes": ""
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2))
if not passed:
    sys.exit(1)
PY
