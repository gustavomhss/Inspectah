#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

BUNDLE_DIR="out/bundles"
OUT_ZIP="$ROOT_DIR/$BUNDLE_DIR/inspectah_s34_evidence_bundle.zip"

mkdir -p "$BUNDLE_DIR"

echo "[S34] Empacotando evidências em $OUT_ZIP"

tmpdir=$(mktemp -d)
cp -r "$ROOT_DIR"/out/evidence/S34_* "$tmpdir" 2>/dev/null || true
cp -r "$ROOT_DIR"/out/scorecards/S34_*.json "$tmpdir" 2>/dev/null || true

(cd "$tmpdir" && zip -r "$OUT_ZIP" . >/dev/null)

rm -rf "$tmpdir"
echo "[S34] Bundle gerado: $OUT_ZIP"
