#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G0_scope"
SCORECARD_PATH="$SCORECARD_DIR/S18_G0_scope.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

CAP_FILES=(
  "$ROOT_DIR/Sprint 18/Capitulo 1.md"
  "$ROOT_DIR/Sprint 18/Capitulo 2.md"
  "$ROOT_DIR/Sprint 18/Capitulo 3.md"
  "$ROOT_DIR/Sprint 18/Capitulo 4.md"
)

missing=0
for file in "${CAP_FILES[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "[S18_G0] Arquivo ausente: $file" >&2
    missing=1
  fi
done

todo_hits="$(rg --no-heading --line-number -w 'TODO' "${CAP_FILES[@]}" || true)"
status="PASS"
details="Todos os capítulos presentes e sem TODOs."
if [[ $missing -ne 0 ]]; then
  status="FAIL"
  details="Faltam capítulos obrigatórios."
elif [[ -n "$todo_hits" ]]; then
  status="FAIL"
  details="Encontrados TODOs nos capítulos: $todo_hits"
fi

cat > "$EVIDENCE_DIR/README.md" <<'EOF'
# S18_G0 — Escopo e intenção

Este gate verifica a presença e a sanidade dos capítulos da Sprint 18.
EOF

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$details"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
status = sys.argv[2]
details = sys.argv[3]

scorecard = {
    "gate_id": "S18_G0",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {
        "note": details,
    },
}
path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit(f"[S18_G0] {details}")
PY

echo "[S18_G0] OK - scorecard em $SCORECARD_PATH"
