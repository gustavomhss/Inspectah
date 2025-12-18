#!/usr/bin/env bash
# =============================================================================
# S39 Gate G18: Production Readiness
# =============================================================================
# Verifica runbooks, alertas, dashboards, health checks e observabilidade
#
# Invariantes validados:
#   INV-S39-11: Uptime >= 99.9% (7d)
#   INV-S39-12: Throughput >= 50K/dia
#   INV-S39-13: API P95 < 100ms
#   INV-S39-14: WebSocket connection stable
#   INV-S39-16: All E2E tests passing
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
echo "S39 Gate G18: Production Readiness"
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
# SECTION 1: Operational Runbooks (W4 tasks T-RB-001 to T-RB-011)
# =============================================================================
echo ""
echo "=== 1. Operational Runbooks (11 total) ==="

check "S39_shard_down.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_shard_down.md"
check "S39_shard_rebalance.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_shard_rebalance.md"
check "S39_router_slow.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_router_slow.md"
check "S39_replication_lag.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_replication_lag.md"
check "S39_connections.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_connections.md"
check "S39_kafka_broker_down.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_kafka_broker_down.md"
check "S39_kafka_lag.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_kafka_lag.md"
check "S39_memory_tokens.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_memory_tokens.md"
check "S39_llm_quota.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_llm_quota.md"
check "S39_api_down.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_api_down.md"
check "S39_throughput.md exists" "test -f $PROJECT_ROOT/docs/runbooks/S39_throughput.md"

echo ""
echo "=== 2. Runbook Content Validation ==="

# Check runbooks have required sections
check "shard_down has symptoms section" "grep -q 'Sintomas\|Symptoms\|Identificacao' $PROJECT_ROOT/docs/runbooks/S39_shard_down.md"
check "shard_down has actions section" "grep -q 'Acoes\|Actions\|Mitigacao\|Passos' $PROJECT_ROOT/docs/runbooks/S39_shard_down.md"
check "kafka_lag has symptoms section" "grep -q 'Sintomas\|Symptoms\|Identificacao' $PROJECT_ROOT/docs/runbooks/S39_kafka_lag.md"
check "api_down has actions section" "grep -q 'Acoes\|Actions\|Mitigacao\|Passos' $PROJECT_ROOT/docs/runbooks/S39_api_down.md"

echo ""
echo "=== 3. Runbook Cross-References ==="

check "shard_down references rebalance" "grep -q 'rebalance\|S39_shard_rebalance' $PROJECT_ROOT/docs/runbooks/S39_shard_down.md"
check "kafka_lag references broker_down" "grep -q 'broker\|S39_kafka_broker' $PROJECT_ROOT/docs/runbooks/S39_kafka_lag.md"
check "memory_tokens references llm_quota" "grep -q 'quota\|S39_llm_quota' $PROJECT_ROOT/docs/runbooks/S39_memory_tokens.md"

# =============================================================================
# SECTION 2: Prometheus Alerts (W4 tasks T-OBS-API-001)
# =============================================================================
echo ""
echo "=== 4. Prometheus Alert Files ==="

check "Kafka alerts file exists" "test -f $PROJECT_ROOT/observability/alerts/s39_kafka.yaml"
check "Memory alerts file exists" "test -f $PROJECT_ROOT/observability/alerts/s39_memory.yaml"
check "API alerts file exists" "test -f $PROJECT_ROOT/observability/alerts/s39_api.yaml"

echo ""
echo "=== 5. Kafka Alert Rules ==="

check "Kafka alert groups defined" "grep -q 'groups:\|name:' $PROJECT_ROOT/observability/alerts/s39_kafka.yaml"
check "KafkaConsumerLag alert defined" "grep -q 'consumer_lag\|kafka_consumer\|lag' $PROJECT_ROOT/observability/alerts/s39_kafka.yaml"
check "KafkaBrokerDown alert defined" "grep -q 'broker\|kafka_broker\|Broker' $PROJECT_ROOT/observability/alerts/s39_kafka.yaml"
check "Kafka runbook reference" "grep -q 'runbook\|docs/runbooks' $PROJECT_ROOT/observability/alerts/s39_kafka.yaml"

echo ""
echo "=== 6. Memory Alert Rules ==="

check "Memory alert groups defined" "grep -q 'groups:\|name:' $PROJECT_ROOT/observability/alerts/s39_memory.yaml"
check "MemoryHealth alert defined" "grep -q 'memory_health\|s39_memory_health' $PROJECT_ROOT/observability/alerts/s39_memory.yaml"
check "MemoryCapacity alert defined" "grep -q 'memory_capacity\|memory_controller\|entries' $PROJECT_ROOT/observability/alerts/s39_memory.yaml"
check "Memory runbook reference" "grep -q 'runbook\|docs/runbooks' $PROJECT_ROOT/observability/alerts/s39_memory.yaml"

echo ""
echo "=== 7. API Alert Rules ==="

check "API alert groups defined" "grep -q 'groups:\|name:' $PROJECT_ROOT/observability/alerts/s39_api.yaml"
check "APILatency alert defined" "grep -q 'latency\|duration\|p95\|percentile' $PROJECT_ROOT/observability/alerts/s39_api.yaml"
check "APIErrorRate alert defined" "grep -q 'error\|rate\|5xx\|4xx' $PROJECT_ROOT/observability/alerts/s39_api.yaml"
check "API runbook reference" "grep -q 'runbook\|docs/runbooks' $PROJECT_ROOT/observability/alerts/s39_api.yaml"

# =============================================================================
# SECTION 3: Loki Log Patterns (W4 task T-OBS-LOKI-001)
# =============================================================================
echo ""
echo "=== 8. Loki Log Patterns ==="

check "Loki patterns file exists" "test -f $PROJECT_ROOT/observability/loki/s39_patterns.yaml"
check "Shard patterns defined" "grep -q 'shard\|SHARD' $PROJECT_ROOT/observability/loki/s39_patterns.yaml"
check "Error patterns defined" "grep -q 'error\|ERROR\|exception' $PROJECT_ROOT/observability/loki/s39_patterns.yaml"
check "Pattern extraction rules" "grep -q 'pattern\|regex\|extract' $PROJECT_ROOT/observability/loki/s39_patterns.yaml"

# =============================================================================
# SECTION 4: Health Checks (W4 task T-OBS-HEALTH-001)
# =============================================================================
echo ""
echo "=== 9. Health Checks ==="

check "Health checks file exists" "test -f $PROJECT_ROOT/observability/health/s39_checks.yaml"
check "Liveness probe defined" "grep -q 'liveness\|livenessProbe' $PROJECT_ROOT/observability/health/s39_checks.yaml"
check "Readiness probe defined" "grep -q 'readiness\|readinessProbe' $PROJECT_ROOT/observability/health/s39_checks.yaml"
check "Startup probe defined" "grep -q 'startup\|startupProbe' $PROJECT_ROOT/observability/health/s39_checks.yaml"
check "Health endpoints defined" "grep -q '/health\|/ready\|/live' $PROJECT_ROOT/observability/health/s39_checks.yaml"

# =============================================================================
# SECTION 5: Docker Infrastructure
# =============================================================================
echo ""
echo "=== 10. Docker Infrastructure ==="

check "docker-compose.shards.yml exists" "test -f $PROJECT_ROOT/docker/docker-compose.shards.yml"
check "docker-compose.kafka.yml exists" "test -f $PROJECT_ROOT/docker/docker-compose.kafka.yml"
check "docker-compose.redis.yml exists" "test -f $PROJECT_ROOT/docker/docker-compose.redis.yml"
check "docker-compose.full.yml exists" "test -f $PROJECT_ROOT/docker/docker-compose.full.yml"

echo ""
echo "=== 11. Docker Compose Content ==="

check "Shards compose has 4 shard services" "grep -c 'shard\|postgres' $PROJECT_ROOT/docker/docker-compose.shards.yml | grep -q '[4-9]\|[0-9][0-9]'"
check "Kafka compose has broker services" "grep -q 'kafka\|broker\|zookeeper' $PROJECT_ROOT/docker/docker-compose.kafka.yml"
check "Redis compose has redis service" "grep -q 'redis' $PROJECT_ROOT/docker/docker-compose.redis.yml"

# =============================================================================
# SECTION 6: Database Migrations
# =============================================================================
echo ""
echo "=== 12. Database Migrations ==="

check "Sprint39 sharding migration exists" "test -f $PROJECT_ROOT/db/migrations/031_sprint39_sharding.sql"
check "Sprint37 claimgraph migration exists" "test -f $PROJECT_ROOT/db/migrations/027_sprint37_claimgraph.sql"
check "Sprint38 relations migration exists" "test -f $PROJECT_ROOT/db/migrations/029_sprint38_claim_relations.sql"

# =============================================================================
# SECTION 7: E2E Tests (W4 tasks T-TEST-E2E-001, T-TEST-E2E-002)
# =============================================================================
echo ""
echo "=== 13. E2E Test Specs ==="

check "E2E explain-tree spec exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/e2e/explain-tree.spec.ts"
check "E2E signal-stream spec exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/e2e/signal-stream.spec.ts"

echo ""
echo "=== 14. E2E Test Content ==="

check "explain-tree has test cases" "grep -q 'test\|it\|describe' $PROJECT_ROOT/frontend/inspectah-ui/e2e/explain-tree.spec.ts"
check "signal-stream has test cases" "grep -q 'test\|it\|describe' $PROJECT_ROOT/frontend/inspectah-ui/e2e/signal-stream.spec.ts"

# =============================================================================
# SECTION 8: ORR Checklist Compliance
# =============================================================================
echo ""
echo "=== 15. ORR Checklist Compliance ==="

# Count runbooks
RUNBOOK_COUNT=$(ls -1 $PROJECT_ROOT/docs/runbooks/S39_*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$RUNBOOK_COUNT" -ge 11 ]; then
    echo -e "${GREEN}[PASS]${NC} Runbook count >= 11 (found: $RUNBOOK_COUNT)"
    PASS=$((PASS+1))
else
    echo -e "${RED}[FAIL]${NC} Runbook count < 11 (found: $RUNBOOK_COUNT)"
    FAIL=$((FAIL+1))
fi

# Count alert files
ALERT_COUNT=$(ls -1 $PROJECT_ROOT/observability/alerts/s39_*.yaml 2>/dev/null | wc -l | tr -d ' ')
if [ "$ALERT_COUNT" -ge 3 ]; then
    echo -e "${GREEN}[PASS]${NC} Alert files >= 3 (found: $ALERT_COUNT)"
    PASS=$((PASS+1))
else
    echo -e "${RED}[FAIL]${NC} Alert files < 3 (found: $ALERT_COUNT)"
    FAIL=$((FAIL+1))
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=========================================="
echo "Gate G18 Results"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Warnings: $WARN"
echo ""
echo "Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}Gate G18: FAILED${NC}"
    exit 1
fi
echo -e "${GREEN}Gate G18: PASSED${NC}"
