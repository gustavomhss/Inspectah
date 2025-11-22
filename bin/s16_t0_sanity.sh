#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S16_T0] Rode o script a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T0_sanity"
SCORECARD_PATH="$SCORECARD_DIR/S16_T0_sanity.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

echo "[S16_T0] Validando baseline da S15 e ambiente..."
set +e
PYTHONPATH="$ROOT_DIR" bash "$ROOT_DIR/bin/s15_all_gates.sh" > "$EVIDENCE_DIR/s15_all_gates.log" 2>&1
S15_STATUS=$?
set -e

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH" "$S15_STATUS"
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
S15_STATUS = int(sys.argv[3])

python_version = platform.python_version()

def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=EVIDENCE_DIR.parent.parent).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"

status = "PASS" if S15_STATUS == 0 else "FAIL"
decision = "GO" if status == "PASS" else "NO_GO"
notes = []
if status == "FAIL":
    notes.append("Falha ao revalidar S15; consulte s15_all_gates.log")

scorecard = {
    "gate": "S16_T0_sanity",
    "status": status,
    "decision": decision,
    "inputs": {"python": python_version, "git_head": _git_head()},
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}

SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
manifest = {
    "logs": ["s15_all_gates.log"],
    "status": status,
}
(EVIDENCE_DIR / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T0] Falhou; consulte evidências.")
PY

echo "[S16_T0] OK. Scorecard em $SCORECARD_PATH"
