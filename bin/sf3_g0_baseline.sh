#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/logs"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF3_G0"
LOG_PATH="$LOG_DIR/SF3_baseline.md"
FIXTURES_PATH="$EVIDENCE_DIR/fixtures_hashes.txt"

mkdir -p "$LOG_DIR" "$EVIDENCE_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF3_G0][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

log "# SF3 Baseline (G0)"
log ""
log "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# 1) Verificar scripts s20–s29/sf3: shebang + set -euo + perm exec
log "## Scripts (s20–s29/sf3) set -euo + exec"
missing=0
while IFS= read -r script; do
  if ! head -n 1 "$script" | grep -qE '^#!'; then
    log "- [FAIL] sem shebang: $script"; missing=$((missing+1))
    continue
  fi
  if ! grep -q "set -euo pipefail" "$script"; then
    log "- [FAIL] sem set -euo pipefail: $script"; missing=$((missing+1))
    continue
  fi
  if [ ! -x "$script" ]; then
    log "- [FAIL] sem permissão de execução: $script"; missing=$((missing+1))
    continue
  fi
  log "- [OK] $script"
done < <(find "$ROOT_DIR/bin" -maxdepth 1 -type f \( -name "s2[0-9]*_g*.sh" -o -name "sf3_*.sh" \) | sort)

if [ "$missing" -gt 0 ]; then
  fail "Encontrados $missing scripts sem padrões de rc estrito."
fi

# 2) Deps: Prom/Alertmanager/Playwright/IdP (stub via middleware)
log ""
log "## Deps de ambiente"
PROM_PID="$(pgrep -f 'prometheus.*prometheus_sf2.yml' || true)"
ALERT_PID="$(pgrep -f 'alertmanager.*alertmanager_sf2.yml' || true)"
PLAYWRIGHT_BIN="$ROOT_DIR/frontend/inspectah-ui/node_modules/.bin/playwright"

log "- Prometheus: ${PROM_PID:-'não encontrado'}"
log "- Alertmanager: ${ALERT_PID:-'não encontrado'}"
log "- Playwright: $( [ -x "$PLAYWRIGHT_BIN" ] && echo "presente" || echo "ausente" )"
log "- IdP/RBAC: middleware app/middlewares/auth.py ativo (headers X-Actor/X-Role)"

if [ -z "$PROM_PID" ] || [ -z "$ALERT_PID" ]; then
  fail "Prometheus ou Alertmanager ausente. G0 deve falhar se ambiente crítico faltar."
fi
if [ ! -x "$PLAYWRIGHT_BIN" ]; then
  fail "Playwright não instalado em frontend/inspectah-ui (node_modules/.bin/playwright ausente)."
fi

# 3) Fixtures (hash/commit) para auth/truth/ingest
log ""
log "## Fixtures (hashes)"
{
  echo "# Fixture hashes (auth/truth/ingest)"
  sha256sum "$ROOT_DIR/app/auth/routes.py"
  sha256sum "$ROOT_DIR/app/api/truth_routes.py"
  sha256sum "$ROOT_DIR/metrics/newsdata_ingest.py"
} > "$FIXTURES_PATH"
log "- Hashes salvos em $FIXTURES_PATH"

log ""
log "[SF3_G0] Baseline concluído."
