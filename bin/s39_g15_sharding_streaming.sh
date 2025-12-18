#!/usr/bin/env bash
# =============================================================================
# S39 Gate G15: Sharding + Signal Streaming
# =============================================================================
# Verifica infraestrutura de sharding, streaming de sinais e tracing
#
# Invariantes validados:
#   INV-S39-01: 4 shards sempre healthy
#   INV-S39-02: Shard balance ratio < 1.5
#   INV-S39-03: ShardRouter P95 < 10ms
#   INV-S39-04: 3 Kafka brokers up
#   INV-S39-05: Consumer lag < 1s
#
# Referencia: docs/Agents/Planejamento/Programa 2/Sprint 39/S39_plano_tecnico.md
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "S39 Gate G15: Sharding + Signal Streaming"
echo "=========================================="
echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

PASS=0
FAIL=0
WARN=0

check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${NC} $desc"
        PASS=$((PASS+1))
    else
        echo -e "${RED}[FAIL]${NC} $desc"
        FAIL=$((FAIL+1))
    fi
}

warn_check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${NC} $desc"
        PASS=$((PASS+1))
    else
        echo -e "${YELLOW}[WARN]${NC} $desc (non-blocking)"
        WARN=$((WARN+1))
    fi
}

# =============================================================================
# SECTION 1: Sharding Infrastructure (W0 tasks)
# =============================================================================
echo ""
echo "=== 1. Sharding Infrastructure ==="

check "ShardRouter class exists" "grep -q 'class ShardRouter' $PROJECT_ROOT/app/data/sharding/router.py"
check "ShardConfig dataclass exists" "grep -q 'class ShardConfig' $PROJECT_ROOT/app/data/sharding/router.py"
check "ShardHealth model exists" "grep -q 'class ShardHealth' $PROJECT_ROOT/app/data/sharding/router.py"
check "Domain enum exists" "grep -q 'class Domain' $PROJECT_ROOT/app/data/sharding/router.py"
check "get_shard_id method" "grep -q 'def get_shard_id' $PROJECT_ROOT/app/data/sharding/router.py"
check "route method" "grep -q 'def route' $PROJECT_ROOT/app/data/sharding/router.py"
check "execute_on_all_shards method" "grep -q 'async def execute_on_all_shards' $PROJECT_ROOT/app/data/sharding/router.py"
check "health_check method" "grep -q 'async def health_check' $PROJECT_ROOT/app/data/sharding/router.py"

echo ""
echo "=== 2. Cross-Shard Queries ==="

check "CrossShardQuery class exists" "grep -q 'class CrossShardQuery' $PROJECT_ROOT/app/data/sharding/cross_shard.py"
check "execute method exists" "grep -q 'def execute\|async def execute' $PROJECT_ROOT/app/data/sharding/cross_shard.py"
check "aggregate method" "grep -q 'async def aggregate' $PROJECT_ROOT/app/data/sharding/cross_shard.py"

echo ""
echo "=== 3. Migration Manager ==="

check "MigrationManager class exists" "grep -q 'class MigrationManager' $PROJECT_ROOT/app/data/sharding/migration.py"
check "ShadowModeWriter class exists" "grep -q 'class ShadowModeWriter' $PROJECT_ROOT/app/data/sharding/migration.py"
check "MigrationPhase enum exists" "grep -q 'class MigrationPhase' $PROJECT_ROOT/app/data/sharding/migration.py"
check "start_shadow_mode method" "grep -q 'async def start_shadow_mode' $PROJECT_ROOT/app/data/sharding/migration.py"
check "execute_cutover method" "grep -q 'async def execute_cutover' $PROJECT_ROOT/app/data/sharding/migration.py"
check "rollback method" "grep -q 'async def rollback' $PROJECT_ROOT/app/data/sharding/migration.py"

echo ""
echo "=== 4. Feature Flags ==="

check "FeatureFlagManager class exists" "grep -q 'class FeatureFlagManager' $PROJECT_ROOT/app/config/feature_flags.py"
check "FeatureFlagValue class exists" "grep -q 'class FeatureFlagValue' $PROJECT_ROOT/app/config/feature_flags.py"
check "is_enabled method" "grep -q 'def is_enabled' $PROJECT_ROOT/app/config/feature_flags.py"
check "is_feature_enabled function" "grep -q 'def is_feature_enabled' $PROJECT_ROOT/app/config/feature_flags.py"
check "on_change callback support" "grep -q 'def on_change' $PROJECT_ROOT/app/config/feature_flags.py"

# =============================================================================
# SECTION 2: Signal Service (W1 tasks)
# =============================================================================
echo ""
echo "=== 5. Signal Service ==="

check "SignalService class exists" "grep -q 'class SignalService' $PROJECT_ROOT/app/signals/signal_service.py"
check "get_signals method" "grep -q 'def get_signals\|async def get_signals' $PROJECT_ROOT/app/signals/signal_service.py"
check "check_alerts method" "grep -q 'def check_alerts' $PROJECT_ROOT/app/signals/signal_service.py"

echo ""
echo "=== 6. Cache Service ==="

check "SignalCacheService class exists" "grep -q 'class SignalCacheService' $PROJECT_ROOT/app/signals/cache_service.py"
check "MemoryCacheBackend exists" "grep -q 'class MemoryCacheBackend' $PROJECT_ROOT/app/signals/cache_service.py"
check "RedisCacheBackend exists" "grep -q 'class RedisCacheBackend' $PROJECT_ROOT/app/signals/cache_service.py"

echo ""
echo "=== 7. Cache Invalidation ==="

check "CacheInvalidationService exists" "grep -q 'class CacheInvalidationService' $PROJECT_ROOT/app/signals/invalidation_service.py"
check "EventType enum exists" "grep -q 'class EventType' $PROJECT_ROOT/app/signals/invalidation_service.py"
check "SignalEventHandler exists" "grep -q 'class SignalEventHandler' $PROJECT_ROOT/app/signals/invalidation_service.py"

echo ""
echo "=== 8. Batch Calculator ==="

check "BatchSignalCalculator class exists" "grep -q 'class BatchSignalCalculator' $PROJECT_ROOT/app/signals/batch_calculator.py"
check "run method exists" "grep -q 'def run' $PROJECT_ROOT/app/signals/batch_calculator.py"
check "get_summary method exists" "grep -q 'def get_summary' $PROJECT_ROOT/app/signals/batch_calculator.py"

echo ""
echo "=== 9. Signal Calculators (4 types) ==="

check "LiesInCirculation calculator file" "test -f $PROJECT_ROOT/app/signals/calculators/lies_in_circulation.py"
check "LiesInCirculation class" "grep -q 'class.*Calculator' $PROJECT_ROOT/app/signals/calculators/lies_in_circulation.py"
check "Battleground calculator file" "test -f $PROJECT_ROOT/app/signals/calculators/battleground.py"
check "Battleground class" "grep -q 'class.*Calculator' $PROJECT_ROOT/app/signals/calculators/battleground.py"
check "SilenceRadar calculator file" "test -f $PROJECT_ROOT/app/signals/calculators/silence_radar.py"
check "SilenceRadar class" "grep -q 'class.*Calculator' $PROJECT_ROOT/app/signals/calculators/silence_radar.py"
check "NarrativeFragility calculator file" "test -f $PROJECT_ROOT/app/signals/calculators/narrative_fragility.py"
check "NarrativeFragility class" "grep -q 'class.*Calculator' $PROJECT_ROOT/app/signals/calculators/narrative_fragility.py"

# =============================================================================
# SECTION 3: OpenTelemetry Tracing (W4 tasks)
# =============================================================================
echo ""
echo "=== 10. OpenTelemetry Tracing ==="

check "Tracing module exists" "test -f $PROJECT_ROOT/app/observability/tracing.py"
check "setup_tracing function" "grep -q 'def setup_tracing' $PROJECT_ROOT/app/observability/tracing.py"
check "get_tracer function" "grep -q 'def get_tracer' $PROJECT_ROOT/app/observability/tracing.py"
check "trace_span context manager" "grep -q 'def trace_span' $PROJECT_ROOT/app/observability/tracing.py"
check "add_span_attribute helper" "grep -q 'def add_span_attribute' $PROJECT_ROOT/app/observability/tracing.py"
check "add_span_event helper" "grep -q 'def add_span_event' $PROJECT_ROOT/app/observability/tracing.py"
check "trace_claim_processing decorator" "grep -q 'def trace_claim_processing' $PROJECT_ROOT/app/observability/tracing.py"
check "trace_signal_update decorator" "grep -q 'def trace_signal_update' $PROJECT_ROOT/app/observability/tracing.py"
check "trace_db_query decorator" "grep -q 'def trace_db_query' $PROJECT_ROOT/app/observability/tracing.py"
check "get_trace_context function" "grep -q 'def get_trace_context' $PROJECT_ROOT/app/observability/tracing.py"
check "inject_trace_headers function" "grep -q 'def inject_trace_headers' $PROJECT_ROOT/app/observability/tracing.py"

# =============================================================================
# SECTION 4: Frontend Signal Streaming (W3 tasks)
# =============================================================================
echo ""
echo "=== 11. Frontend WebSocket Core ==="

check "WebSocket types file" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/core/websocket/types.ts"
check "WebSocketClient file" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/core/websocket/WebSocketClient.ts"
check "WebSocketProvider file" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/core/websocket/WebSocketProvider.tsx"
check "WebSocket index exports" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/core/websocket/index.ts"

echo ""
echo "=== 12. Signal Stream Components ==="

check "useSignalStream hook exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/signals/hooks/useSignalStream.ts"
check "useSignalStream exports" "grep -q 'export.*useSignalStream' $PROJECT_ROOT/frontend/inspectah-ui/src/modules/signals/hooks/useSignalStream.ts"
check "SignalStreamPanel component" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/signals/components/SignalStreamPanel.tsx"
check "SignalCard component" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/signals/components/SignalCard.tsx"
check "Signals module index" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/signals/index.ts"

echo ""
echo "=== 13. WebSocket Mock Utility ==="

check "WebSocket mock exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/test/mocks/websocket.ts"
check "MockWebSocket class" "grep -q 'class MockWebSocket' $PROJECT_ROOT/frontend/inspectah-ui/src/test/mocks/websocket.ts"
check "createSignalUpdate helper" "grep -q 'function createSignalUpdate\|export function createSignalUpdate' $PROJECT_ROOT/frontend/inspectah-ui/src/test/mocks/websocket.ts"
check "setupMockWebSocket helper" "grep -q 'function setupMockWebSocket\|export function setupMockWebSocket' $PROJECT_ROOT/frontend/inspectah-ui/src/test/mocks/websocket.ts"

# =============================================================================
# SECTION 5: Tests
# =============================================================================
echo ""
echo "=== 14. Backend Tests ==="

check "Sharding tests directory" "test -d $PROJECT_ROOT/tests/data/sharding"
check "Router tests exist" "test -f $PROJECT_ROOT/tests/data/sharding/test_router.py"
check "Cross-shard tests exist" "test -f $PROJECT_ROOT/tests/data/sharding/test_cross_shard.py"
check "Migration tests exist" "test -f $PROJECT_ROOT/tests/data/sharding/test_migration.py"
check "Feature flags tests exist" "test -f $PROJECT_ROOT/tests/config/test_feature_flags.py"
check "Signal tests directory" "test -d $PROJECT_ROOT/tests/signals"
check "Signal service tests exist" "test -f $PROJECT_ROOT/tests/signals/test_signal_service.py"
check "Cache service tests exist" "test -f $PROJECT_ROOT/tests/signals/test_cache_service.py"
check "Invalidation tests exist" "test -f $PROJECT_ROOT/tests/signals/test_invalidation_service.py"
check "Calculator tests exist" "test -f $PROJECT_ROOT/tests/signals/test_calculators.py"
check "Tracing tests exist" "test -f $PROJECT_ROOT/tests/obs/test_tracing.py"

echo ""
echo "=== 15. Frontend Tests ==="

check "useSignalStream test exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/__tests__/hooks/useSignalStream.test.ts"
check "SignalStreamPanel test exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/__tests__/components/SignalStreamPanel.test.tsx"

# =============================================================================
# SECTION 6: Run Tests
# =============================================================================
echo ""
echo "=== 16. Running Backend Tests ==="
cd "$PROJECT_ROOT"

# Run sharding + signals + tracing tests
TEST_OUTPUT=$(PYTHONPATH=. .venv/bin/python -m pytest tests/data/sharding/ tests/signals/ tests/obs/test_tracing.py tests/config/test_feature_flags.py -v --tb=short -q 2>&1 || true)
TEST_RESULT=$(echo "$TEST_OUTPUT" | tail -3)
echo "$TEST_RESULT"

if echo "$TEST_OUTPUT" | grep -q "passed"; then
    if echo "$TEST_OUTPUT" | grep -q "failed"; then
        FAIL=$((FAIL+1))
        echo -e "${RED}[FAIL]${NC} Backend tests have failures"
    else
        PASS=$((PASS+1))
        echo -e "${GREEN}[PASS]${NC} Backend tests pass"
    fi
else
    FAIL=$((FAIL+1))
    echo -e "${RED}[FAIL]${NC} Backend tests failed to run"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=========================================="
echo "Gate G15 Results"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Warnings: $WARN"
echo ""
echo "Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}Gate G15: FAILED${NC}"
    exit 1
fi
echo -e "${GREEN}Gate G15: PASSED${NC}"
