#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G0_grounding"
SCORECARD_PATH="$SCORECARD_DIR/S22_G0_grounding.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

docs=(
  "$ROOT_DIR/docs/sprint_22_capitulo_1_contexto.md"
  "$ROOT_DIR/docs/sprint_22_capitulo_2_gates.md"
  "$ROOT_DIR/docs/sprint_22_capitulo_3_filemap.md"
  "$ROOT_DIR/docs/sprint_22_capitulo_4_execucao.md"
  "$ROOT_DIR/docs/sprint_22_g0_summary.md"
)

docs_missing=()
for doc in "${docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    docs_missing+=("$doc")
  fi
done

todo_hits="$(rg --no-heading --line-number 'TODO:|FIXME' "${docs[@]}" || true)"
ack_count=$(rg --no-heading '^\\|' "$ROOT_DIR/docs/sprint_22_g0_summary.md" | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}' | wc -l | tr -d ' ')

status="PASS"
notes="Grounding verificado."
if [[ ${#docs_missing[@]} -gt 0 ]]; then
  status="FAIL"
  notes="Documentos da S22 ausentes."
elif [[ -n "$todo_hits" ]]; then
  status="FAIL"
  notes="Encontrados TODO/FIXME nos docs da S22."
elif [[ "$ack_count" -eq 0 ]]; then
  status="FAIL"
  notes="Nenhum ack registrado no resumo G0."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$ack_count"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G0",
    "status": sys.argv[2],
    "notes": sys.argv[3],
    "team_members_ack_count": int(sys.argv[4]),
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

printf "%s\n" "$todo_hits" > "$EVIDENCE_DIR/todo_scan.log"
printf "docs_missing=%s\n" "${docs_missing[*]-}" > "$EVIDENCE_DIR/checks.log"
printf "team_members_ack_count=%s\n" "$ack_count" >> "$EVIDENCE_DIR/checks.log"

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "Verificação de grounding e leitura dos capítulos da S22."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G0] status=$status ack_count=$ack_count"
