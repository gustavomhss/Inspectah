#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G0] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S13_G0"
SCORECARD_PATH="$SCORECARD_DIR/S13_G0_env_repo.json"
SNAPSHOT_PATH="$EVIDENCE_DIR/env_snapshot.json"
S12_DECISION_PATH="$ROOT_DIR/out/scorecards/S12_G8_decision.json"
CONFIG_PATH="$ROOT_DIR/config/s13_pilotos.yml"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

BRANCH="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
ORIGIN="$(git -C "$ROOT_DIR" remote get-url origin 2>/dev/null || echo "unknown")"

python3 - <<'PY' "$ROOT_DIR" "$SCORECARD_PATH" "$SNAPSHOT_PATH" "$S12_DECISION_PATH" "$CONFIG_PATH" "$BRANCH" "$ORIGIN" "Sprint 13/Capitulo 1.md" "Sprint 13/Capitulo 2.md" "Sprint 13/Capitulo 3.md" "Sprint 13/Capitulo 4.md"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
snapshot_path = Path(sys.argv[3])
s12_decision_path = Path(sys.argv[4])
config_path = Path(sys.argv[5])
branch = sys.argv[6]
origin = sys.argv[7]
required_docs = [root / path for path in sys.argv[8:]]

checks = {}
status = "PASS"

allowed_branches = {"main", "s13_piloto_multi_dominio_v0"}
branch_ok = branch in allowed_branches
checks["branch"] = {"value": branch, "valid": branch_ok}
if not branch_ok:
    status = "FAIL"

origin_ok = "inspectah" in origin.lower()
checks["origin"] = {"value": origin, "valid": origin_ok}
if not origin_ok:
    status = "FAIL"

missing_docs = [str(path.relative_to(root)) for path in required_docs if not path.exists()]
checks["docs"] = {"missing": missing_docs, "valid": not missing_docs}
if missing_docs:
    status = "FAIL"

config_ok = config_path.exists()
checks["config"] = {"path": str(config_path), "valid": config_ok}
if not config_ok:
    status = "FAIL"

s12_ok = False
s12_reason = "scorecard inexistente"
if s12_decision_path.exists():
    try:
        s12_data = json.loads(s12_decision_path.read_text(encoding="utf-8"))
        decision = s12_data.get("decision") or s12_data.get("details", {}).get("decision")
        s12_ok = str(decision).upper() == "GO"
        s12_reason = f"decision={decision}"
    except Exception as exc:  # pragma: no cover
        s12_reason = f"erro ao ler scorecard: {exc}"
checks["s12_go"] = {"reason": s12_reason, "valid": s12_ok}
if not s12_ok:
    status = "FAIL"

snapshot = {
    "root": str(root),
    "branch": branch,
    "origin": origin,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")

payload = {
    "gate": "S13_G0",
    "status": status,
    "ts": snapshot["timestamp"],
    "checks": checks,
}
scorecard_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

if status != "PASS":
    raise SystemExit("S13-G0 falhou. Consulte out/evidence/S13_G0.")
PY

printf '[S13][G0] Ambiente validado. Scorecard em %s\n' "$SCORECARD_PATH"
