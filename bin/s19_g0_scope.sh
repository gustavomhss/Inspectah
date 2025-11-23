#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G0_scope"
SCORECARD_PATH="$SCORECARD_DIR/S19_G0_scope.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

docs=(
  "Sprint 19/Capitulo 1.md"
  "Sprint 19/Capitulo 2.md"
  "Sprint 19/Capitulo 3.md"
  "Sprint 19/Capitulo 4.md"
)

docs_missing=()
for doc in "${docs[@]}"; do
  if [[ ! -f "$ROOT_DIR/$doc" ]]; then
    docs_missing+=("$doc")
  fi
done

git -C "$ROOT_DIR" status --porcelain > "$EVIDENCE_DIR/git_status.txt"

python3 - <<'PY' "$ROOT_DIR" "$SCORECARD_PATH" "$EVIDENCE_DIR" "${docs_missing[@]}"
import json, sys, shlex
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])
docs_missing = sys.argv[4:]

allowed_prefixes = (
    "Sprint 19",
    "app/admin",
    "tests/admin",
    "frontend/inspectah-ui/src",
    "bin/s19",
    ".github/workflows/_s19",
    "docs/sprint_19",
    "out/scorecards",
    "out/evidence/S19",
)

status_lines = (root / "out" / "evidence" / "S19_G0_scope" / "git_status.txt").read_text(encoding="utf-8").splitlines()
files_in_scope, files_out_of_scope = [], []
for line in status_lines:
    if not line.strip():
        continue
    path = line[3:].strip().strip('"')
    normalized = path.replace("\\", "/")
    if any(normalized.startswith(prefix) for prefix in allowed_prefixes):
        files_in_scope.append(normalized)
    else:
        files_out_of_scope.append(normalized)

status = "PASS" if not docs_missing and not files_out_of_scope else "FAIL"
scorecard = {
    "gate_id": "S19_G0",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {
        "docs_ok": not docs_missing,
        "docs_missing": docs_missing,
        "files_in_scope": files_in_scope,
        "files_out_of_scope": files_out_of_scope,
    },
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G0] Falhou: revise docs ou escopo")
PY

echo "[S19_G0] OK - scorecard em $SCORECARD_PATH"
