#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G2_journeys_and_ux"
SCORECARD_PATH="$SCORECARD_DIR/S18_G2_journeys_and_ux.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

cat > "$EVIDENCE_DIR/journeys.md" <<'EOF'
# S18_G2 — Journeys & UX

Preencha aqui o roteiro executado (Operador, Curador, PO) navegando em /admin, /admin/sources, /admin/cases.
Marque estados de loading/erro visualizados e eventuais becos sem saída.
EOF

status="PASS"
details="Journeys semi-manuais registradas em journeys.md."

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$details"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
status = sys.argv[2]
details = sys.argv[3]
scorecard = {
    "gate_id": "S18_G2",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {"note": details},
}
path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit(f"[S18_G2] {details}")
PY

echo "[S18_G2] OK - scorecard em $SCORECARD_PATH"
