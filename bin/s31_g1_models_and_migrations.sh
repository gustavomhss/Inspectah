#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S31_G1_models_and_migrations"
SCORECARD_PATH="$SCORECARD_DIR/S31_G1_models_and_migrations.json"
LOG_PATH="$EVIDENCE_DIR/g1_models_and_migrations.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$LOG_PATH"
import importlib
import sys
from pathlib import Path

log_path = Path(sys.argv[1])
modules = [
    "migrations.versions.0032_s31_providers",
    "migrations.versions.0033_s31_profiles_seed",
]
log_lines = []
for mod_name in modules:
    mod = importlib.import_module(mod_name)
    if hasattr(mod, "apply_migration"):
        mod.apply_migration()  # type: ignore[attr-defined]
        log_lines.append(f"[S31_G1] applied {mod_name}\n")
    if hasattr(mod, "seed"):
        mod.seed()  # type: ignore[attr-defined]
        log_lines.append(f"[S31_G1] seeded via {mod_name}\n")
log_path.write_text("".join(log_lines), encoding="utf-8")
PY

STATUS="GO"

{
  echo "[S31_G1] migrations applied and seeds executed"
  python3 - <<'PY'
import importlib
import json
from pathlib import Path

db_path = Path("out/databases/s31_providers.sqlite")
mod = importlib.import_module("migrations.versions.0032_s31_providers")
info = mod.verify_schema(db_path)
print(json.dumps({"db": str(db_path), "tables": info.get("tables", 0)}, indent=2))
PY
} | tee "$LOG_PATH"

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S31_G1_models_and_migrations",
    "timestamp": timestamp,
    "status": status,
    "metrics": {"db": "out/databases/s31_providers.sqlite", "seeded": True},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S31_G1] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
