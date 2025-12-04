#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/evidence/S30_G0_scope_and_alignment"
SCORECARD="$ROOT_DIR/out/scorecards/S30_G0_scope_and_alignment.json"

mkdir -p "$LOG_DIR"
STATUS="PASS"
REASONS=()

DOCS_DIR="$ROOT_DIR/Programa 1/Epico 28/Sprint 30"

echo "[s30-g0] Verificando docs e TODO/FIXME" | tee "$LOG_DIR/g0.log"

MISSING=0
for cap in 1 2 3 4; do
  if ! ls "$DOCS_DIR"/Capitulo\ "$cap"/Bloco*.md >/dev/null 2>&1; then
    MISSING=1
    REASONS+=("Capítulo $cap faltando")
  fi
done

if [ "$MISSING" -eq 1 ]; then
  STATUS="FAIL"
fi

if rg -n "TODO|FIXME|TBD" "$DOCS_DIR" >/dev/null 2>&1; then
  STATUS="FAIL"
  REASONS+=("Encontrado TODO/FIXME/TBD em docs da sprint")
fi

REASONS_JSON=$(printf '%s\n' "${REASONS[@]:-}" | python3 -c "import sys,json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")

cat > "$SCORECARD" <<JSON
{
  "gate": "S30_G0_scope_and_alignment",
  "status": "$STATUS",
  "reasons": $REASONS_JSON
}
JSON

echo "[s30-g0] status=$STATUS scorecard=$SCORECARD"
