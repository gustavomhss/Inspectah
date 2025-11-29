#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_G0_scope_and_baseline"
SCORECARD_PATH="$SCORECARD_DIR/S25_G0_scope_and_baseline.json"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # usa o ambiente virtual local quando disponível
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

EXPECTED_DOCS=(
  "$ROOT_DIR/Sprint 25/Capitulo 0.md"
  "$ROOT_DIR/Sprint 25/Capitulo 0-A.md"
  "$ROOT_DIR/Sprint 25/Capitulo 0.5.md"
  "$ROOT_DIR/Sprint 25/Capitulo 0.5-A.md"
  "$ROOT_DIR/Sprint 25/Capitulo 1.md"
  "$ROOT_DIR/Sprint 25/Capitulo 2.md"
  "$ROOT_DIR/Sprint 25/Capitulo 7.md"
)

EXPECTED_DIRS=(
  "$ROOT_DIR/app/truth"
  "$ROOT_DIR/app/policies"
  "$ROOT_DIR/app/layers"
  "$ROOT_DIR/app/context"
  "$ROOT_DIR/app/threatmodel"
  "$ROOT_DIR/app/agents"
  "$ROOT_DIR/app/incidents"
  "$ROOT_DIR/app/api"
  "$ROOT_DIR/configs/promotion_policies"
  "$ROOT_DIR/configs/threatmodel"
  "$ROOT_DIR/data/s25/golden_sets/politics_case_01"
  "$ROOT_DIR/data/s25/golden_sets/corporate_case_01"
  "$ROOT_DIR/data/s25/golden_sets/climate_case_01"
  "$ROOT_DIR/data/s25/golden_sets/science_case_01"
  "$ROOT_DIR/data/s25/golden_sets/gossip_case_01"
  "$ROOT_DIR/out/scorecards"
  "$ROOT_DIR/out/evidence"
  "$ROOT_DIR/out/bundles"
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

SMOKE_LOG="$EVIDENCE_DIR/smoke_pytest.log"
SMOKE_STATUS="pass"
echo "[S25_G0] Rodando smoke pytest (contrato S23/S24/S25)..." | tee "$SMOKE_LOG"
if ! (cd "$ROOT_DIR" && PYTHONPATH=. pytest -q tests/integration/test_s23_s24_s25_contracts.py >>"$SMOKE_LOG" 2>&1); then
  SMOKE_STATUS="fail"
fi

git -C "$ROOT_DIR" status -sb > "$EVIDENCE_DIR/git_status.txt"
BRANCH="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"
COMMIT_SHA="$(git -C "$ROOT_DIR" rev-parse HEAD)"

STATUS="GO"
if [[ ${#docs_missing[@]} -gt 0 ]]; then
  STATUS="NO_GO"
fi
if [[ ${#dirs_missing[@]} -gt 0 ]]; then
  STATUS="NO_GO"
fi
if [[ "$SMOKE_STATUS" != "pass" ]]; then
  STATUS="NO_GO"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$COMMIT_SHA" "$BRANCH" "$SMOKE_STATUS" -- "${docs_missing[@]}" --DIRS-- "${dirs_missing[@]}"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
commit_sha = sys.argv[3]
branch = sys.argv[4]
smoke_status = sys.argv[5]

args_iter = sys.argv[6:]
docs_missing = []
dirs_missing = []
mode = "docs"
for item in args_iter:
    if item == "--":
        continue
    if item == "--DIRS--":
        mode = "dirs"
        continue
    if mode == "docs":
        docs_missing.append(item)
    else:
        dirs_missing.append(item)

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

metrics = {
    "M.functional.docs_present": len(docs_missing) == 0,
    "M.operational.structure_ok": len(dirs_missing) == 0,
    "M.functional.smoke_tests_pass": smoke_status == "pass",
}

scorecard = {
    "gate": "S25_G0_scope_and_baseline",
    "status": status,
    "timestamp": timestamp,
    "commit_sha": commit_sha,
    "inputs": {
        "branch": branch,
        "env": "local",
    },
    "metrics": metrics,
    "human_code_score": {
        "applied": True,
        "score": 0.5,
        "notes": "G0 cheque de legibilidade: estrutura mínima e docs no lugar.",
    },
    "risks": [
        {"id": "R-G0-MISSING-DOCS", "severity": "high", "description": "Docs críticos ausentes"}
        if docs_missing
        else {"id": "R-G0-NO-KNOWN", "severity": "low", "description": "Nenhum risco identificado no gate G0"}
    ],
    "notes": "; ".join(
        note
        for note in [
            f"docs_missing: {docs_missing}" if docs_missing else "",
            f"dirs_missing: {dirs_missing}" if dirs_missing else "",
            f"smoke_status: {smoke_status}",
        ]
        if note
    ),
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if status != "GO":
    print("[S25_G0] NO_GO - cheque scorecard e evidências.", file=sys.stderr)
    sys.exit(1)

print(f"[S25_G0] Scorecard gerado em {scorecard_path}")
PY
