#!/usr/bin/env bash
# ============================================================
# check_coverage.sh - Verifica cobertura de testes
# ============================================================
# Uso: ./bin/check_coverage.sh [módulo]
#
# Exemplos:
#   ./bin/check_coverage.sh              # Cobertura global
#   ./bin/check_coverage.sh app/flows    # Cobertura de módulo
# ============================================================

set -e

MINIMUM_COVERAGE=97
MODULE=${1:-app}

echo "=============================================="
echo "Verificação de Cobertura de Testes"
echo "=============================================="
echo "Módulo: $MODULE"
echo "Cobertura mínima: ${MINIMUM_COVERAGE}%"
echo "=============================================="
echo ""

# Ativa ambiente virtual
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Roda testes com cobertura
PYTHONPATH=. python -m pytest --cov=$MODULE --cov-report=term-missing --cov-fail-under=$MINIMUM_COVERAGE

RESULT=$?

echo ""
echo "=============================================="
if [ $RESULT -eq 0 ]; then
    echo "✅ SUCESSO: Cobertura >= ${MINIMUM_COVERAGE}%"
else
    echo "❌ FALHA: Cobertura abaixo de ${MINIMUM_COVERAGE}%"
    echo ""
    echo "Para identificar módulos com baixa cobertura:"
    echo "  PYTHONPATH=. python -m pytest --cov=app 2>&1 | grep -v '100%'"
fi
echo "=============================================="

exit $RESULT
