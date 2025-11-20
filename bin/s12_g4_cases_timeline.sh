#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G4"
SCORECARD_PATH="$SCORECARD_DIR/S12_G4_cases_timeline.json"
MESSAGE="S12-G4 placeholder: invariantes de casos/timeline serão validadas na Wave 2."

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
            "gate": "S12-G4",
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
