#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence"
STAGING_DIR="${ROOT_DIR}/out/bundles/S27_bundle"
BUNDLE_ZIP="${ROOT_DIR}/out/bundles/inspectah_s27_evidence_bundle.zip"
MANIFEST_PATH="${STAGING_DIR}/bundle_manifest.json"
BUNDLE_LOG="${EVIDENCE_DIR}/S27_bundle/bundle.log"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}/S27_bundle" "${ROOT_DIR}/out/bundles"
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/scorecards" "${STAGING_DIR}/evidence"

echo "[S27_BUNDLE] Rodando gates G0-G4..."
set +e
cd "${ROOT_DIR}"
bash bin/s27_g0_scope_and_baseline.sh && \
bash bin/s27_g1_models_and_invariants.sh && \
bash bin/s27_g2_backend_ingestion_ops.sh && \
bash bin/s27_g3_frontend_sources_console_ops.sh && \
bash bin/s27_g4_audit_logs_evidence.sh
GATES_EXIT=$?
set -e

if [[ $GATES_EXIT -ne 0 ]]; then
  echo "[S27_BUNDLE] Falha em algum gate, abortando bundle."
  exit 1
fi

if compgen -G "${SCORECARDS_DIR}/S27_*.json" >/dev/null; then
  cp "${SCORECARDS_DIR}"/S27_*.json "${STAGING_DIR}/scorecards/" 2>/dev/null || true
fi

if compgen -G "${EVIDENCE_DIR}/S27*" >/dev/null; then
  cp -R ${EVIDENCE_DIR}/S27* "${STAGING_DIR}/evidence/" 2>/dev/null || true
fi

commit_hash="$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || echo "unknown")"

python3 - <<PY
import json, pathlib, time

staging = pathlib.Path("${STAGING_DIR}")
scorecards = sorted([p.name for p in (staging / "scorecards").glob("*.json")])
evidence_dirs = sorted([p.name for p in (staging / "evidence").glob("*") if p.is_dir()])
manifest = {
    "sprint": "S27",
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
path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

cd "${STAGING_DIR}"
rm -f "${BUNDLE_ZIP}"
zip -qr "${BUNDLE_ZIP}" .

cat > "${BUNDLE_LOG}" <<LOG
S27 bundle generated at $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Bundle: ${BUNDLE_ZIP}
Manifest: ${MANIFEST_PATH}
Commit: ${commit_hash}
Included scorecards: $(ls "${STAGING_DIR}/scorecards" 2>/dev/null | tr '\n' ' ')
Included evidence dirs: $(ls "${STAGING_DIR}/evidence" 2>/dev/null | tr '\n' ' ')
LOG

echo "[S27_BUNDLE] Bundle created at ${BUNDLE_ZIP}"
