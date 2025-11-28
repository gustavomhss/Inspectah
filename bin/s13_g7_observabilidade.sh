#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S13_G7_observabilidade.json"
mkdir -p "$SCORECARD_DIR"
python3 - <<'PY' "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
scorecard_path.write_text(
    json.dumps(
        {
            "gate": "S13_G7_observabilidade",
            "status": "FAIL",
            "reason": "S13 skeleton – lógica ainda não implementada",
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        indent=2,
    ),
    encoding="utf-8",
)
PY
>&2 echo "[S13] S13_G7_observabilidade ainda não implementado (skeleton)."
exit 1
