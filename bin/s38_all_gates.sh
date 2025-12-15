#!/usr/bin/env bash
# S38: Execute all gates
# Sprint 38: Hardening Dominios

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=============================================="
echo "S38 HARDENING DOMINIOS - ALL GATES"
echo "=============================================="
echo ""

TOTAL_PASS=0
TOTAL_FAIL=0
GATES_PASS=0
GATES_FAIL=0

run_gate() {
    local gate_script="$1"
    local gate_name="$2"

    echo ""
    echo ">>> Running $gate_name..."
    echo ""

    if bash "$SCRIPT_DIR/$gate_script"; then
        GATES_PASS=$((GATES_PASS+1))
        echo ""
        echo ">>> $gate_name: PASSED"
    else
        GATES_FAIL=$((GATES_FAIL+1))
        echo ""
        echo ">>> $gate_name: FAILED"
    fi
    echo ""
}

# Run all gates
run_gate "s38_g10_signals.sh" "G10 - Signals On-Demand"
run_gate "s38_g11_sources.sh" "G11 - Sources & Scrapers"
run_gate "s38_g12_claims.sh" "G12 - Claims Relations"
run_gate "s38_g13_policies.sh" "G13 - Policy Versioning & Memory"
run_gate "s38_g14_ops.sh" "G14 - Ops Dashboard & Observability"

echo ""
echo "=============================================="
echo "S38 FINAL RESULTS"
echo "=============================================="
echo ""
echo "Gates Passed: $GATES_PASS"
echo "Gates Failed: $GATES_FAIL"
echo ""

if [ $GATES_FAIL -gt 0 ]; then
    echo "STATUS: SOME GATES FAILED"
    echo ""
    echo "Please fix the failing gates before proceeding."
    exit 1
fi

echo "STATUS: ALL GATES PASSED"
echo ""
echo "S38 Hardening Dominios is ready for ORR."
echo ""
echo "=============================================="
echo "ORR CHECKLIST"
echo "=============================================="
echo "[x] G10 - Signals On-Demand"
echo "[x] G11 - Sources & Scrapers"
echo "[x] G12 - Claims Relations"
echo "[x] G13 - Policy Versioning & Memory"
echo "[x] G14 - Ops Dashboard & Observability"
echo ""
echo "Entregaveis:"
echo "- Signal service com cache on-demand"
echo "- 3 integradores oficiais (gov.br, dados.gov, TSE)"
echo "- 5 scrapers de fact-checking"
echo "- Rate limiter + Circuit breaker + Health monitor"
echo "- Console Fontes UI"
echo "- Inferencia de relacoes entre claims"
echo "- Policy versioning com audit trail"
echo "- Memory controller para contexto"
echo "- Ops dashboard centralizado"
echo "- Contratos de API v1"
echo "- Servico de explicabilidade"
echo "- Testes + Alertas Prometheus + Dashboards Grafana"
echo ""
echo "=============================================="
