#!/usr/bin/env bash
# S38 Gate G11: Sources & Scrapers
# Verifica implementacao completa do modulo de fontes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "S38 Gate G11: Sources & Scrapers"
echo "=========================================="

PASS=0
FAIL=0

check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo "[PASS] $desc"
        PASS=$((PASS+1))
    else
        echo "[FAIL] $desc"
        FAIL=$((FAIL+1))
    fi
}

echo ""
echo "=== Official Integrators ==="
check "gov_br.py integrator exists" "test -f $PROJECT_ROOT/app/ingestion/providers/gov_br.py"
check "dados_gov.py integrator exists" "test -f $PROJECT_ROOT/app/ingestion/providers/dados_gov.py"
check "tse.py integrator exists" "test -f $PROJECT_ROOT/app/ingestion/providers/tse.py"
check "official_integrator.py exists" "test -f $PROJECT_ROOT/app/ingestion/official_integrator.py"

echo ""
echo "=== Scraper Framework ==="
check "Scrapers directory exists" "test -d $PROJECT_ROOT/app/ingestion/scrapers"
check "BaseScraper class exists" "grep -q 'class BaseScraper' $PROJECT_ROOT/app/ingestion/scrapers/base.py"
check "aosfatos.py scraper exists" "test -f $PROJECT_ROOT/app/ingestion/scrapers/aosfatos.py"
check "lupa.py scraper exists" "test -f $PROJECT_ROOT/app/ingestion/scrapers/lupa.py"
check "boatos.py scraper exists" "test -f $PROJECT_ROOT/app/ingestion/scrapers/boatos.py"
check "efarsas.py scraper exists" "test -f $PROJECT_ROOT/app/ingestion/scrapers/efarsas.py"
check "fatooufake.py scraper exists" "test -f $PROJECT_ROOT/app/ingestion/scrapers/fatooufake.py"

echo ""
echo "=== Resilience Patterns ==="
check "RateLimiter exists" "grep -q 'class TokenBucketRateLimiter' $PROJECT_ROOT/app/ingestion/rate_limiter.py"
check "CircuitBreaker exists" "grep -q 'class CircuitBreaker' $PROJECT_ROOT/app/ingestion/circuit_breaker.py"
check "HealthMonitor exists" "grep -q 'class HealthMonitor' $PROJECT_ROOT/app/ingestion/health_monitor.py"

echo ""
echo "=== Sources API ==="
check "Sources API router exists" "grep -q 'router = APIRouter' $PROJECT_ROOT/app/api/sources_routes.py"
check "GET /sources endpoint" "grep -q '@router.get' $PROJECT_ROOT/app/api/sources_routes.py"
check "POST /sources endpoint" "grep -q '@router.post' $PROJECT_ROOT/app/api/sources_routes.py"
check "dry-run endpoint" "grep -q 'dry-run' $PROJECT_ROOT/app/api/sources_routes.py"

echo ""
echo "=== Frontend Module ==="
check "Sources module directory exists" "test -d $PROJECT_ROOT/frontend/inspectah-ui/src/modules/sources"
check "SourcesPage.tsx exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/sources/pages/SourcesPage.tsx"
check "SourceDetailPage.tsx exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/sources/pages/SourceDetailPage.tsx"
check "useSources hook exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/sources/hooks/useSources.ts"

echo ""
echo "=========================================="
echo "Gate G11 Results: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
echo "Gate G11: PASSED"
