#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out"
BUNDLE_DIR="$OUT_DIR/bundles"
BUNDLE_PATH="$BUNDLE_DIR/inspectah_s31_evidence_bundle.zip"

mkdir -p "$BUNDLE_DIR"

cd "$ROOT_DIR"
python3 - <<'PY' "$BUNDLE_PATH"
import sys
from pathlib import Path
import zipfile

bundle_path = Path(sys.argv[1])
root = bundle_path.parents[2]
targets = [
    root / "out" / "evidence",
    root / "out" / "scorecards",
]

with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for target in targets:
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(root))
print(f"[S31_G5] Bundle gerado em {bundle_path}")
PY

echo "[S31_G5] Bundle pronto em $BUNDLE_PATH"
