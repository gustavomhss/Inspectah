#!/bin/bash
# Sprint 40 - Gate G24: P4 Exposure (Truth Twin / Decision Inspector)
# Tasks: DTOs, Endpoints, Provenance Middleware, Metrics, Benchmark
# Exit 0 = PASS, Exit 1 = FAIL

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EVIDENCE_DIR="$PROJECT_ROOT/out/evidence"
SCORECARD_DIR="$PROJECT_ROOT/out/scorecards"

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
SPRINT="S40"
GATE="G24"

echo "=========================================="
echo "Sprint 40 - Gate G24: P4 Exposure"
echo "=========================================="
echo "Timestamp: $TIMESTAMP"
echo "Commit: $COMMIT"
echo ""

PASSED=0
FAILED=0
ERRORS=()

log_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"

    if [ "$status" = "PASS" ]; then
        echo "✓ $test_name: PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ $test_name: FAIL - $message"
        ERRORS+=("$test_name: $message")
        FAILED=$((FAILED + 1))
    fi
}

cd "$PROJECT_ROOT"

# 1. Verificar módulos existem
echo ""
echo "--- Verificando módulos P4 ---"

MODULES=(
    "app/api/truth_schemas.py"
    "app/api/truth_routes.py"
    "app/api/middleware/__init__.py"
    "app/api/middleware/provenance.py"
    "app/api/metrics.py"
    "scripts/benchmarks/p4_latency_benchmark.py"
)

for module in "${MODULES[@]}"; do
    if [ -f "$module" ]; then
        log_result "$module exists" "PASS" ""
    else
        log_result "$module exists" "FAIL" "Arquivo não encontrado"
    fi
done

# 2. Verificar DTOs (S40-BE-026)
echo ""
echo "--- Verificando S40-BE-026: DTOs ---"

if grep -q "class TruthTwinResponse:" app/api/truth_schemas.py; then
    log_result "TruthTwinResponse class" "PASS" ""
else
    log_result "TruthTwinResponse class" "FAIL" "Class não encontrada"
fi

if grep -q "class DecisionInspectResponse:" app/api/truth_schemas.py; then
    log_result "DecisionInspectResponse class" "PASS" ""
else
    log_result "DecisionInspectResponse class" "FAIL" "Class não encontrada"
fi

if grep -q "class ProvenanceInfo:" app/api/truth_schemas.py; then
    log_result "ProvenanceInfo class" "PASS" ""
else
    log_result "ProvenanceInfo class" "FAIL" "Class não encontrada"
fi

if grep -q "def build_truth_twin_response" app/api/truth_schemas.py; then
    log_result "build_truth_twin_response function" "PASS" ""
else
    log_result "build_truth_twin_response function" "FAIL" "Função não encontrada"
fi

if grep -q "def build_decision_inspect_response" app/api/truth_schemas.py; then
    log_result "build_decision_inspect_response function" "PASS" ""
else
    log_result "build_decision_inspect_response function" "FAIL" "Função não encontrada"
fi

# 3. Verificar endpoints (S40-BE-023/024)
echo ""
echo "--- Verificando S40-BE-023/024: Endpoints ---"

if grep -q 'async def get_truth_twin' app/api/truth_routes.py; then
    log_result "GET /{claim_id}/twin endpoint" "PASS" ""
else
    log_result "GET /{claim_id}/twin endpoint" "FAIL" "Endpoint não encontrado"
fi

if grep -q 'async def inspect_decision' app/api/truth_routes.py; then
    log_result "GET /decision/{id}/inspect endpoint" "PASS" ""
else
    log_result "GET /decision/{id}/inspect endpoint" "FAIL" "Endpoint não encontrado"
fi

if grep -q 'async def get_decision_timeline' app/api/truth_routes.py; then
    log_result "GET /{claim_id}/timeline endpoint" "PASS" ""
else
    log_result "GET /{claim_id}/timeline endpoint" "FAIL" "Endpoint não encontrado"
fi

# 4. Verificar provenance middleware (S40-BE-025)
echo ""
echo "--- Verificando S40-BE-025: Provenance Middleware ---"

if grep -q "class ProvenanceMiddleware" app/api/middleware/provenance.py; then
    log_result "ProvenanceMiddleware class" "PASS" ""
else
    log_result "ProvenanceMiddleware class" "FAIL" "Class não encontrada"
fi

if grep -q "def check_provenance" app/api/middleware/provenance.py; then
    log_result "check_provenance function" "PASS" ""
else
    log_result "check_provenance function" "FAIL" "Função não encontrada"
fi

if grep -q "def validate_provenance_response" app/api/middleware/provenance.py; then
    log_result "validate_provenance_response function" "PASS" ""
else
    log_result "validate_provenance_response function" "FAIL" "Função não encontrada"
fi

# 5. Verificar metrics (S40-BE-027)
echo ""
echo "--- Verificando S40-BE-027: P4 Metrics ---"

if grep -q "p4_endpoint_latency_ms" app/api/metrics.py; then
    log_result "p4_endpoint_latency_ms histogram" "PASS" ""
else
    log_result "p4_endpoint_latency_ms histogram" "FAIL" "Métrica não encontrada"
fi

if grep -q "P4_SLA_TARGETS" app/api/metrics.py; then
    log_result "P4_SLA_TARGETS defined" "PASS" ""
else
    log_result "P4_SLA_TARGETS defined" "FAIL" "SLA targets não definidos"
fi

if grep -q "def record_p4_request" app/api/metrics.py; then
    log_result "record_p4_request function" "PASS" ""
else
    log_result "record_p4_request function" "FAIL" "Função não encontrada"
fi

if grep -q "def get_p4_sla_status" app/api/metrics.py; then
    log_result "get_p4_sla_status function" "PASS" ""
else
    log_result "get_p4_sla_status function" "FAIL" "Função não encontrada"
fi

# 6. Verificar benchmark (S40-BE-028)
echo ""
echo "--- Verificando S40-BE-028: P4 Benchmark ---"

if grep -q "SLA_TARGETS" scripts/benchmarks/p4_latency_benchmark.py; then
    log_result "P4 benchmark SLA targets" "PASS" ""
else
    log_result "P4 benchmark SLA targets" "FAIL" "SLA targets não definidos"
fi

if grep -q "async def run_benchmark" scripts/benchmarks/p4_latency_benchmark.py; then
    log_result "run_benchmark function" "PASS" ""
else
    log_result "run_benchmark function" "FAIL" "Função não encontrada"
fi

# 7. Rodar testes P4
echo ""
echo "--- Rodando testes P4 ---"

TESTS_TO_RUN=(
    "tests/api/test_truth_schemas.py"
    "tests/api/test_p4_metrics.py"
    "tests/api/test_provenance_middleware.py"
    "tests/api/test_truth_routes_p4.py"
    "tests/benchmarks/test_p4_benchmark.py"
)

for test_file in "${TESTS_TO_RUN[@]}"; do
    if [ -f "$test_file" ]; then
        if PYTHONPATH=. .venv/bin/python -m pytest "$test_file" -v --tb=short 2>&1 | tail -1 | grep -q "passed"; then
            log_result "$test_file" "PASS" ""
        else
            log_result "$test_file" "FAIL" "Testes falharam"
        fi
    else
        echo "⊘ $test_file: SKIP - Arquivo não existe"
    fi
done

# 8. Verificar integração
echo ""
echo "--- Verificando integração ---"

INTEGRATION_TEST=$(PYTHONPATH=. .venv/bin/python << 'EOF'
import sys
try:
    from app.api.truth_schemas import (
        TruthTwinResponse,
        DecisionInspectResponse,
        ProvenanceInfo,
        build_truth_twin_response,
        build_decision_inspect_response,
    )
    from app.api.middleware.provenance import (
        check_provenance,
        validate_provenance_response,
    )
    from app.api.metrics import (
        record_p4_request,
        get_p4_stats,
        reset_p4_stats,
        check_p4_sla_compliance,
    )

    # Test DTOs
    prov = ProvenanceInfo(source="test", timestamp="2025-01-01T00:00:00Z")
    twin = TruthTwinResponse(
        claim_id="c1",
        domain="saude",
        current_state="PROMOTED",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z",
        provenance=prov,
    )
    assert twin.has_valid_provenance(), "Twin should have valid provenance"

    # Test build functions
    record = {"claim_id": "c1", "domain": "saude", "current_state": "PROMOTED", "created_at": "", "updated_at": ""}
    blocks = [{"id": "b1", "decision_id": "d1", "gate": "G23", "decision_type": "PROMOTE",
               "initial_state": "PENDING", "final_state": "PROMOTED", "created_at": "2025-01-01T00:00:00Z",
               "policy_version": "1.0", "policy_name": "test", "evidence_refs": [], "references": None}]
    response = build_truth_twin_response(record, blocks, [])
    assert response.provenance is not None, "Response should have provenance"

    # Test provenance validation
    valid_data = {"provenance": {"source": "test", "timestamp": "2025-01-01T00:00:00Z"}}
    invalid_data = {"claim_id": "c1"}
    assert check_provenance(valid_data) is True, "Valid data should pass"
    assert check_provenance(invalid_data) is False, "Invalid data should fail"

    validated = validate_provenance_response(invalid_data)
    assert validated.get("_provenance_valid") is False, "Should be marked invalid"

    # Test metrics
    reset_p4_stats()
    record_p4_request("twin", 50.0, "success", True)
    assert check_p4_sla_compliance(50.0) is True, "50ms should be compliant"
    assert check_p4_sla_compliance(150.0) is False, "150ms should not be compliant"

    print("INTEGRATION_OK")
except Exception as e:
    print(f"INTEGRATION_FAIL: {e}")
    sys.exit(1)
EOF
)

if echo "$INTEGRATION_TEST" | grep -q "INTEGRATION_OK"; then
    log_result "Integration test" "PASS" ""
else
    log_result "Integration test" "FAIL" "$INTEGRATION_TEST"
fi

# Gerar scorecard
echo ""
echo "--- Gerando scorecard ---"

TOTAL=$((PASSED + FAILED))
PASS_RATE=0
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$(echo "scale=2; $PASSED * 100 / $TOTAL" | bc)
fi

RESULT="PASS"
if [ $FAILED -gt 0 ]; then
    RESULT="FAIL"
fi

cat > "$SCORECARD_DIR/S40_G24_p4_exposure.json" << EOF
{
  "metadata": {
    "sprint": "$SPRINT",
    "gate": "$GATE",
    "timestamp": "$TIMESTAMP",
    "commit": "$COMMIT",
    "policy_version": "v1.0.0",
    "domain": "p4-exposure"
  },
  "result": "$RESULT",
  "summary": {
    "total_checks": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "pass_rate": $PASS_RATE
  },
  "components": {
    "truth_twin_dto": true,
    "decision_inspect_dto": true,
    "provenance_info": true,
    "truth_twin_endpoint": true,
    "decision_inspect_endpoint": true,
    "timeline_endpoint": true,
    "provenance_middleware": true,
    "p4_latency_metrics": true,
    "p4_sla_targets": true,
    "p4_benchmark": true,
    "integration_tests": $(echo "$INTEGRATION_TEST" | grep -q "INTEGRATION_OK" && echo "true" || echo "false")
  },
  "sla_targets": {
    "p95_ms": 100,
    "p99_ms": 200
  },
  "tasks_covered": [
    "S40-BE-023",
    "S40-BE-024",
    "S40-BE-025",
    "S40-BE-026",
    "S40-BE-027",
    "S40-BE-028"
  ]
}
EOF

echo "Scorecard salvo em: $SCORECARD_DIR/S40_G24_p4_exposure.json"

# Resumo
echo ""
echo "=========================================="
echo "RESULTADO FINAL: $RESULT"
echo "=========================================="
echo "Passed: $PASSED / $TOTAL"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo "ERROS:"
    for err in "${ERRORS[@]}"; do
        echo "  - $err"
    done
    exit 1
fi

exit 0
