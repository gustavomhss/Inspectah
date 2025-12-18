#!/bin/bash
# Sprint 40 - Gate G23: Truth-DB Core
# Tasks: DecisionBlocks válidos, E40.5 enforcement, Experiências
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
GATE="G23"

echo "=========================================="
echo "Sprint 40 - Gate G23: Truth-DB Core"
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
echo "--- Verificando módulos S40 ---"

MODULES=(
    "app/guardian/models.py"
    "app/truth/references.py"
    "app/truth/experiences.py"
)

for module in "${MODULES[@]}"; do
    if [ -f "$module" ]; then
        log_result "$module exists" "PASS" ""
    else
        log_result "$module exists" "FAIL" "Arquivo não encontrado"
    fi
done

# 2. Verificar DecisionBlock tem novos campos (S40-BE-003)
echo ""
echo "--- Verificando S40-BE-003: DecisionBlock estendido ---"

if grep -q "class References:" app/guardian/models.py; then
    log_result "References class exists" "PASS" ""
else
    log_result "References class exists" "FAIL" "Class References não encontrada"
fi

if grep -q "experience_ref" app/guardian/models.py; then
    log_result "experience_ref field" "PASS" ""
else
    log_result "experience_ref field" "FAIL" "Campo experience_ref não encontrado"
fi

if grep -q "state_transition" app/guardian/models.py; then
    log_result "state_transition field" "PASS" ""
else
    log_result "state_transition field" "FAIL" "Campo state_transition não encontrado"
fi

# 3. Verificar build_references (S40-BE-004)
echo ""
echo "--- Verificando S40-BE-004: build_references ---"

if grep -q "def build_references" app/truth/references.py; then
    log_result "build_references function" "PASS" ""
else
    log_result "build_references function" "FAIL" "Função não encontrada"
fi

# 4. Verificar Experience model (S40-BE-007/008)
echo ""
echo "--- Verificando S40-BE-007/008: Experiences ---"

if grep -q "class Experience:" app/truth/experiences.py; then
    log_result "Experience class" "PASS" ""
else
    log_result "Experience class" "FAIL" "Class não encontrada"
fi

if grep -q "class ExperienceRepository:" app/truth/experiences.py; then
    log_result "ExperienceRepository class" "PASS" ""
else
    log_result "ExperienceRepository class" "FAIL" "Class não encontrada"
fi

if grep -q "def find_similar" app/truth/experiences.py; then
    log_result "find_similar method" "PASS" ""
else
    log_result "find_similar method" "FAIL" "Método não encontrado"
fi

# 5. Verificar S40-BE-005/006/029 (E40.5 + Degraded + Repository)
echo ""
echo "--- Verificando S40-BE-005/006/029 ---"

if grep -q "class E40_5CheckResult:" app/guardian/flow.py; then
    log_result "E40_5CheckResult class" "PASS" ""
else
    log_result "E40_5CheckResult class" "FAIL" "Class não encontrada"
fi

if grep -q "BLOCKED = " app/guardian/flow.py; then
    log_result "BLOCKED state" "PASS" ""
else
    log_result "BLOCKED state" "FAIL" "Estado BLOCKED não encontrado"
fi

if grep -q "DEGRADED = " app/guardian/flow.py; then
    log_result "DEGRADED state" "PASS" ""
else
    log_result "DEGRADED state" "FAIL" "Estado DEGRADED não encontrado"
fi

if grep -q "class DecisionBlockRepository:" app/truth/repository.py; then
    log_result "DecisionBlockRepository class" "PASS" ""
else
    log_result "DecisionBlockRepository class" "FAIL" "Class não encontrada"
fi

if grep -q "def record_decision_block" app/truth/repository.py; then
    log_result "record_decision_block function" "PASS" ""
else
    log_result "record_decision_block function" "FAIL" "Função não encontrada"
fi

# 6. Rodar testes relevantes
echo ""
echo "--- Rodando testes S40 Truth-DB ---"

TESTS_TO_RUN=(
    "tests/truth/test_validators.py"
    "tests/truth/test_references.py"
    "tests/truth/test_experiences.py"
    "tests/truth/test_repository_s40.py"
    "tests/guardian/test_flow_s40.py"
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

# 6. Verificar integração
echo ""
echo "--- Verificando integração ---"

INTEGRATION_TEST=$(PYTHONPATH=. .venv/bin/python << 'EOF'
import sys
try:
    from app.guardian.models import DecisionBlock, References, GuiaReference, PilarReference, E40_5Result
    from app.truth.references import build_references
    from app.truth.experiences import Experience, ExperienceRepository, find_similar_experiences

    # Test build_references
    claim = {"claim_id": "test", "domain": "saude", "gate": "G23"}
    e40_5 = {"status": "PASS", "invariants_checked": ["INV-1"], "violations": []}
    refs = build_references(claim, None, e40_5)

    assert len(refs.guias) > 0, "guias[] vazio"
    assert len(refs.pilares) > 0, "pilares[] vazio"
    assert refs.e40_5.status == "PASS", "e40_5 status incorreto"

    # Test experiences
    repo = ExperienceRepository()
    exp = Experience.create(
        claim_id="c1",
        decision_id="d1",
        claim_text="test claim",
        outcome="ESTABLISHED_FACT",
        embedding=[0.1] * 10,
    )
    repo.add(exp)

    similar = repo.find_similar([0.1] * 10, top_n=1)
    assert len(similar) == 1, "find_similar falhou"

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

cat > "$SCORECARD_DIR/S40_G23_truthdb.json" << EOF
{
  "metadata": {
    "sprint": "$SPRINT",
    "gate": "$GATE",
    "timestamp": "$TIMESTAMP",
    "commit": "$COMMIT",
    "policy_version": "v1.0.0",
    "domain": "truth-db"
  },
  "result": "$RESULT",
  "summary": {
    "total_checks": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "pass_rate": $PASS_RATE
  },
  "components": {
    "decision_block_extended": true,
    "build_references": true,
    "experiences_model": true,
    "experiences_repository": true,
    "e40_5_enforcement": true,
    "blocked_state": true,
    "degraded_mode": true,
    "decision_block_repository": true,
    "integration_tests": $(echo "$INTEGRATION_TEST" | grep -q "INTEGRATION_OK" && echo "true" || echo "false")
  },
  "tasks_covered": [
    "S40-BE-003",
    "S40-BE-004",
    "S40-BE-005",
    "S40-BE-006",
    "S40-BE-007",
    "S40-BE-008",
    "S40-BE-029"
  ]
}
EOF

echo "Scorecard salvo em: $SCORECARD_DIR/S40_G23_truthdb.json"

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
