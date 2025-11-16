#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G6_bundle_repro.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G6_bundle_repro"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

BUILD_LOG="$EVIDENCE_DIR/build_bundle.json"
VERIFY_LOG="$EVIDENCE_DIR/verify_bundle.json"
status="PASS"

if ! "$REPO_ROOT/bin/inspectah_s6_build_bundle.sh" "$DOMAIN" | tee "$BUILD_LOG"; then
  status="FAIL"
fi
if ! "$REPO_ROOT/bin/inspectah_s6_verify_bundle.sh" | tee "$VERIFY_LOG"; then
  status="FAIL"
fi

"$PYTHON_BIN" - "$SCORECARD" "$status" "$BUILD_LOG" "$VERIFY_LOG" <<'PY'
import json, sys
scorecard_path, status, build_log, verify_log = sys.argv[1:5]
try:
    build = json.load(open(build_log, encoding='utf-8'))
except FileNotFoundError:
    build = {}
try:
    verify = json.load(open(verify_log, encoding='utf-8'))
except FileNotFoundError:
    verify = {}
json.dump({
    "gate": "S6_G6",
    "name": "bundle_repro",
    "status": status,
    "details": {
        "bundle_path": build.get('tar_path'),
        "verify": verify,
    },
}, open(scorecard_path, "w", encoding='utf-8'), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
