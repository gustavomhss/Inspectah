#!/usr/bin/env bash
# S38 Gate G12: Claims Relations
# Verifica implementacao completa do modulo de relacoes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "S38 Gate G12: Claims Relations"
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
echo "=== Relation Types ==="
check "relation_types.py exists" "test -f $PROJECT_ROOT/app/claims/relation_types.py"
check "RelationType enum exists" "grep -q 'class RelationType' $PROJECT_ROOT/app/claims/relation_types.py"
check "SUPPORTS type" "grep -q 'SUPPORTS' $PROJECT_ROOT/app/claims/relation_types.py"
check "CONTRADICTS type" "grep -q 'CONTRADICTS' $PROJECT_ROOT/app/claims/relation_types.py"
check "DUPLICATE type" "grep -q 'DUPLICATE' $PROJECT_ROOT/app/claims/relation_types.py"
check "ClaimRelation dataclass" "grep -q 'class ClaimRelation' $PROJECT_ROOT/app/claims/relation_types.py"

echo ""
echo "=== Relation Inference ==="
check "relation_inference.py exists" "test -f $PROJECT_ROOT/app/claims/relation_inference.py"
check "RelationInferenceService exists" "grep -q 'class RelationInferenceService' $PROJECT_ROOT/app/claims/relation_inference.py"
check "infer_relations method" "grep -q 'def infer_relations' $PROJECT_ROOT/app/claims/relation_inference.py"
check "cosine_similarity method" "grep -q '_cosine_similarity' $PROJECT_ROOT/app/claims/relation_inference.py"
check "detect_contradiction method" "grep -q '_detect_contradiction' $PROJECT_ROOT/app/claims/relation_inference.py"

echo ""
echo "=== Claims API ==="
check "Claims API router exists" "grep -q 'router = APIRouter' $PROJECT_ROOT/app/api/claims_routes.py"
check "POST /relations/infer endpoint" "grep -q 'infer_relations' $PROJECT_ROOT/app/api/claims_routes.py"
check "POST /relations/similar endpoint" "grep -q 'find_similar' $PROJECT_ROOT/app/api/claims_routes.py"
check "POST /cluster endpoint" "grep -q 'cluster' $PROJECT_ROOT/app/api/claims_routes.py"

echo ""
echo "=========================================="
echo "Gate G12 Results: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
echo "Gate G12: PASSED"
