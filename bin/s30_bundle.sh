#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out"
BUNDLE="$OUT_DIR/bundles/inspectah_s30_evidence_bundle.zip"

mkdir -p "$OUT_DIR/bundles"

zip -r "$BUNDLE" "$OUT_DIR/scorecards" "$OUT_DIR/evidence" >/dev/null
echo "[s30-bundle] bundle criado em $BUNDLE"
