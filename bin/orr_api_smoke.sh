#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T2_unit"
LOG_FILE="$EVID_DIR/api_smoke.log"
mkdir -p "$EVID_DIR"

python3 - "$EVID_DIR" "$LOG_FILE" "$ROOT" <<'PY'
import importlib.util
import json
import sys
from pathlib import Path
import time

evid_dir = Path(sys.argv[1])
log_file = Path(sys.argv[2])
root = Path(sys.argv[3])
module_path = root / "scripts/api_server.py"
spec = importlib.util.spec_from_file_location("inspectah_api_server", module_path)
api_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_server)  # type: ignore

fields_payload = json.loads((root / "tests/fixtures/unit/field_designer/example_fields.json").read_text(encoding="utf-8"))
report = api_server.run_smoke_sequence(fields_payload)
report["captured_at"] = time.time()
(evid_dir / "api_smoke.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
log_file.write_text("API smoke executed via shared contract logic\n", encoding="utf-8")
PY

echo "API smoke completed (contract simulation). Log written to $LOG_FILE"
