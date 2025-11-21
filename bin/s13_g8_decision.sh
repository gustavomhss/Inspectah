#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G8] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_PATH="$ROOT_DIR/out/scorecards/S13_G8_decision.json"
EVIDENCE_SUMMARY="$ROOT_DIR/out/evidence/S13_G8/summary.md"

mkdir -p "$ROOT_DIR/out/scorecards"

export PYTHONPATH="$ROOT_DIR"

python3 -m scripts.s13_decision >/dev/null

if [[ ! -f "$SCORECARD_PATH" ]]; then
  >&2 echo "[S13][G8] Scorecard não foi gerado."
  exit 1
fi

python3 - <<'PY' "$SCORECARD_PATH"
import json
import sys
from pathlib import Path

scorecard = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
status = scorecard.get("status", "FAIL")
if status != "PASS":
    raise SystemExit("S13-G8 falhou. Consulte o scorecard e summary.md")
PY

if [[ ! -f "$EVIDENCE_SUMMARY" ]]; then
  >&2 echo "[S13][G8] summary.md não encontrado."
  exit 1
fi

echo "[S13][G8] Decisão gerada. Scorecard: $SCORECARD_PATH"
