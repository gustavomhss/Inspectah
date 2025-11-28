#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out"
BUNDLE_DIR="$OUT_DIR/bundles"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BUNDLE_PATH="$BUNDLE_DIR/s25_full_orr_bundle_${TIMESTAMP}.zip"

mkdir -p "$BUNDLE_DIR"

TMP_DIR="$(mktemp -d)"

cp -r "$OUT_DIR/scorecards" "$TMP_DIR/scorecards"
cp -r "$OUT_DIR/evidence" "$TMP_DIR/evidence"
mkdir -p "$TMP_DIR/docs"
cp -r "$ROOT_DIR/Sprint 25" "$TMP_DIR/docs/"
cp "$ROOT_DIR/docs/sprint_25_code_review_checklist.md" "$TMP_DIR/docs/"

cat >"$TMP_DIR/README_S25_BUNDLE.md" <<'MD'
# Sprint 25 ORR Bundle

Conteúdo:
- scorecards/: scorecards S25_G0..G8 e ORR.
- evidence/: evidências produzidas pelos gates.
- docs/: capítulos da Sprint 25 e checklist de revisão.

Reexecução de gates:
1) Ative o venv: `source .venv/bin/activate`
2) Rode scripts em bin/: s25_g0...s25_g7, s25_orr.sh, s25_make_bundle.sh

Contato: Squad Verdade/Fato.
MD

(cd "$TMP_DIR" && zip -r "$BUNDLE_PATH" . >/dev/null)
rm -rf "$TMP_DIR"

echo "[S25_BUNDLE] Gerado em $BUNDLE_PATH"
