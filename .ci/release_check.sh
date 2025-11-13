#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T7_ci"
REPORT="$OUT/release_check_report.json"
mkdir -p "$OUT"
python3 - <<'PY' "$ROOT" "$REPORT"
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
report_path = Path(sys.argv[2])
checks = []
passed = True
checksum_files = sorted(root.glob('out/CHECKSUMS_D*.sha256'))
checksum_results = []
for chk in checksum_files:
    entries = []
    with chk.open() as fh:
        for line in fh:
            parts = line.strip().split(None, 1)
            if len(parts) != 2:
                continue
            expected, rel = parts
            file_path = root / rel
            if not file_path.exists():
                entries.append({'file': rel, 'status': 'missing'})
                passed = False
                continue
            actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
            ok = actual == expected
            if not ok:
                passed = False
            entries.append({'file': rel, 'expected': expected, 'actual': actual, 'status': 'passed' if ok else 'failed'})
    checksum_results.append({'file': str(chk), 'entries': entries})
checks.append({'type': 'checksums', 'results': checksum_results})
manifest_results = []
for manifest in sorted((root / 'out/evidence').glob('D*/MANIFEST.json')):
    manifest_results.append({'manifest': str(manifest), 'exists': manifest.exists()})
checks.append({'type': 'manifests', 'results': manifest_results})
report = {'passed': passed, 'checks': checks}
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
if not passed:
    sys.exit(1)
PY
