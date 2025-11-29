#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

ALLOWED_BRANCHES=("main" "s14_hardening_truth_kernel_v0")
EXPECTED_ORIGIN="github.com:gustavomhss/Inspectah.git"

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G0"
SCORECARD_PATH="$SCORECARD_DIR/S14_G0_env_repo.json"
SNAPSHOT_PATH="$EVIDENCE_DIR/env_snapshot.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

BRANCH="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
ORIGIN_URL="$(git -C "$ROOT_DIR" remote get-url origin 2>/dev/null || echo "unknown")"
REQUIRED_DOCS=(
  "Sprint 14/Capitulo 1.md"
  "Sprint 14/Capitulo 2.md"
  "Sprint 14/Capitulo 3.md"
  "Sprint 14/Capitulo 4.md"
)

status="PASS"
reasons=()
notes=()

is_allowed=0
for allowed in "${ALLOWED_BRANCHES[@]}"; do
  if [[ "$BRANCH" == "$allowed" ]]; then
    is_allowed=1
    break
  fi
done
if [[ "$is_allowed" -eq 0 ]]; then
  notes+=("Branch diferente das de baseline da S14: $BRANCH (permitidas: ${ALLOWED_BRANCHES[*]})")
fi

if [[ "$ORIGIN_URL" != *"$EXPECTED_ORIGIN" ]]; then
  notes+=("Origin inesperado: $ORIGIN_URL (esperado conter $EXPECTED_ORIGIN)")
fi

for doc in "${REQUIRED_DOCS[@]}"; do
  if [[ ! -f "$ROOT_DIR/$doc" ]]; then
    status="FAIL"
    reasons+=("Documento ausente: $doc")
  fi
done

S12_SCORECARD="$ROOT_DIR/out/scorecards/S12_G8_decision.json"
S13_SCORECARD="$ROOT_DIR/out/scorecards/S13_G8_decision.json"

if [[ ! -f "$S12_SCORECARD" ]]; then
  status="FAIL"
  reasons+=("Scorecard S12_G8_decision.json não encontrado")
fi
if [[ ! -f "$S13_SCORECARD" ]]; then
  status="FAIL"
  reasons+=("Scorecard S13_G8_decision.json não encontrado")
fi

decision_s12="UNKNOWN"
decision_s13="UNKNOWN"
if [[ -f "$S12_SCORECARD" ]]; then
  decision_s12="$(python3 - <<'PY' "$S12_SCORECARD"
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data.get("decision", "UNKNOWN"))
PY
)"
  if [[ "$decision_s12" != "GO" ]]; then
    status="FAIL"
    reasons+=("S12 decisão não é GO (atual: $decision_s12)")
  fi
fi
if [[ -f "$S13_SCORECARD" ]]; then
  decision_s13="$(python3 - <<'PY' "$S13_SCORECARD"
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data.get("decision", "UNKNOWN"))
PY
)"
  if [[ "$decision_s13" != "GO" ]]; then
    status="FAIL"
    reasons+=("S13 decisão não é GO (atual: $decision_s13)")
  fi
fi

python3 - <<'PY' "$SNAPSHOT_PATH" "$BRANCH" "$ORIGIN_URL" "${REQUIRED_DOCS[@]}" "$S12_SCORECARD" "$S13_SCORECARD" "$decision_s12" "$decision_s13" "${ALLOWED_BRANCHES[@]}" "--notes--" "${notes[@]}"
import json, sys
from pathlib import Path

env_path = Path(sys.argv[1])
branch = sys.argv[2]
origin = sys.argv[3]
docs = sys.argv[4:8]
s12_scorecard = sys.argv[8]
s13_scorecard = sys.argv[9]
decision_s12 = sys.argv[10]
decision_s13 = sys.argv[11]
rest = sys.argv[12:]
notes: list[str] = []
if "--notes--" in rest:
    split = rest.index("--notes--")
    allowed = rest[:split]
    notes = rest[split + 1 :]
else:
    allowed = rest

payload = {
    "branch": branch,
    "origin": origin,
    "docs_present": docs,
    "s12_scorecard": s12_scorecard,
    "s13_scorecard": s13_scorecard,
    "decision_s12": decision_s12,
    "decision_s13": decision_s13,
    "allowed_branches": allowed,
    "notes": notes,
}
env_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$SCORECARD_PATH" "$status" "${reasons[@]}" "--notes--" "${notes[@]}"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
parts = sys.argv[3:]
notes = []
if "--notes--" in parts:
    idx = parts.index("--notes--")
    reasons = parts[:idx]
    notes = parts[idx + 1 :]
else:
    reasons = parts
scorecard = {
    "gate": "S14_G0",
    "status": status,
    "reasons": reasons,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("S14_G0 falhou; verifique razões.")
PY

echo "[S14_G0] OK. Scorecard: $SCORECARD_PATH"
