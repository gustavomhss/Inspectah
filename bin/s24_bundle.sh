#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence"
BUNDLES_DIR="${ROOT_DIR}/out/bundles"
STAGING_DIR="${BUNDLES_DIR}/S24_bundle"
MANIFEST_PATH="${STAGING_DIR}/bundle_manifest.json"
BUNDLE_ZIP="${BUNDLES_DIR}/inspectah_s24_evidence_bundle.zip"
BUNDLE_LOG="${EVIDENCE_DIR}/S24_bundle/bundle.log"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}/S24_bundle" "${BUNDLES_DIR}"
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/scorecards" "${STAGING_DIR}/evidence"

set +e
scorecard_files=($(find "${SCORECARDS_DIR}" -maxdepth 1 -type f -name "S24_*.json"))
set -e
if [ ${#scorecard_files[@]} -gt 0 ]; then
  cp "${scorecard_files[@]}" "${STAGING_DIR}/scorecards/" 2>/dev/null || true
fi

if compgen -G "${EVIDENCE_DIR}/S24*" >/dev/null; then
  cp -R ${EVIDENCE_DIR}/S24* "${STAGING_DIR}/evidence/" 2>/dev/null || true
fi

commit_hash="$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || echo "unknown")"

${PYTHON_BIN} - <<PY
import json, os, pathlib, time

staging = pathlib.Path("${STAGING_DIR}")
scorecards = sorted([p.name for p in (staging / "scorecards").glob("*.json")])
evidence_dirs = sorted([p.name for p in (staging / "evidence").glob("*") if p.is_dir()])
manifest = {
    "sprint": "S24",
    "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "commit": "${commit_hash}",
    "scorecards": scorecards,
    "evidence_dirs": evidence_dirs,
    "paths": {
        "scorecards": "scorecards/",
        "evidence": "evidence/",
    },
}
path = pathlib.Path("${MANIFEST_PATH}")
path.write_text(json.dumps(manifest, indent=2))
PY

cd "${STAGING_DIR}"
rm -f "${BUNDLE_ZIP}"
zip -qr "${BUNDLE_ZIP}" .

cat > "${BUNDLE_LOG}" <<LOG
S24 bundle generated at $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Bundle: ${BUNDLE_ZIP}
Manifest: ${MANIFEST_PATH}
Commit: ${commit_hash}
Included scorecards: $(ls "${STAGING_DIR}/scorecards" 2>/dev/null | tr '\n' ' ')
Included evidence dirs: $(ls "${STAGING_DIR}/evidence" 2>/dev/null | tr '\n' ' ')
LOG

echo "Bundle created at ${BUNDLE_ZIP}"
