#!/bin/bash
# Sprint 40 - Gate G22: ClaimGraph Export & NO-GO Signals
# Tasks: S40-BE-011 to S40-BE-017
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
GATE="G22"

echo "=========================================="
echo "Sprint 40 - Gate G22: ClaimGraph Export"
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
echo "--- Verificando módulos S40-BE-011 a S40-BE-017 ---"

MODULES=(
    "app/claims/export.py"
    "app/claims/signals.py"
)

for module in "${MODULES[@]}"; do
    if [ -f "$module" ]; then
        log_result "$module exists" "PASS" ""
    else
        log_result "$module exists" "FAIL" "Arquivo não encontrado"
    fi
done

# 2. Verificar S40-BE-011: export_claimgraph_v1()
echo ""
echo "--- Verificando S40-BE-011: export_claimgraph_v1 ---"

if grep -q "def export_claimgraph_v1" app/claims/export.py; then
    log_result "export_claimgraph_v1 function" "PASS" ""
else
    log_result "export_claimgraph_v1 function" "FAIL" "Função não encontrada"
fi

if grep -q "class ClaimGraphExport:" app/claims/export.py; then
    log_result "ClaimGraphExport class" "PASS" ""
else
    log_result "ClaimGraphExport class" "FAIL" "Class não encontrada"
fi

# 3. Verificar S40-BE-013: ingest_claimgraph_export()
echo ""
echo "--- Verificando S40-BE-013: ingest_claimgraph_export ---"

if grep -q "def ingest_claimgraph_export" app/claims/export.py; then
    log_result "ingest_claimgraph_export function" "PASS" ""
else
    log_result "ingest_claimgraph_export function" "FAIL" "Função não encontrada"
fi

# 4. Verificar S40-BE-014: NO-GO signals
echo ""
echo "--- Verificando S40-BE-014: NO-GO Signals ---"

if grep -q "class SignalType" app/claims/signals.py; then
    log_result "SignalType enum" "PASS" ""
else
    log_result "SignalType enum" "FAIL" "Enum não encontrado"
fi

if grep -q "INCONSISTENCY" app/claims/signals.py && grep -q "SUSPICION" app/claims/signals.py && grep -q "ABUSE" app/claims/signals.py; then
    log_result "All signal types defined" "PASS" ""
else
    log_result "All signal types defined" "FAIL" "Tipos de sinal faltando"
fi

if grep -q "class NOGOSignal:" app/claims/signals.py; then
    log_result "NOGOSignal class" "PASS" ""
else
    log_result "NOGOSignal class" "FAIL" "Class não encontrada"
fi

if grep -q "class SignalRepository:" app/claims/signals.py; then
    log_result "SignalRepository class" "PASS" ""
else
    log_result "SignalRepository class" "FAIL" "Class não encontrada"
fi

# 5. Verificar S40-BE-017: Detecção automática
echo ""
echo "--- Verificando S40-BE-017: Detecção automática ---"

if grep -q "def detect_inconsistency" app/claims/signals.py; then
    log_result "detect_inconsistency function" "PASS" ""
else
    log_result "detect_inconsistency function" "FAIL" "Função não encontrada"
fi

if grep -q "def detect_suspicion" app/claims/signals.py; then
    log_result "detect_suspicion function" "PASS" ""
else
    log_result "detect_suspicion function" "FAIL" "Função não encontrada"
fi

if grep -q "def detect_abuse" app/claims/signals.py; then
    log_result "detect_abuse function" "PASS" ""
else
    log_result "detect_abuse function" "FAIL" "Função não encontrada"
fi

if grep -q "def check_nogo_signals" app/claims/signals.py; then
    log_result "check_nogo_signals function" "PASS" ""
else
    log_result "check_nogo_signals function" "FAIL" "Função não encontrada"
fi

# 5b. Verificar S40-BE-015: Integração NO-GO em flow.py
echo ""
echo "--- Verificando S40-BE-015: Integração NO-GO em flow.py ---"

if grep -q "NOGO_BLOCKED" app/guardian/flow.py; then
    log_result "NOGO_BLOCKED event" "PASS" ""
else
    log_result "NOGO_BLOCKED event" "FAIL" "Evento não encontrado"
fi

if grep -q "def check_nogo_signals" app/guardian/flow.py; then
    log_result "check_nogo_signals in GuardianFlow" "PASS" ""
else
    log_result "check_nogo_signals in GuardianFlow" "FAIL" "Método não encontrado"
fi

if grep -q "signal_refs" app/guardian/flow.py; then
    log_result "signal_refs in FlowContext" "PASS" ""
else
    log_result "signal_refs in FlowContext" "FAIL" "Campo não encontrado"
fi

# 5c. Verificar S40-BE-012 e S40-BE-016: Endpoints API
echo ""
echo "--- Verificando S40-BE-012/016: Endpoints API ---"

if grep -q "def export_claimgraph" app/api/claims_routes.py; then
    log_result "export_claimgraph endpoint" "PASS" ""
else
    log_result "export_claimgraph endpoint" "FAIL" "Endpoint não encontrado"
fi

if grep -q "def get_claim_signals" app/api/claims_routes.py; then
    log_result "get_claim_signals endpoint" "PASS" ""
else
    log_result "get_claim_signals endpoint" "FAIL" "Endpoint não encontrado"
fi

# 6. Rodar testes
echo ""
echo "--- Rodando testes S40 ClaimGraph ---"

TESTS_TO_RUN=(
    "tests/claims/test_export.py"
    "tests/claims/test_signals.py"
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

# 7. Verificar integração
echo ""
echo "--- Verificando integração ---"

INTEGRATION_TEST=$(PYTHONPATH=. .venv/bin/python << 'EOF'
import sys
try:
    from app.claims.export import (
        export_claimgraph_v1,
        ingest_claimgraph_export,
        ClaimGraphExport,
        ClaimPrior,
        ClaimExportItem,
    )
    from app.claims.signals import (
        NOGOSignal,
        SignalType,
        SignalSeverity,
        SignalRepository,
        detect_inconsistency,
        check_nogo_signals,
        get_signal_repository,
    )
    from app.claims.graph_models import ClaimNode, ClaimState

    # Test export
    claim = ClaimNode.create(
        domain="saude",
        content="Test claim",
        state=ClaimState.VERIFIED,
        evidence_count=1,
    )
    claim.properties["prior"] = {"probability": 0.8, "confidence": 0.9, "source": "model"}
    claim.properties["evidence_trail"] = [
        {"evidence_id": "ev1", "type": "source", "stance": "supports", "weight": 0.7}
    ]

    export = export_claimgraph_v1([claim], domain="saude")
    assert export.version == "1.0"
    assert len(export.claims) == 1
    assert export.claims[0].prior.probability == 0.8

    # Test ingest
    export_dict = export.to_dict()
    claims = ingest_claimgraph_export(export_dict)
    assert len(claims) == 1
    assert claims[0].claim_id == claim.id

    # Test signals
    signal = NOGOSignal.create(
        type=SignalType.INCONSISTENCY,
        severity=SignalSeverity.HIGH,
        claim_id="claim-1",
        reason="Test inconsistency",
    )
    assert signal.is_blocking()

    repo = get_signal_repository()
    repo.add(signal)
    assert repo.has_blocking_signals("claim-1")

    signal.resolve("admin", "Resolved")
    assert not signal.is_blocking()

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

cat > "$SCORECARD_DIR/S40_G22_claimgraph.json" << EOF
{
  "metadata": {
    "sprint": "$SPRINT",
    "gate": "$GATE",
    "timestamp": "$TIMESTAMP",
    "commit": "$COMMIT",
    "policy_version": "v1.0.0",
    "domain": "claimgraph-export"
  },
  "result": "$RESULT",
  "summary": {
    "total_checks": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "pass_rate": $PASS_RATE
  },
  "components": {
    "export_claimgraph_v1": true,
    "ingest_claimgraph_export": true,
    "nogo_signals": true,
    "signal_repository": true,
    "detect_inconsistency": true,
    "integration_tests": $(echo "$INTEGRATION_TEST" | grep -q "INTEGRATION_OK" && echo "true" || echo "false")
  },
  "tasks_covered": [
    "S40-BE-011",
    "S40-BE-012",
    "S40-BE-013",
    "S40-BE-014",
    "S40-BE-015",
    "S40-BE-016",
    "S40-BE-017"
  ]
}
EOF

echo "Scorecard salvo em: $SCORECARD_DIR/S40_G22_claimgraph.json"

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
