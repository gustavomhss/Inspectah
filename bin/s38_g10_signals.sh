#!/usr/bin/env bash
# S38 Gate G10: Signals On-Demand
# Verifica implementacao completa do modulo de sinais

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "S38 Gate G10: Signals On-Demand"
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
echo "=== Signal Types ==="
check "SignalType enum exists" "grep -q 'class SignalType' $PROJECT_ROOT/app/signals/signal_types.py"
check "All signal types defined" "grep -q 'MENTIRAS_EM_CIRCULACAO' $PROJECT_ROOT/app/signals/signal_types.py && grep -q 'CAMPO_BATALHA' $PROJECT_ROOT/app/signals/signal_types.py"
check "SignalConfig exists" "grep -q 'class SignalConfig' $PROJECT_ROOT/app/signals/signal_types.py"
check "SignalValue dataclass exists" "grep -q 'class SignalValue' $PROJECT_ROOT/app/signals/signal_types.py"

echo ""
echo "=== Signal Service ==="
check "SignalService class exists" "grep -q 'class SignalService' $PROJECT_ROOT/app/signals/signal_service.py"
check "get_signals method exists" "grep -q 'async def get_signals' $PROJECT_ROOT/app/signals/signal_service.py"
check "check_alerts method exists" "grep -q 'def check_alerts' $PROJECT_ROOT/app/signals/signal_service.py"
check "MentirasEmCirculacaoCalculator exists" "grep -q 'class MentirasEmCirculacaoCalculator' $PROJECT_ROOT/app/signals/signal_service.py"

echo ""
echo "=== Cache Service ==="
check "SignalCacheService exists" "grep -q 'class SignalCacheService' $PROJECT_ROOT/app/signals/cache_service.py"
check "MemoryCacheBackend exists" "grep -q 'class MemoryCacheBackend' $PROJECT_ROOT/app/signals/cache_service.py"
check "RedisCacheBackend exists" "grep -q 'class RedisCacheBackend' $PROJECT_ROOT/app/signals/cache_service.py"

echo ""
echo "=== Invalidation Service ==="
check "CacheInvalidationService exists" "grep -q 'class CacheInvalidationService' $PROJECT_ROOT/app/signals/invalidation_service.py"
check "EventType enum exists" "grep -q 'class EventType' $PROJECT_ROOT/app/signals/invalidation_service.py"
check "SignalEventHandler exists" "grep -q 'class SignalEventHandler' $PROJECT_ROOT/app/signals/invalidation_service.py"

echo ""
echo "=== API Routes ==="
check "Signals API router exists" "grep -q 'router = APIRouter' $PROJECT_ROOT/app/api/signals_routes.py"
check "GET /signals endpoint" "grep -q '@router.get.*response_model=SignalBatchResponse' $PROJECT_ROOT/app/api/signals_routes.py"
check "POST /signals/invalidate endpoint" "grep -q '@router.post.*invalidate' $PROJECT_ROOT/app/api/signals_routes.py"

echo ""
echo "=== Tests ==="
check "Signal tests directory exists" "test -d $PROJECT_ROOT/tests/signals"
check "Signal service tests exist" "test -f $PROJECT_ROOT/tests/signals/test_signal_service.py"

echo ""
echo "=========================================="
echo "Gate G10 Results: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
echo "Gate G10: PASSED"
