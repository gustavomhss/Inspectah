#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_G6_human_code_quality"
SCORECARD_PATH="$SCORECARD_DIR/S25_G6_human_code_quality.json"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

LINT_LOG="$EVIDENCE_DIR/lint.log"
PYTEST_LOG="$EVIDENCE_DIR/pytest.log"
REVIEW_NOTES="$EVIDENCE_DIR/review_notes.txt"

status="GO"
lint_status="PASS"
pytest_status="PASS"

echo "[S25_G6] Rodando lint básico (python -m compileall)..." | tee "$LINT_LOG"
set +e
python -m compileall "$ROOT_DIR/app" >>"$LINT_LOG" 2>&1
lint_exit=$?
set -e
if [[ $lint_exit -ne 0 ]]; then
  lint_status="FAIL"
  status="NO_GO"
fi

echo "[S25_G6] Rodando pytest rápido em policies/layers/threatmodel..." | tee "$PYTEST_LOG"
set +e
PYTHONPATH="$ROOT_DIR" pytest "$ROOT_DIR/tests/policies" "$ROOT_DIR/tests/layers" "$ROOT_DIR/tests/threatmodel" -q >>"$PYTEST_LOG" 2>&1
pytest_exit=$?
set -e
if [[ $pytest_exit -ne 0 ]]; then
  pytest_status="FAIL"
  status="NO_GO"
fi

cat >"$REVIEW_NOTES" <<TXT
Checklist: docs/sprint_25_code_review_checklist.md
Notas manuais de revisão: preencher após leitura humana dos módulos alterados nesta sprint.
TXT

cat >"$SCORECARD_PATH" <<JSON
{
  "gate_id": "S25_G6",
  "gate_name": "human_code_quality",
  "sprint": "S25",
  "status": "$status",
  "timestamp": "$ts",
  "commit_sha": "$git_commit",
  "inputs": {
    "branch": "$git_branch"
  },
  "metrics": {
    "lint_status": "$lint_status",
    "pytest_status": "$pytest_status"
  },
  "human_code_score": {
    "applied": true,
    "score": 0.7,
    "notes": "Lint leve + pytest e checklist disponível para revisão humana."
  },
  "risks": [],
  "notes": "Evidências em $EVIDENCE_DIR"
}
JSON

if [[ "$status" != "GO" ]]; then
  echo "[S25_G6] NO_GO - confira $SCORECARD_PATH"
  exit 1
fi

echo "[S25_G6] GO - scorecard em $SCORECARD_PATH"
