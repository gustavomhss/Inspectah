#!/usr/bin/env bash
# =============================================================================
# S39 Gate G16: ClaimGraph + Memory Controller
# =============================================================================
# Verifica grafo de claims, inferencia de relacoes e controlador de memoria
#
# Invariantes validados:
#   INV-S39-06: Cross-shard P95 < 200ms
#   INV-S39-07: Memory tokens < 8000
#   INV-S39-08: Context switch P95 < 100ms
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
echo "S39 Gate G16: ClaimGraph + Memory Controller"
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
# SECTION 1: ClaimGraph Models (W2 tasks)
# =============================================================================
echo ""
echo "=== 1. ClaimGraph Models ==="

check "GraphNode base class exists" "grep -q 'class GraphNode' $PROJECT_ROOT/app/claims/graph_models.py"
check "ClaimNode model exists" "grep -q 'class ClaimNode' $PROJECT_ROOT/app/claims/graph_models.py"
check "EntityNode model exists" "grep -q 'class EntityNode' $PROJECT_ROOT/app/claims/graph_models.py"
check "CaseNode model exists" "grep -q 'class CaseNode' $PROJECT_ROOT/app/claims/graph_models.py"
check "TopicNode model exists" "grep -q 'class TopicNode' $PROJECT_ROOT/app/claims/graph_models.py"
check "GraphEdge model exists" "grep -q 'class GraphEdge' $PROJECT_ROOT/app/claims/graph_models.py"
check "NodeType enum exists" "grep -q 'class NodeType' $PROJECT_ROOT/app/claims/graph_models.py"
check "EdgeType enum exists" "grep -q 'class EdgeType' $PROJECT_ROOT/app/claims/graph_models.py"
check "ClaimState enum exists" "grep -q 'class ClaimState' $PROJECT_ROOT/app/claims/graph_models.py"

echo ""
echo "=== 2. Relation Types ==="

check "RelationType enum exists" "grep -q 'class RelationType' $PROJECT_ROOT/app/claims/relation_types.py"
check "Multiple relation types defined" "grep -c 'RelationType\.' $PROJECT_ROOT/app/claims/relation_types.py | grep -q '[3-9]\|[0-9][0-9]'"

# =============================================================================
# SECTION 2: ClaimGraph Repository
# =============================================================================
echo ""
echo "=== 3. ClaimGraph Repository ==="

check "ClaimGraphRepository class exists" "grep -q 'class ClaimGraphRepository' $PROJECT_ROOT/app/claims/graph_repository.py"
check "insert_node method" "grep -q 'def insert_node' $PROJECT_ROOT/app/claims/graph_repository.py"
check "get_node method" "grep -q 'def get_node' $PROJECT_ROOT/app/claims/graph_repository.py"
check "find_nodes method" "grep -q 'def find_nodes' $PROJECT_ROOT/app/claims/graph_repository.py"
check "update_node method" "grep -q 'def update_node' $PROJECT_ROOT/app/claims/graph_repository.py"
check "delete_node method" "grep -q 'def delete_node' $PROJECT_ROOT/app/claims/graph_repository.py"
check "insert_edge method" "grep -q 'def insert_edge' $PROJECT_ROOT/app/claims/graph_repository.py"
check "get_edge method" "grep -q 'def get_edge' $PROJECT_ROOT/app/claims/graph_repository.py"
check "find_edges method" "grep -q 'def find_edges' $PROJECT_ROOT/app/claims/graph_repository.py"
check "get_cluster method" "grep -q 'def get_cluster' $PROJECT_ROOT/app/claims/graph_repository.py"
check "get_contradictions method" "grep -q 'def get_contradictions' $PROJECT_ROOT/app/claims/graph_repository.py"
check "get_timeline method" "grep -q 'def get_timeline' $PROJECT_ROOT/app/claims/graph_repository.py"
check "get_metrics method" "grep -q 'def get_metrics' $PROJECT_ROOT/app/claims/graph_repository.py"

# =============================================================================
# SECTION 3: ClaimGraph Service
# =============================================================================
echo ""
echo "=== 4. ClaimGraph Service ==="

check "ClaimGraphService class exists" "grep -q 'class ClaimGraphService' $PROJECT_ROOT/app/claims/graph_service.py"
check "add_claim method" "grep -q 'def add_claim' $PROJECT_ROOT/app/claims/graph_service.py"
check "get_claim method" "grep -q 'def get_claim' $PROJECT_ROOT/app/claims/graph_service.py"
check "update_claim_state method" "grep -q 'def update_claim_state' $PROJECT_ROOT/app/claims/graph_service.py"
check "add_entity method" "grep -q 'def add_entity' $PROJECT_ROOT/app/claims/graph_service.py"
check "add_relation method" "grep -q 'def add_relation' $PROJECT_ROOT/app/claims/graph_service.py"
check "link_claim_to_entity method" "grep -q 'def link_claim_to_entity' $PROJECT_ROOT/app/claims/graph_service.py"
check "add_support_relation method" "grep -q 'def add_support_relation' $PROJECT_ROOT/app/claims/graph_service.py"
check "add_opposition_relation method" "grep -q 'def add_opposition_relation' $PROJECT_ROOT/app/claims/graph_service.py"
check "bulk_add_claims method" "grep -q 'def bulk_add_claims' $PROJECT_ROOT/app/claims/graph_service.py"

# =============================================================================
# SECTION 4: Relation Inference
# =============================================================================
echo ""
echo "=== 5. Relation Inference ==="

check "RelationInference class exists" "grep -q 'class RelationInference' $PROJECT_ROOT/app/claims/relation_inference.py"
check "infer_relations method" "grep -q 'def infer_relations\|async def infer_relations' $PROJECT_ROOT/app/claims/relation_inference.py"
check "calculate_similarity method" "grep -q 'def.*similarity\|_calculate_similarity\|_semantic_similarity' $PROJECT_ROOT/app/claims/relation_inference.py"

# =============================================================================
# SECTION 5: Memory Controller (W2 tasks)
# =============================================================================
echo ""
echo "=== 6. Memory Controller ==="

check "MemoryController class exists" "grep -q 'class MemoryController' $PROJECT_ROOT/app/context/memory_controller.py"
check "remember method exists" "grep -q 'def remember' $PROJECT_ROOT/app/context/memory_controller.py"
check "recall method exists" "grep -q 'def recall' $PROJECT_ROOT/app/context/memory_controller.py"
check "forget method exists" "grep -q 'def forget' $PROJECT_ROOT/app/context/memory_controller.py"
check "build_context method exists" "grep -q 'def build_context' $PROJECT_ROOT/app/context/memory_controller.py"

echo ""
echo "=== 7. Memory Metrics ==="

check "MemoryMetrics class exists" "grep -q 'class MemoryMetrics' $PROJECT_ROOT/app/context/memory_metrics.py"
check "collect_metrics method" "grep -q 'def collect_metrics' $PROJECT_ROOT/app/context/memory_metrics.py"
check "get_health_report method" "grep -q 'def get_health_report' $PROJECT_ROOT/app/context/memory_metrics.py"
check "check_alerts method" "grep -q 'def check_alerts' $PROJECT_ROOT/app/context/memory_metrics.py"

# =============================================================================
# SECTION 6: Context Models & Service
# =============================================================================
echo ""
echo "=== 8. Context Models ==="

check "DossierClaim model exists" "grep -q 'class DossierClaim' $PROJECT_ROOT/app/context/models.py"
check "EntityContextDossier model exists" "grep -q 'class EntityContextDossier' $PROJECT_ROOT/app/context/models.py"
check "CaseContextDossier model exists" "grep -q 'class CaseContextDossier' $PROJECT_ROOT/app/context/models.py"

echo ""
echo "=== 9. Context Service ==="

check "build_case_dossier function exists" "grep -q 'def build_case_dossier' $PROJECT_ROOT/app/context/service.py"
check "build_entity_dossier function exists" "grep -q 'def build_entity_dossier' $PROJECT_ROOT/app/context/service.py"

# =============================================================================
# SECTION 7: Database Migrations
# =============================================================================
echo ""
echo "=== 10. Database Migrations ==="

check "ClaimGraph migration (S37)" "test -f $PROJECT_ROOT/db/migrations/027_sprint37_claimgraph.sql"
check "Claim relations migration (S38)" "test -f $PROJECT_ROOT/db/migrations/029_sprint38_claim_relations.sql"
warn_check "Policy versions migration (S38)" "test -f $PROJECT_ROOT/db/migrations/030_sprint38_policy_versions.sql"

# =============================================================================
# SECTION 8: Tests
# =============================================================================
echo ""
echo "=== 11. ClaimGraph Tests ==="

check "Graph models tests exist" "test -f $PROJECT_ROOT/tests/claims/test_claims_graph_models.py"
check "Graph repository tests exist" "test -f $PROJECT_ROOT/tests/claims/test_graph_repository.py"
check "Graph service tests exist" "test -f $PROJECT_ROOT/tests/claims/test_graph_service.py"
check "Topology metrics tests exist" "test -f $PROJECT_ROOT/tests/claims/test_topology_metrics.py"

echo ""
echo "=== 12. Context/Memory Tests ==="

check "Memory controller tests exist" "test -f $PROJECT_ROOT/tests/context/test_memory_controller.py"
check "Memory metrics tests exist" "test -f $PROJECT_ROOT/tests/context/test_memory_metrics.py"
check "Context dossiers tests exist" "test -f $PROJECT_ROOT/tests/context/test_context_dossiers.py"
check "Init lazy imports tests exist" "test -f $PROJECT_ROOT/tests/context/test_init_lazy_imports.py"

# =============================================================================
# SECTION 9: Run Tests
# =============================================================================
echo ""
echo "=== 13. Running Tests ==="
cd "$PROJECT_ROOT"

# Run claims + context tests
TEST_OUTPUT=$(PYTHONPATH=. .venv/bin/python -m pytest tests/claims/ tests/context/ -v --tb=short -q 2>&1 || true)
TEST_RESULT=$(echo "$TEST_OUTPUT" | tail -3)
echo "$TEST_RESULT"

if echo "$TEST_OUTPUT" | grep -q "passed"; then
    if echo "$TEST_OUTPUT" | grep -q "failed"; then
        FAIL=$((FAIL+1))
        echo -e "${RED}[FAIL]${NC} ClaimGraph + Context tests have failures"
    else
        PASS=$((PASS+1))
        echo -e "${GREEN}[PASS]${NC} ClaimGraph + Context tests pass"
    fi
else
    FAIL=$((FAIL+1))
    echo -e "${RED}[FAIL]${NC} Tests failed to run"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=========================================="
echo "Gate G16 Results"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Warnings: $WARN"
echo ""
echo "Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}Gate G16: FAILED${NC}"
    exit 1
fi
echo -e "${GREEN}Gate G16: PASSED${NC}"
