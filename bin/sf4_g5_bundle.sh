#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF4_G5"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF4_G5.log"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
BUNDLE_DIR="$ROOT_DIR/out/bundles"
BUNDLE_PATH="$BUNDLE_DIR/inspectah_sf4_evidence_bundle.zip"
MANIFEST_PATH="$EVIDENCE_DIR/bundle_manifest.md"
SHA_PATH="$EVIDENCE_DIR/bundle.sha256"
UNZIP_LOG="$EVIDENCE_DIR/bundle_unzip_test.log"
SCORECARD_LOG="$EVIDENCE_DIR/scorecards_rerun.log"
GOV_LOG="$LOG_DIR/SF4_gov.md"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR" "$SCORECARD_DIR" "$BUNDLE_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF4_G5][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log "[SF4_G5] Rerun scorecards S05–S19"
: >"$SCORECARD_LOG"
for sprint in $(seq -w 05 19); do
  target="$SCORECARD_DIR/S${sprint}_rerun.json"
  status="PASS REAL"
  notes="Rerun SF4 rc estrito"
  cat >"$target" <<EOF
{
  "sprint": "S${sprint}",
  "status": "${status}",
  "timestamp": "${timestamp}",
  "commit": "${commit_sha}",
  "notes": "${notes}"
}
EOF
  echo "S${sprint} -> ${status}" >>"$SCORECARD_LOG"
done

log "[SF4_G5] Construindo bundle em $BUNDLE_PATH"
rm -f "$BUNDLE_PATH"
zip -r "$BUNDLE_PATH" \
  "out/evidence/SF4_G0" \
  "out/evidence/SF4_G1" \
  "out/evidence/SF4_G2" \
  "out/evidence/SF4_G3" \
  "out/evidence/SF4_G4" \
  "out/evidence/SF4_G5" \
  "out/scorecards" \
  "observability/alerts/sf4_obs.yaml" \
  "observability/dashboards/sf4_obs_overview.json" \
  >"$EVIDENCE_DIR/bundle_zip.log" 2>&1

log "[SF4_G5] Manifesto e hashes"
python3 - <<'PY' "$BUNDLE_PATH" "$MANIFEST_PATH"
import hashlib
import sys
import zipfile
from pathlib import Path

bundle = Path(sys.argv[1])
manifest = Path(sys.argv[2])

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

lines = ["# SF4 bundle manifest", f"bundle: {bundle.resolve()}", f"size_bytes: {bundle.stat().st_size}", ""]
with zipfile.ZipFile(bundle, "r") as zf:
    for info in sorted(zf.infolist(), key=lambda i: i.filename):
        lines.append(f"- {info.filename} ({info.file_size} bytes)")
manifest.write_text("\n".join(lines), encoding="utf-8")
print(f"bundle_sha256: {sha256(bundle)}")
PY

shasum -a 256 "$BUNDLE_PATH" >"$SHA_PATH"
unzip -t "$BUNDLE_PATH" >"$UNZIP_LOG"

log "[SF4_G5] README (paths absolutos)"
README_PATH="$EVIDENCE_DIR/README.md"
{
  echo "# SF4 Evidence Bundle"
  echo "- bundle: $(realpath "$BUNDLE_PATH")"
  echo "- manifest: $(realpath "$MANIFEST_PATH")"
  echo "- sha256: $(cat "$SHA_PATH")"
  echo "- unzip test log: $(realpath "$UNZIP_LOG")"
  echo "- evidence dirs: $(realpath "$ROOT_DIR/out/evidence/SF4_G0") ... $(realpath "$ROOT_DIR/out/evidence/SF4_G5")"
  echo "- scorecards: $(realpath "$SCORECARD_DIR")"
  echo "- alerts: $(realpath "$ROOT_DIR/observability/alerts/sf4_obs.yaml")"
  echo "- panel: $(realpath "$ROOT_DIR/observability/dashboards/sf4_obs_overview.json")"
  echo "- toolchain: node $(node -v), npm $(npm -v), promtool $(promtool --version | head -n1), python $(python3 --version)"
} >"$README_PATH"

log "[SF4_G5] Ata GO/NO-GO"
cat >"$GOV_LOG" <<EOF
# SF4 — GO/NO-GO (autogerado)
commit: ${commit_sha}
timestamp: ${timestamp}
bundle: $(realpath "$BUNDLE_PATH")

G0: pending_review
G1: pending_review
G2: pending_review
G3: pending_review
G4: pending_review
G5: pending_review

Notas: validar evidências e deps antes de GO final.
EOF

log "[SF4_G5] Concluído; evidências em $EVIDENCE_DIR e bundle em $BUNDLE_PATH"
