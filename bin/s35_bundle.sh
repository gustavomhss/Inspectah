#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

OUT_DIR="out/bundles"
ZIP_PATH="$OUT_DIR/inspectah_s35_evidence_bundle.zip"
LOG="out/evidence/S35_bundle/log.txt"

mkdir -p "$OUT_DIR" out/evidence/S35_bundle

echo "[S35_bundle] Empacotando evidências e scorecards" | tee "$LOG"

zip -r "$ZIP_PATH" out/scorecards out/evidence >/dev/null

echo "[S35_bundle] Bundle criado em $ZIP_PATH" | tee -a "$LOG"

zip -T "$ZIP_PATH" >/dev/null

echo "[S35_bundle] Bundle verificado com sucesso" | tee -a "$LOG"
