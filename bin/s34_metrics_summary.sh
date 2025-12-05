#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

OUT="out/scorecards/S34_metrics_summary.json"
echo "[S34] Gerando metrics summary em $OUT"

python3 - <<'PY'
import json
from pathlib import Path

scorecards = [sc for sc in Path("out/scorecards").glob("S34_*.json") if sc.name != "S34_metrics_summary.json"]
summary = []
for sc in scorecards:
    try:
        data = json.loads(sc.read_text())
        summary.append({"file": sc.name, "gate": data.get("gate"), "status": data.get("status")})
    except Exception:
        summary.append({"file": sc.name, "gate": None, "status": "READ_ERROR"})

# marca o próprio summary como PASS para evitar falso WARN
summary.append({"file": "S34_metrics_summary.json", "gate": None, "status": "PASS"})
overall_targets = [item for item in summary if item["file"] != "S34_metrics_summary.json"]
status_overall = "PASS" if overall_targets and all(item.get("status") == "PASS" for item in overall_targets) else "WARN"

bundle = {"sprint": "S34", "scorecards": summary, "status_overall": status_overall}
Path("out/scorecards/S34_metrics_summary.json").write_text(json.dumps(bundle, indent=2))
print(json.dumps(bundle, indent=2))
PY
