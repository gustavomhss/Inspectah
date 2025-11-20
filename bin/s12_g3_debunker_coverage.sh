#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G3"
SCORECARD_PATH="$SCORECARD_DIR/S12_G3_debunker_coverage.json"
MESSAGE="S12-G3 placeholder: cobertura do Debunker v0 será medida na Wave 2."

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
echo "$MESSAGE" > "$EVIDENCE_DIR/placeholder.log"

python3 - <<'PY' "$SCORECARD_PATH" "$MESSAGE"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
message = sys.argv[2]
scorecard_path.write_text(
    json.dumps(
        {
            "gate": "S12-G3",
            "status": "FAIL",
            "details": {"notes": message},
            "slis": {},
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        indent=2,
    ),
    encoding="utf-8",
)
PY

>&2 echo "$MESSAGE"
exit 1
