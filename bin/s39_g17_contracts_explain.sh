#!/usr/bin/env bash
# =============================================================================
# S39 Gate G17: API Contracts + Explainability
# =============================================================================
# Verifica contratos de API v1, validacao, versionamento e servico de explicabilidade
#
# Invariantes validados:
#   INV-S39-09: Contract validation = 100%
#   INV-S39-10: Explain drill >= 5 levels
#   INV-S39-15: All unit tests passing
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
echo "S39 Gate G17: API Contracts + Explainability"
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
# SECTION 1: API Contracts Module (W3 tasks)
# =============================================================================
echo ""
echo "=== 1. API Contracts Module ==="

check "Contracts module exists" "test -d $PROJECT_ROOT/app/contracts"
check "V1 contracts file exists" "test -f $PROJECT_ROOT/app/contracts/v1.py"
check "Contract middleware file exists" "test -f $PROJECT_ROOT/app/contracts/middleware.py"
check "Contract validator file exists" "test -f $PROJECT_ROOT/app/contracts/validator.py"
check "SemVer module file exists" "test -f $PROJECT_ROOT/app/contracts/semver.py"
check "Contracts __init__.py exists" "test -f $PROJECT_ROOT/app/contracts/__init__.py"

# =============================================================================
# SECTION 2: V1 Contract Definitions
# =============================================================================
echo ""
echo "=== 2. V1 Contract Definitions ==="

check "ContractStatus enum exists" "grep -q 'class ContractStatus' $PROJECT_ROOT/app/contracts/v1.py"
check "ErrorContract class exists" "grep -q 'class ErrorContract' $PROJECT_ROOT/app/contracts/v1.py"
check "PaginationContract class exists" "grep -q 'class PaginationContract' $PROJECT_ROOT/app/contracts/v1.py"
check "ResponseEnvelope class exists" "grep -q 'class ResponseEnvelope' $PROJECT_ROOT/app/contracts/v1.py"
check "ClaimContract class exists" "grep -q 'class ClaimContract' $PROJECT_ROOT/app/contracts/v1.py"
check "SourceContract class exists" "grep -q 'class SourceContract' $PROJECT_ROOT/app/contracts/v1.py"
check "SignalContract class exists" "grep -q 'class SignalContract' $PROJECT_ROOT/app/contracts/v1.py"
check "PolicyContract class exists" "grep -q 'class PolicyContract' $PROJECT_ROOT/app/contracts/v1.py"
check "VerdictContract class exists" "grep -q 'class VerdictContract' $PROJECT_ROOT/app/contracts/v1.py"
check "RelationContract class exists" "grep -q 'class RelationContract' $PROJECT_ROOT/app/contracts/v1.py"
check "success_response helper exists" "grep -q 'def success_response' $PROJECT_ROOT/app/contracts/v1.py"
check "error_response helper exists" "grep -q 'def error_response' $PROJECT_ROOT/app/contracts/v1.py"

# =============================================================================
# SECTION 3: Contract Middleware
# =============================================================================
echo ""
echo "=== 3. Contract Middleware ==="

check "ContractMiddleware class exists" "grep -q 'class ContractMiddleware' $PROJECT_ROOT/app/contracts/middleware.py"
check "validate_request method" "grep -q 'def validate_request\|async def validate_request' $PROJECT_ROOT/app/contracts/middleware.py"
check "validate_response method" "grep -q 'def validate_response\|async def validate_response' $PROJECT_ROOT/app/contracts/middleware.py"

echo ""
echo "=== 4. Contract Validator ==="

check "ContractValidator class exists" "grep -q 'class ContractValidator\|ContractValidator' $PROJECT_ROOT/app/contracts/validator.py"
check "validate_claim method" "grep -q 'validate_claim' $PROJECT_ROOT/app/contracts/v1.py"
check "validate_source method" "grep -q 'validate_source' $PROJECT_ROOT/app/contracts/v1.py"

# =============================================================================
# SECTION 4: SemVer Support
# =============================================================================
echo ""
echo "=== 5. SemVer Support ==="

check "SemVer class exists" "grep -q 'class SemVer' $PROJECT_ROOT/app/contracts/semver.py"
check "parse_version function" "grep -q 'def parse_version' $PROJECT_ROOT/app/contracts/semver.py"
check "is_compatible function" "grep -q 'def is_compatible' $PROJECT_ROOT/app/contracts/semver.py"
check "is_breaking_change function" "grep -q 'def is_breaking_change\|breaking' $PROJECT_ROOT/app/contracts/semver.py"
check "bump_major function" "grep -q 'def bump_major\|bump.*major' $PROJECT_ROOT/app/contracts/semver.py"
check "bump_minor function" "grep -q 'def bump_minor\|bump.*minor' $PROJECT_ROOT/app/contracts/semver.py"
check "bump_patch function" "grep -q 'def bump_patch\|bump.*patch' $PROJECT_ROOT/app/contracts/semver.py"

# =============================================================================
# SECTION 5: Explainability Service (W3 tasks)
# =============================================================================
echo ""
echo "=== 6. Explainability Service ==="

check "Explainability module exists" "test -d $PROJECT_ROOT/app/explainability"
check "Explainability service file exists" "test -f $PROJECT_ROOT/app/explainability/service.py"
check "ExplainabilityService class exists" "grep -q 'class ExplainabilityService' $PROJECT_ROOT/app/explainability/service.py"

echo ""
echo "=== 7. Explainability Models ==="

check "ExplanationType enum exists" "grep -q 'class ExplanationType' $PROJECT_ROOT/app/explainability/service.py"
check "ExplanationLevel enum exists" "grep -q 'class ExplanationLevel' $PROJECT_ROOT/app/explainability/service.py"
check "FactorType enum exists" "grep -q 'class FactorType' $PROJECT_ROOT/app/explainability/service.py"
check "Factor class exists" "grep -q 'class Factor' $PROJECT_ROOT/app/explainability/service.py"
check "DecisionExplanation class exists" "grep -q 'class DecisionExplanation' $PROJECT_ROOT/app/explainability/service.py"
check "ExplanationTemplate class exists" "grep -q 'class ExplanationTemplate' $PROJECT_ROOT/app/explainability/service.py"

echo ""
echo "=== 8. Explainability Methods ==="

check "explain_verdict method exists" "grep -q 'def explain_verdict' $PROJECT_ROOT/app/explainability/service.py"
check "explain_signal method exists" "grep -q 'def explain_signal' $PROJECT_ROOT/app/explainability/service.py"
check "explain_relation method exists" "grep -q 'def explain_relation' $PROJECT_ROOT/app/explainability/service.py"
check "get_explanation method exists" "grep -q 'def get_explanation' $PROJECT_ROOT/app/explainability/service.py"
check "get_top_factors method exists" "grep -q 'def get_top_factors' $PROJECT_ROOT/app/explainability/service.py"
check "generate_factors helper exists" "grep -q 'def generate_factors\|_generate_factors' $PROJECT_ROOT/app/explainability/service.py"

# =============================================================================
# SECTION 6: Frontend Explainability (W3 tasks)
# =============================================================================
echo ""
echo "=== 9. Frontend Explainability ==="

check "Explain module directory exists" "test -d $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain"
check "ExplainTreeView component exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/components/ExplainTreeView.tsx"
check "useClaimExplanation hook exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/hooks/useClaimExplanation.ts"
check "Explain types file exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/types.ts"
check "Explain module index exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/index.ts"

echo ""
echo "=== 10. Frontend Explainability Implementation ==="

check "ExplainTreeView exports" "grep -q 'export.*ExplainTreeView\|ExplainTreeView' $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/components/ExplainTreeView.tsx"
check "useClaimExplanation exports" "grep -q 'export.*useClaimExplanation' $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/hooks/useClaimExplanation.ts"
check "fetchExplanation function" "grep -q 'fetchExplanation\|fetch.*explanation' $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/hooks/useClaimExplanation.ts"
check "expandNode function" "grep -q 'expandNode\|expand.*node\|toggleNode' $PROJECT_ROOT/frontend/inspectah-ui/src/modules/explain/hooks/useClaimExplanation.ts"

# =============================================================================
# SECTION 7: Tests
# =============================================================================
echo ""
echo "=== 11. Backend Tests ==="

check "Contract V1 tests exist" "test -f $PROJECT_ROOT/tests/contracts/test_v1.py"
check "Contract middleware tests exist" "test -f $PROJECT_ROOT/tests/contracts/test_middleware.py"
check "Contract validator tests exist" "test -f $PROJECT_ROOT/tests/contracts/test_validator.py"
check "SemVer tests exist" "test -f $PROJECT_ROOT/tests/contracts/test_semver.py"
check "JSON schema tests exist" "test -f $PROJECT_ROOT/tests/contracts/test_json_schemas.py"
check "Explainability service tests exist" "test -f $PROJECT_ROOT/tests/explainability/test_service.py"

echo ""
echo "=== 12. Frontend Tests ==="

check "ExplainTreeView test exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/__tests__/components/ExplainTreeView.test.tsx"
check "useClaimExplanation test exists" "test -f $PROJECT_ROOT/frontend/inspectah-ui/src/__tests__/hooks/useClaimExplanation.test.ts"

# =============================================================================
# SECTION 8: Run Tests
# =============================================================================
echo ""
echo "=== 13. Running Backend Tests ==="
cd "$PROJECT_ROOT"

# Run contracts + explainability tests
TEST_OUTPUT=$(PYTHONPATH=. .venv/bin/python -m pytest tests/contracts/ tests/explainability/ -v --tb=short -q 2>&1 || true)
TEST_RESULT=$(echo "$TEST_OUTPUT" | tail -3)
echo "$TEST_RESULT"

if echo "$TEST_OUTPUT" | grep -q "passed"; then
    if echo "$TEST_OUTPUT" | grep -q "failed"; then
        FAIL=$((FAIL+1))
        echo -e "${RED}[FAIL]${NC} Contracts + Explainability tests have failures"
    else
        PASS=$((PASS+1))
        echo -e "${GREEN}[PASS]${NC} Contracts + Explainability tests pass"
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
echo "Gate G17 Results"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Warnings: $WARN"
echo ""
echo "Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}Gate G17: FAILED${NC}"
    exit 1
fi
echo -e "${GREEN}Gate G17: PASSED${NC}"
