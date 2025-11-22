#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T5_performance_and_bundle"
SCORECARD_PATH="$SCORECARD_DIR/S17_T5_performance_and_bundle.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

set +e
(cd "$FRONTEND_DIR" && npm run build) > "$EVIDENCE_DIR/build.log" 2>&1
BUILD_STATUS=$?
set -e

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$BUILD_STATUS"
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
build_status = int(sys.argv[3])

log_text = (evidence_dir / "build.log").read_text(encoding="utf-8") if (evidence_dir / "build.log").exists() else ""
bundles = []
for line in log_text.splitlines():
    if line.strip().startswith("dist/"):
        match = re.findall(r"dist/\S+\s+([0-9.]+) kB \u2502 gzip: ([0-9.]+) kB", line)
        if match:
            bundles.append({"artifact": line.strip().split()[0], "size_kb": float(match[0][0]), "gzip_kb": float(match[0][1])})

status = "PASS" if build_status == 0 else "FAIL"
scorecard = {
    "gate": "S17_T5_performance_and_bundle",
    "status": status,
    "details": {
        "objective": "Medir build e tamanho de bundle inicial",
        "bundle_sizes": bundles,
        "build_log": str(evidence_dir / "build.log"),
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T5] Falhou; build não finalizou.")
PY

echo "[S17_T5] OK. Scorecard em $SCORECARD_PATH"
