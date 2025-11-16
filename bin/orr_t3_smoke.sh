#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T3_property"
REPORT="$EVID_DIR/preliminary.json"
mkdir -p "$EVID_DIR"

python3 - "$REPORT" <<'PY'
import hashlib
import json
from datetime import datetime
from pathlib import Path
import sys

report_path = Path(sys.argv[1])
vault_dir = Path("out/evidence/T2_unit/evidence_vault")
manifests = list(vault_dir.glob("*/manifest.json"))
if not manifests:
    raise SystemExit("no manifests to evaluate")
manifest_path = manifests[0]
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

payload_ok = manifest["fetched_payload_sha256"] == manifest["hashes"]["payload_sha256"]

canon = json.loads(json.dumps(manifest))
canon["hashes"]["manifest_sha256"] = ""
canonical_bytes = json.dumps(canon, sort_keys=True).encode("utf-8")
manifest_hash = hashlib.sha256(canonical_bytes).hexdigest()
manifest_ok = manifest_hash == manifest["hashes"]["manifest_sha256"]

def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
ordered = parse(manifest["event_time"]) <= parse(manifest["observed_at"]) <= parse(manifest["indexed_at"])

result = {
    "item_id": manifest["item_id"],
    "checks": {
        "payload_hash_match": payload_ok,
        "manifest_hash_match": manifest_ok,
        "temporal_order": ordered
    }
}
report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
PY

echo "T3 preliminary checks written to $REPORT"
