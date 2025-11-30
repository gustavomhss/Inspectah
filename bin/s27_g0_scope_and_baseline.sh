#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S27_G0_scope_and_baseline"
SCORECARD_PATH="$SCORECARD_DIR/S27_G0_scope_and_baseline.json"
LOG_PATH="$EVIDENCE_DIR/g0_scope_and_baseline.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

EXPECTED_DOCS=(
  "$ROOT_DIR/docs/sprint_27_cap_1_contexto.md"
  "$ROOT_DIR/docs/sprint_27_cap_2_gates_e_metricas.md"
  "$ROOT_DIR/docs/sprint_27_cap_3_arquitetura_e_filemap.md"
  "$ROOT_DIR/docs/sprint_27_cap_4_execucao_e_evidencias.md"
)

EXPECTED_DIRS=(
  "$ROOT_DIR/frontend/inspectah-ui/src/ui/admin"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources"
  "$ROOT_DIR/out/evidence"
  "$ROOT_DIR/out/scorecards"
)

docs_missing=()
for doc in "${EXPECTED_DOCS[@]}"; do
  if [[ ! -f "$doc" ]]; then
    docs_missing+=("$doc")
  fi
done

dirs_missing=()
for dir in "${EXPECTED_DIRS[@]}"; do
  if [[ ! -d "$dir" ]]; then
    dirs_missing+=("$dir")
  fi
done

frontend_deps_ok=false
if [[ -d "$ROOT_DIR/frontend/inspectah-ui/node_modules" ]]; then
  frontend_deps_ok=true
fi

backend_deps_ok=false
if [[ -d "$ROOT_DIR/.venv" ]] || [[ -f "$ROOT_DIR/poetry.lock" ]]; then
  backend_deps_ok=true
fi

design_system_skeleton_present=$([[ -d "$ROOT_DIR/frontend/inspectah-ui/src/ui/admin" ]] && echo true || echo false)
sources_console_skeleton_present=$([[ -d "$ROOT_DIR/frontend/inspectah-ui/src/features/sources" ]] && echo true || echo false)
docs_present=$([[ ${#docs_missing[@]} -eq 0 ]] && echo true || echo false)

STATUS="GO"
if [[ "$docs_present" != true || "$frontend_deps_ok" != true || "$backend_deps_ok" != true || "$design_system_skeleton_present" != true || "$sources_console_skeleton_present" != true ]]; then
  STATUS="NO_GO"
fi

{
  echo "[S27_G0] docs_present=$docs_present"
  echo "[S27_G0] frontend_deps_ok=$frontend_deps_ok"
  echo "[S27_G0] backend_deps_ok=$backend_deps_ok"
  echo "[S27_G0] design_system_skeleton_present=$design_system_skeleton_present"
  echo "[S27_G0] sources_console_skeleton_present=$sources_console_skeleton_present"
  if [[ ${#docs_missing[@]} -gt 0 ]]; then
    echo "[S27_G0] Docs faltantes:"
    printf '%s\n' "${docs_missing[@]}"
  fi
  if [[ ${#dirs_missing[@]} -gt 0 ]]; then
    echo "[S27_G0] Diretórios faltantes:"
    printf '%s\n' "${dirs_missing[@]}"
  fi
} | tee "$LOG_PATH"

git -C "$ROOT_DIR" status -sb > "$EVIDENCE_DIR/git_status.txt"

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$docs_present" "$frontend_deps_ok" "$backend_deps_ok" "$design_system_skeleton_present" "$sources_console_skeleton_present"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
docs_present = sys.argv[3] == "true"
frontend_deps_ok = sys.argv[4] == "true"
backend_deps_ok = sys.argv[5] == "true"
design_system_skeleton_present = sys.argv[6] == "true"
sources_console_skeleton_present = sys.argv[7] == "true"

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S27_G0_scope_and_baseline",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "docs_present": docs_present,
        "frontend_deps_ok": frontend_deps_ok,
        "backend_deps_ok": backend_deps_ok,
        "design_system_skeleton_present": design_system_skeleton_present,
        "sources_console_skeleton_present": sources_console_skeleton_present,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S27_G0] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
