#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T2_unit/evidence_vault"
PAYLOAD="$ROOT/tests/fixtures/unit/evidence_vault/sample_payload.json"
METADATA="$ROOT/tests/fixtures/unit/evidence_vault/sample_metadata.json"
python3 "$ROOT/scripts/evidence_vault.py" \
  --payload "$PAYLOAD" \
  --metadata "$METADATA" \
  --out-dir "$EVID_DIR"
python3 - <<'PY' "$EVID_DIR"
import hashlib, json, os, sys
root = sys.argv[1]
files = []
for dirpath, _, filenames in os.walk(root):
    for name in sorted(filenames):
        path = os.path.join(dirpath, name)
        rel = os.path.relpath(path, os.path.join(os.path.dirname(root), '..'))
        with open(path, 'rb') as fh:
            data = fh.read()
        files.append({
            'path': rel,
            'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data)
        })
manifest_path = os.path.join(root, 'MANIFEST.json')
with open(manifest_path, 'w', encoding='utf-8') as fh:
    json.dump({'files': files}, fh, indent=2)
PY
echo "Evidence Vault smoke completed. Artifacts in $EVID_DIR"
