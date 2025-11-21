#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G8"
SCORECARD_PATH="$SCORECARD_DIR/S14_G8_decision.json"
SUMMARY_PATH="$EVIDENCE_DIR/summary.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"
python3 -m scripts.s14_decision

if [[ ! -f "$SCORECARD_PATH" || ! -f "$SUMMARY_PATH" ]]; then
  >&2 echo "[S14_G8] Artefatos faltando (scorecard ou summary.md)"
  exit 1
fi

decision="$(python3 - <<'PY' "$SCORECARD_PATH"
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data.get("decision", "UNKNOWN"))
PY
)"

if [[ "$decision" != "GO" ]]; then
  >&2 echo "[S14_G8] Decisão = $decision (esperado GO)."
  exit 1
fi

echo "[S14_G8] Decisão GO registrada em $SCORECARD_PATH"
