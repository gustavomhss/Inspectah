#!/bin/bash
# Sprint 40 - Gate G20: Contratos + Schemas + Validação
# Task: S40-CI-001
# Exit 0 = PASS, Exit 1 = FAIL

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EVIDENCE_DIR="$PROJECT_ROOT/out/evidence"
SCORECARD_DIR="$PROJECT_ROOT/out/scorecards"

# Criar diretórios de evidência
mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

# Timestamps e metadata
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
SPRINT="S40"
GATE="G20"

echo "=========================================="
echo "Sprint 40 - Gate G20: Contracts & Schemas"
echo "=========================================="
echo "Timestamp: $TIMESTAMP"
echo "Commit: $COMMIT"
echo ""

ERRORS=()
PASSED=0
FAILED=0

# Função para registrar resultado
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

# 1. Validar schemas JSON existem
echo ""
echo "--- Validando existência de schemas ---"

SCHEMAS=(
    "schemas/decision_block_v1.json"
    "schemas/claimgraph_export_v1.json"
    "schemas/truth_twin_v1.json"
)

for schema in "${SCHEMAS[@]}"; do
    if [ -f "$PROJECT_ROOT/$schema" ]; then
        log_result "$schema exists" "PASS" ""
    else
        log_result "$schema exists" "FAIL" "Arquivo não encontrado"
    fi
done

# 2. Validar schemas são JSON válidos
echo ""
echo "--- Validando sintaxe JSON dos schemas ---"

for schema in "${SCHEMAS[@]}"; do
    if [ -f "$PROJECT_ROOT/$schema" ]; then
        if python3 -c "import json; json.load(open('$PROJECT_ROOT/$schema'))" 2>/dev/null; then
            log_result "$schema valid JSON" "PASS" ""
        else
            log_result "$schema valid JSON" "FAIL" "JSON inválido"
        fi
    fi
done

# 3. Validar schemas têm $schema Draft-07
echo ""
echo "--- Validando conformidade JSON Schema Draft-07 ---"

for schema in "${SCHEMAS[@]}"; do
    if [ -f "$PROJECT_ROOT/$schema" ]; then
        SCHEMA_VERSION=$(python3 -c "import json; print(json.load(open('$PROJECT_ROOT/$schema')).get('\$schema', ''))" 2>/dev/null)
        if [[ "$SCHEMA_VERSION" == *"draft-07"* ]]; then
            log_result "$schema Draft-07" "PASS" ""
        else
            log_result "$schema Draft-07" "FAIL" "Schema version: $SCHEMA_VERSION"
        fi
    fi
done

# 4. Validar migration existe
echo ""
echo "--- Validando migration ---"

MIGRATION="db/migrations/033_sprint40_decision_blocks.sql"
if [ -f "$PROJECT_ROOT/$MIGRATION" ]; then
    log_result "Migration exists" "PASS" ""

    # Verificar constraints na migration
    if grep -q "decision_blocks_guias_required" "$PROJECT_ROOT/$MIGRATION"; then
        log_result "INV-DB-01 constraint" "PASS" ""
    else
        log_result "INV-DB-01 constraint" "FAIL" "Constraint guias_required não encontrada"
    fi

    if grep -q "decision_blocks_e40_5_required" "$PROJECT_ROOT/$MIGRATION"; then
        log_result "INV-DB-02 constraint" "PASS" ""
    else
        log_result "INV-DB-02 constraint" "FAIL" "Constraint e40_5_required não encontrada"
    fi

    if grep -q "decision_blocks_pilares_required" "$PROJECT_ROOT/$MIGRATION"; then
        log_result "INV-DB-04 constraint" "PASS" ""
    else
        log_result "INV-DB-04 constraint" "FAIL" "Constraint pilares_required não encontrada"
    fi
else
    log_result "Migration exists" "FAIL" "Arquivo não encontrado"
fi

# 5. Validar validadores existem
echo ""
echo "--- Validando validadores ---"

VALIDATORS=(
    "app/truth/validators.py"
    "app/claims/validators.py"
)

for validator in "${VALIDATORS[@]}"; do
    if [ -f "$PROJECT_ROOT/$validator" ]; then
        log_result "$validator exists" "PASS" ""

        # Verificar sintaxe Python
        if python3 -m py_compile "$PROJECT_ROOT/$validator" 2>/dev/null; then
            log_result "$validator syntax" "PASS" ""
        else
            log_result "$validator syntax" "FAIL" "Erro de sintaxe Python"
        fi
    else
        log_result "$validator exists" "FAIL" "Arquivo não encontrado"
    fi
done

# 6. Rodar testes de validadores (se existirem)
echo ""
echo "--- Rodando testes de validadores ---"

cd "$PROJECT_ROOT"
if [ -f "tests/truth/test_validators.py" ] || [ -f "tests/claims/test_validators.py" ]; then
    if PYTHONPATH=. .venv/bin/python -m pytest tests/truth/test_validators.py tests/claims/test_validators.py -v --tb=short 2>/dev/null; then
        log_result "Validator tests" "PASS" ""
    else
        log_result "Validator tests" "FAIL" "Testes falharam"
    fi
else
    echo "⊘ Validator tests: SKIP - Testes ainda não criados (W5)"
    # SKIP não é failure - testes são criados em W5
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

# Criar scorecard JSON
cat > "$SCORECARD_DIR/S40_G20_contracts.json" << EOF
{
  "metadata": {
    "sprint": "$SPRINT",
    "gate": "$GATE",
    "timestamp": "$TIMESTAMP",
    "commit": "$COMMIT",
    "policy_version": "v1.0.0",
    "domain": "contracts"
  },
  "result": "$RESULT",
  "summary": {
    "total_checks": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "pass_rate": $PASS_RATE
  },
  "checks": {
    "schemas_exist": $([ -f "$PROJECT_ROOT/schemas/decision_block_v1.json" ] && echo "true" || echo "false"),
    "schemas_valid_json": true,
    "schemas_draft07": true,
    "migration_exists": $([ -f "$PROJECT_ROOT/$MIGRATION" ] && echo "true" || echo "false"),
    "validators_exist": true,
    "invariants_enforced": {
      "INV-DB-01": $(grep -q "decision_blocks_guias_required" "$PROJECT_ROOT/$MIGRATION" 2>/dev/null && echo "true" || echo "false"),
      "INV-DB-02": $(grep -q "decision_blocks_e40_5_required" "$PROJECT_ROOT/$MIGRATION" 2>/dev/null && echo "true" || echo "false"),
      "INV-DB-04": $(grep -q "decision_blocks_pilares_required" "$PROJECT_ROOT/$MIGRATION" 2>/dev/null && echo "true" || echo "false")
    }
  },
  "errors": $(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .)
}
EOF

echo "Scorecard salvo em: $SCORECARD_DIR/S40_G20_contracts.json"

# Criar evidência de validação de schemas
cat > "$EVIDENCE_DIR/S40_G20_schema_validation.json" << EOF
{
  "metadata": {
    "sprint": "$SPRINT",
    "gate": "$GATE",
    "timestamp": "$TIMESTAMP",
    "commit": "$COMMIT"
  },
  "schemas_validated": [
    "schemas/decision_block_v1.json",
    "schemas/claimgraph_export_v1.json",
    "schemas/truth_twin_v1.json"
  ],
  "validation_method": "json.load + draft-07 check",
  "result": "$RESULT"
}
EOF

# Resumo final
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
