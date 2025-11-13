#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T2_unit"
SCORECARD="$OUT_DIR/scorecards/T2_unit.json"
mkdir -p "$EVID_DIR" "$OUT_DIR/scorecards"

# Field Designer dry-run (baseline contract)
FIELDS="$ROOT/tests/fixtures/unit/field_designer/example_fields.json"
PAYLOAD="$ROOT/tests/fixtures/unit/field_designer/example_payload.json"
FD_OUTPUT="$EVID_DIR/field_designer_dryrun.json"
python3 "$ROOT/scripts/field_designer_validate.py" --fields "$FIELDS" --payload "$PAYLOAD" --out "$FD_OUTPUT"
jq -e . "$FD_OUTPUT" >/dev/null

# Evidence Vault determinism
bin/orr_vault_smoke.sh

# API smoke exercising contracts
bin/orr_api_smoke.sh

python3 - "$EVID_DIR" "$SCORECARD" <<'PY'
import datetime, hashlib, json, os, sys
root, scorecard = sys.argv[1:3]
files = []
targets = [
    "field_designer_dryrun.json",
    "api_smoke.json",
    "api_smoke.log",
]
vault_manifest = os.path.join(root, "evidence_vault", "MANIFEST.json")
if os.path.exists(vault_manifest):
    targets.append(os.path.relpath(vault_manifest, root))

for rel in targets:
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        continue
    with open(path, "rb") as fh:
        data = fh.read()
    files.append({
        "path": os.path.relpath(path, os.path.join(root, "..")),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    })
manifest_path = os.path.join(root, "MANIFEST.json")
with open(manifest_path, "w", encoding="utf-8") as fh:
    json.dump({"files": files}, fh, indent=2)

now = datetime.datetime.utcnow().isoformat() + "Z"
with open(scorecard, "w", encoding="utf-8") as fh:
    json.dump({
        "gate": "T2",
        "version": "1.1",
        "started_at": now,
        "finished_at": now,
        "passed": True,
        "failures": [],
        "metrics": {},
        "artifacts": [
            {"path": "out/evidence/T2_unit/field_designer_dryrun.json"},
            {"path": "out/evidence/T2_unit/evidence_vault/MANIFEST.json"},
            {"path": "out/evidence/T2_unit/api_smoke.json"},
            {"path": "out/evidence/T2_unit/MANIFEST.json"}
        ],
        "notes": "Field Designer + Evidence Vault + API smoke validated"
    }, fh, indent=2)
PY

echo "T2 reinforced: field designer, evidence vault, and API smoke completed."
