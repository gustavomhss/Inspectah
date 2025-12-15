#!/usr/bin/env bash
# S38 Gate G14: Ops Dashboard & Observability
# Verifica implementacao completa de ops e observabilidade

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "S38 Gate G14: Ops Dashboard & Observability"
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
echo "=== Dashboard Service ==="
check "dashboard_service.py exists" "test -f $PROJECT_ROOT/app/ops/dashboard_service.py"
check "OpsDashboardService class exists" "grep -q 'class OpsDashboardService' $PROJECT_ROOT/app/ops/dashboard_service.py"
check "HealthChecker class exists" "grep -q 'class HealthChecker' $PROJECT_ROOT/app/ops/dashboard_service.py"
check "AlertManager class exists" "grep -q 'class AlertManager' $PROJECT_ROOT/app/ops/dashboard_service.py"
check "get_snapshot method" "grep -q 'def get_snapshot' $PROJECT_ROOT/app/ops/dashboard_service.py"

echo ""
echo "=== Contracts ==="
check "Contracts module exists" "test -d $PROJECT_ROOT/app/contracts"
check "v1 contracts exist" "test -f $PROJECT_ROOT/app/contracts/v1.py"
check "ClaimContract exists" "grep -q 'class ClaimContract' $PROJECT_ROOT/app/contracts/v1.py"
check "SourceContract exists" "grep -q 'class SourceContract' $PROJECT_ROOT/app/contracts/v1.py"
check "ResponseEnvelope exists" "grep -q 'class ResponseEnvelope' $PROJECT_ROOT/app/contracts/v1.py"

echo ""
echo "=== Explainability ==="
check "Explainability module exists" "test -d $PROJECT_ROOT/app/explainability"
check "ExplainabilityService exists" "grep -q 'class ExplainabilityService' $PROJECT_ROOT/app/explainability/service.py"
check "explain_verdict method" "grep -q 'def explain_verdict' $PROJECT_ROOT/app/explainability/service.py"
check "Factor class exists" "grep -q 'class Factor' $PROJECT_ROOT/app/explainability/service.py"

echo ""
echo "=== Dashboard API ==="
check "Dashboard API router exists" "grep -q 'router = APIRouter' $PROJECT_ROOT/app/api/dashboard_routes.py"
check "GET /snapshot endpoint" "grep -q 'snapshot' $PROJECT_ROOT/app/api/dashboard_routes.py"
check "GET /health endpoint" "grep -q 'health' $PROJECT_ROOT/app/api/dashboard_routes.py"
check "GET /alerts endpoint" "grep -q 'alerts' $PROJECT_ROOT/app/api/dashboard_routes.py"

echo ""
echo "=== Observability ==="
check "Alerts directory exists" "test -d $PROJECT_ROOT/observability/alerts"
check "S38 alerts config exists" "test -f $PROJECT_ROOT/observability/alerts/s38_alerts.yaml"
check "S38 dashboard config exists" "test -f $PROJECT_ROOT/observability/dashboards/s38_hardening.json"

echo ""
echo "=========================================="
echo "Gate G14 Results: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
echo "Gate G14: PASSED"
