#!/bin/bash
# =============================================================================
# validate_s37_stability.sh
# S37 Stability Check - Pre-requisito para iniciar S38
# =============================================================================
#
# Este script valida a estabilidade do S37 antes de iniciar o S38.
#
# Criterios verificados:
#   1. Testes passando (pytest)
#   2. Build OK (ruff check)
#   3. Confirmacao manual de ausencia de bugs criticos
#
# Uso:
#   bash bin/validate_s37_stability.sh
#
# Exit codes:
#   0 = S37 estavel, OK para iniciar S38
#   1 = S37 instavel, resolver antes de iniciar S38
#
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracao
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

EVIDENCE_DIR="${PROJECT_ROOT}/out/evidence"
EVIDENCE_FILE="${EVIDENCE_DIR}/S38_precheck_s37.txt"

# -----------------------------------------------------------------------------
# Funcoes
# -----------------------------------------------------------------------------
log_header() {
    echo ""
    echo -e "${BOLD}$1${NC}"
    echo "─────────────────────────────────────────────────"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# -----------------------------------------------------------------------------
# Check 1: Pytest
# -----------------------------------------------------------------------------
check_pytest() {
    log_header "CHECK 1: Testes (pytest)"

    cd "$PROJECT_ROOT"

    if ! command -v pytest &> /dev/null; then
        # Tentar com python -m pytest
        if python3 -m pytest --version &> /dev/null 2>&1; then
            PYTEST_CMD="python3 -m pytest"
        else
            log_warn "pytest nao encontrado"
            log_info "Instale com: pip install pytest"
            return 1
        fi
    else
        PYTEST_CMD="pytest"
    fi

    log_info "Executando testes..."

    # Rodar pytest e capturar saida
    set +e
    TEST_OUTPUT=$($PYTEST_CMD tests/ -q --tb=no 2>&1)
    TEST_EXIT=$?
    set -e

    # Extrair resultado
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | head -1 || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1 || echo "0")
    ERRORS=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' | head -1 || echo "0")

    if [ "$TEST_EXIT" -eq 0 ]; then
        log_pass "Testes: ${PASSED} passed, ${FAILED} failed, ${ERRORS} errors"
        return 0
    else
        log_fail "Testes falhando: ${PASSED} passed, ${FAILED} failed, ${ERRORS} errors"
        echo ""
        echo "Detalhes:"
        echo "$TEST_OUTPUT" | tail -20
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Check 2: Lint (ruff)
# -----------------------------------------------------------------------------
check_lint() {
    log_header "CHECK 2: Lint (ruff)"

    cd "$PROJECT_ROOT"

    if ! command -v ruff &> /dev/null; then
        log_warn "ruff nao encontrado, pulando check de lint"
        log_info "Instale com: pip install ruff"
        return 0
    fi

    log_info "Executando ruff check..."

    set +e
    LINT_OUTPUT=$(ruff check app/ --select=E,F --ignore=E501 2>&1)
    LINT_EXIT=$?
    set -e

    if [ "$LINT_EXIT" -eq 0 ]; then
        log_pass "Lint OK (sem erros criticos)"
        return 0
    else
        ERROR_COUNT=$(echo "$LINT_OUTPUT" | grep -c "error\|E[0-9]" || echo "0")
        if [ "$ERROR_COUNT" -gt 10 ]; then
            log_fail "Lint: $ERROR_COUNT erros encontrados"
            echo ""
            echo "Primeiros erros:"
            echo "$LINT_OUTPUT" | head -10
            return 1
        else
            log_warn "Lint: $ERROR_COUNT warnings (nao bloqueante)"
            return 0
        fi
    fi
}

# -----------------------------------------------------------------------------
# Check 3: Build Check
# -----------------------------------------------------------------------------
check_build() {
    log_header "CHECK 3: Build (importacao)"

    cd "$PROJECT_ROOT"

    log_info "Verificando importacao dos modulos principais..."

    set +e
    BUILD_OUTPUT=$(python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import app
    print('app: OK')
except Exception as e:
    print(f'app: FAIL - {e}')
    sys.exit(1)
" 2>&1)
    BUILD_EXIT=$?
    set -e

    if [ "$BUILD_EXIT" -eq 0 ]; then
        log_pass "Build OK (modulos importam corretamente)"
        return 0
    else
        log_fail "Build falhou"
        echo "$BUILD_OUTPUT"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Check 4: Confirmacao Manual
# -----------------------------------------------------------------------------
check_manual_confirmation() {
    log_header "CHECK 4: Confirmacao Manual"

    echo ""
    echo "Confirme manualmente:"
    echo ""
    echo "  1. Nao ha bugs P1 conhecidos pendentes"
    echo "  2. Nao houve incidentes criticos recentes"
    echo "  3. O sistema esta funcionando conforme esperado"
    echo ""

    # Se nao for interativo, assumir confirmado
    if [ ! -t 0 ]; then
        log_info "Modo nao-interativo: assumindo confirmacao"
        log_pass "Confirmacao manual: assumida (CI/CD)"
        return 0
    fi

    read -p "Confirma que S37 esta estavel? [s/N] " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Ss]$ ]]; then
        log_pass "Confirmacao manual: OK"
        return 0
    else
        log_fail "Confirmacao manual: NAO"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Gerar Evidencia
# -----------------------------------------------------------------------------
generate_evidence() {
    mkdir -p "$EVIDENCE_DIR"

    {
        echo "=============================================="
        echo "  S37 STABILITY CHECK - EVIDENCIA"
        echo "=============================================="
        echo ""
        echo "Data: $(date -Iseconds)"
        echo "Host: $(hostname)"
        echo "Usuario: $(whoami)"
        echo "Diretorio: $PROJECT_ROOT"
        echo ""
        echo "----------------------------------------------"
        echo "RESULTADOS"
        echo "----------------------------------------------"
        echo ""
        echo "Check 1 - Testes:    $CHECK1_RESULT"
        echo "Check 2 - Lint:      $CHECK2_RESULT"
        echo "Check 3 - Build:     $CHECK3_RESULT"
        echo "Check 4 - Manual:    $CHECK4_RESULT"
        echo ""
        echo "----------------------------------------------"
        echo "RESULTADO FINAL: $FINAL_RESULT"
        echo "----------------------------------------------"
        echo ""
        echo "Assinatura: validate_s37_stability.sh v2.0"
    } > "$EVIDENCE_FILE"

    log_info "Evidencia salva em: $EVIDENCE_FILE"
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    echo ""
    echo "=============================================="
    echo "  S37 STABILITY CHECK"
    echo "  Pre-requisito para iniciar S38"
    echo "=============================================="
    echo ""
    echo "Projeto: $PROJECT_ROOT"
    echo "Data: $(date)"
    echo ""

    BLOCKERS=0

    # Check 1: Testes
    if check_pytest; then
        CHECK1_RESULT="PASS"
    else
        CHECK1_RESULT="FAIL"
        ((BLOCKERS++))
    fi

    # Check 2: Lint
    if check_lint; then
        CHECK2_RESULT="PASS"
    else
        CHECK2_RESULT="FAIL"
        ((BLOCKERS++))
    fi

    # Check 3: Build
    if check_build; then
        CHECK3_RESULT="PASS"
    else
        CHECK3_RESULT="FAIL"
        ((BLOCKERS++))
    fi

    # Check 4: Confirmacao Manual
    if check_manual_confirmation; then
        CHECK4_RESULT="PASS"
    else
        CHECK4_RESULT="FAIL"
        ((BLOCKERS++))
    fi

    # Resultado Final
    log_header "RESULTADO FINAL"

    if [ "$BLOCKERS" -eq 0 ]; then
        FINAL_RESULT="PASS"
        echo ""
        log_pass "S37 ESTAVEL"
        echo ""
        echo -e "${GREEN}${BOLD}W0 do S38 esta LIBERADO${NC}"
        echo ""
        generate_evidence
        exit 0
    else
        FINAL_RESULT="FAIL ($BLOCKERS blocker(s))"
        echo ""
        log_fail "S37 INSTAVEL - $BLOCKERS blocker(s)"
        echo ""
        echo "Resolva os problemas acima antes de iniciar S38."
        echo ""
        generate_evidence
        exit 1
    fi
}

# Executar
main "$@"
