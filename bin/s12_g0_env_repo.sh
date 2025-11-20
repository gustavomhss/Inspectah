#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G0"
SCORECARD_PATH="$SCORECARD_DIR/S12_G0_env_repo.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
PLACEHOLDER_LOG="$EVIDENCE_DIR/placeholder.log"
MESSAGE="S12-G0 placeholder: implemente as checagens de repo/env durante a Wave 0.5/1."

cat <<'EOF' > "$PLACEHOLDER_LOG"
S12-G0 ainda está em modo skeleton. Este log mostra que o gate foi chamado,
mas as checagens reais serão implementadas na Wave correspondente.
EOF

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
            "gate": "S12-G0",
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
