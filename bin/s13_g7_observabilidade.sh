#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G7] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S13_G7_observabilidade.json"
SNAPSHOT_PATH="$ROOT_DIR/out/evidence/S13_G7/metrics_snapshot.json"

mkdir -p "$SCORECARD_DIR"

export PYTHONPATH="$ROOT_DIR"

python3 -m scripts.s13_metrics_snapshot >/dev/null

if [[ ! -f "$SNAPSHOT_PATH" ]]; then
  >&2 echo "[S13][G7] metrics_snapshot.json não encontrado."
  exit 1
fi

status="PASS"
python3 - <<'PY' "$SNAPSHOT_PATH" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

snapshot_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
health = snapshot.get("global_health", "CRITICAL")
if health == "OK":
    status = "PASS"
elif health == "WARN":
    status = "WARN"
else:
    status = "FAIL"
scorecard = {
    "gate": "S13_G7",
    "status": status,
    "global_health": health,
    "slis": snapshot.get("slis", {}),
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
if status == "FAIL":
    raise SystemExit("S13-G7 falhou. Consulte metrics_snapshot.json e risks_and_debts.md")
PY

printf '[S13][G7] Observabilidade consolidada. Scorecard em %s\n' "$SCORECARD_PATH"
