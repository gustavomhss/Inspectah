#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G1_frontend_build_and_sanity"
SCORECARD_PATH="$SCORECARD_DIR/S20_G1_frontend_build_and_sanity.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
status="PASS"
M1=1

echo "[S20_G1] Rodando npm test..."
if ! (cd "$FRONTEND_DIR" && npm test >"$EVIDENCE_DIR/npm_test.log" 2>&1); then
  status="FAIL"
  M1=0
fi

echo "[S20_G1] Rodando npm run build..."
if ! (cd "$FRONTEND_DIR" && npm run build >"$EVIDENCE_DIR/npm_build.log" 2>&1); then
  status="FAIL"
  M1=0
fi

cat > "$EVIDENCE_DIR/MANIFEST.json" <<EOF
{
  "commands": [
    "npm test",
    "npm run build"
  ]
}
EOF

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$M1" "$commit_sha"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
M1 = int(sys.argv[3])
commit_sha = sys.argv[4]

scorecard = {
    "gate_id": "S20_G1_frontend_build_and_sanity",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M1": M1},
    "details": {
        "commit": commit_sha,
        "notes": "Build e testes do frontend (npm test, npm run build)."
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G1] FAIL - veja evidências em out/evidence/S20_G1_frontend_build_and_sanity")
PY

echo "[S20_G1] Scorecard gerado em $SCORECARD_PATH"
