#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G0"
SCORECARD_PATH="$SCORECARD_DIR/S12_G0_env_repo.json"
ENV_SNAPSHOT="$EVIDENCE_DIR/env_snapshot.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

BRANCH="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
ORIGIN="$(git -C "$ROOT_DIR" remote get-url origin 2>/dev/null || echo "unknown")"

ALLOWED_BRANCHES=(
  "s12_ingestao_continua_comunidade_v0"
  "main"
)

REQUIRED_DOCS=(
  "Sprint 12/Capitulo 1.md"
  "Sprint 12/Capitulo 2.md"
  "Sprint 12/Capitulo 3.md"
  "Sprint 12/Capitulo 4.md"
)

missing_docs=()
for doc in "${REQUIRED_DOCS[@]}"; do
  if [[ ! -f "$ROOT_DIR/$doc" ]]; then
    missing_docs+=("$doc")
  fi
done

status="PASS"
notes=()

if [[ "${#missing_docs[@]}" -gt 0 ]]; then
  status="FAIL"
  notes+=("Documentos faltando: ${missing_docs[*]}")
fi

is_allowed_branch="yes"
found=0
for allowed in "${ALLOWED_BRANCHES[@]}"; do
  if [[ "$BRANCH" == "$allowed" ]]; then
    found=1
    break
  fi
done
if [[ "$found" -eq 0 ]]; then
  is_allowed_branch="no"
  notes+=("Branch diferente do baseline da S12: $BRANCH")
fi

python3 - <<'PY' "$ENV_SNAPSHOT" "$BRANCH" "$ORIGIN" "$is_allowed_branch" "${ALLOWED_BRANCHES[@]}" "${REQUIRED_DOCS[@]}" "${missing_docs[@]}"
import json
import sys
from pathlib import Path

env_path = Path(sys.argv[1])
branch = sys.argv[2]
origin = sys.argv[3]
is_allowed = sys.argv[4]
allowed_branches = sys.argv[5:7]
required_docs = sys.argv[7:11]
missing_docs = sys.argv[11:]
payload = {
    "branch": branch,
    "is_allowed_branch": is_allowed,
    "allowed_branches": allowed_branches,
    "origin": origin,
    "required_docs": required_docs,
    "missing_docs": missing_docs,
}
env_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
PY

python3 - <<'PY' "$SCORECARD_PATH" "$status" "${notes[@]}"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
notes = sys.argv[3:]
scorecard = {
    "gate": "S12-G0",
    "status": status,
    "details": {
        "notes": notes,
    },
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
if status != "PASS":
    raise SystemExit("S12-G0 falhou. Consulte o snapshot em evidências.")
PY

echo "S12-G0 OK. Scorecard: $SCORECARD_PATH"
