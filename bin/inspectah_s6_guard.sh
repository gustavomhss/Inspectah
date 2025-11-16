#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOG_DIR="$REPO_ROOT/out/logs"
LOG_FILE="$LOG_DIR/inspectah_s6_guard.log"
DOMAIN="${1:-dominio_piloto}"

mkdir -p "$LOG_DIR"
: > "$LOG_FILE"

run_step() {
  local label="$1"
  shift
  {
    echo "[guard] $label"
    "$@"
    echo
  } | tee -a "$LOG_FILE"
}

cd "$REPO_ROOT"
run_step "Validando fontes" "$REPO_ROOT/bin/inspectah_sources_validate.sh" "$DOMAIN"
run_step "Preview de campos" "$REPO_ROOT/bin/inspectah_fields_preview.sh" "$DOMAIN"
run_step "Coletando evidências" "$REPO_ROOT/bin/inspectah_collect_once.sh" "$DOMAIN"
run_step "Consultando registros" "$REPO_ROOT/bin/inspectah_query.sh" "$DOMAIN" --page 1 --page-size 5 --format table

echo "[guard] log salvo em $LOG_FILE"
