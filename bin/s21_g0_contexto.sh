#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G0_contexto"
SCORECARD_PATH="$SCORECARD_DIR/S21_G0_contexto.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

docs=(
  "$ROOT_DIR/docs/sprint_21_capitulo_1.md"
  "$ROOT_DIR/docs/sprint_21_capitulo_2_gates.md"
  "$ROOT_DIR/docs/sprint_21_capitulo_3_filemap.md"
  "$ROOT_DIR/docs/sprint_21_capitulo_4_execucao.md"
)

docs_missing=()
for doc in "${docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    docs_missing+=("$doc")
  fi
done

todo_hits="$(rg --no-heading --line-number 'TODO:|FIXME' "${docs[@]}" || true)"

status="PASS"
notes="Contexto materializado."
if [[ ${#docs_missing[@]} -gt 0 ]]; then
  status="FAIL"
  notes="Documentos de capítulo ausentes."
elif [[ -n "$todo_hits" ]]; then
  status="FAIL"
  notes="Encontrados TODO/FIXME nos capítulos."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S21_G0",
    "status": sys.argv[2],
    "automated_checks": {"status": sys.argv[2], "details": sys.argv[3]},
    "reviewers_internal": [],
    "reviewers_external": [],
    "risk_level": "low" if sys.argv[2] == "PASS" else "high",
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys, os
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "G0 contexto/verificação de capítulos materializados."
}
manifest_path = evidence_dir / "MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G0] status=$status"
