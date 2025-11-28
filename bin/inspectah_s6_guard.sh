#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN="${1:-dominio_piloto}"
LOG_DIR="$REPO_ROOT/out/logs"
LOG_FILE="$LOG_DIR/inspectah_s6_guard.log"

mkdir -p "$LOG_DIR"
cd "$REPO_ROOT"

echo "[guard] executando guard Sprint 6 para ${DOMAIN}" | tee "$LOG_FILE"

run_step() {
  local description="$1"
  shift
  echo "[guard] $description" | tee -a "$LOG_FILE"
  "$@" | tee -a "$LOG_FILE"
}

run_step "Validar fontes" "$REPO_ROOT/bin/inspectah_sources_validate.sh" "$DOMAIN"
run_step "Preview de campos" "$REPO_ROOT/bin/inspectah_fields_preview.sh" "$DOMAIN"
run_step "Coleta única" "$REPO_ROOT/bin/inspectah_collect_once.sh" "$DOMAIN"
run_step "Consulta canônica" "$REPO_ROOT/bin/inspectah_query.sh" "$DOMAIN" --page 1 --page-size 5 --format table

echo "[guard] guard finalizado. log: $LOG_FILE"
