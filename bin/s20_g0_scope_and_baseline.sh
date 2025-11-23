#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G0_scope_and_baseline"
SCORECARD_PATH="$SCORECARD_DIR/S20_G0_scope_and_baseline.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

docs=(
  "$ROOT_DIR/docs/sprint_20_capitulo_1_contexto_objetivos.md"
  "$ROOT_DIR/docs/sprint_20_capitulo_2_gates_validacao.md"
  "$ROOT_DIR/docs/sprint_20_capitulo_3_arquitetura_filemap.md"
  "$ROOT_DIR/docs/sprint_20_capitulo_4_execucao.md"
)

docs_missing=()
for doc in "${docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    docs_missing+=("$doc")
  fi
done

todo_hits="$(rg --no-heading --line-number -w 'TODO|FIXME' "${docs[@]}" || true)"

commit_base="$(git -C "$ROOT_DIR" rev-parse HEAD)"
echo "$commit_base" > "$EVIDENCE_DIR/commit_base.txt"

build_status="pass"
test_status="pass"
M1=1

echo "[S20_G0] Rodando build do frontend..."
if ! (cd "$FRONTEND_DIR" && npm run build >"$EVIDENCE_DIR/frontend_build.log" 2>&1); then
  build_status="fail"
  M1=0
fi

echo "[S20_G0] Rodando testes do frontend..."
if ! (cd "$FRONTEND_DIR" && npm test >"$EVIDENCE_DIR/frontend_test.log" 2>&1); then
  test_status="fail"
  M1=0
fi

status="PASS"
details="Baseline ok."
if [[ ${#docs_missing[@]} -ne 0 ]]; then
  status="FAIL"
  details="Faltam documentos de capítulos da sprint."
elif [[ -n "$todo_hits" ]]; then
  status="FAIL"
  details="Encontrados TODO/FIXME nos capítulos materializados."
elif [[ $M1 -ne 1 ]]; then
  status="FAIL"
  details="Build ou testes do frontend falharam."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$commit_base" "$build_status" "$test_status" "$M1" "$todo_hits" "${docs_missing[@]}"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
commit_base = sys.argv[3]
build_status = sys.argv[4]
test_status = sys.argv[5]
M1 = int(sys.argv[6])
todo_hits = sys.argv[7]
docs_missing = sys.argv[8:]

scorecard = {
    "gate_id": "S20_G0_scope_and_baseline",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {
        "commit_base": commit_base,
        "docs_missing": docs_missing,
        "todo_hits": todo_hits,
        "build_status": build_status,
        "test_status": test_status,
        "M1": M1,
        "notes": [] if status == "PASS" else ["Revise detalhes acima antes de prosseguir para G1"],
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G0] FAIL - veja scorecard para detalhes.")
PY

echo "[S20_G0] Scorecard escrito em $SCORECARD_PATH"
