#!/bin/bash
# S40-CI-006: All Gates Runner
# Runs all S40 gates and reports overall status
# Exit 0 if all pass, non-zero otherwise

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "S40 All Gates Runner"
echo "======================================"
echo "Project: $PROJECT_ROOT"
echo "Time: $(date)"
echo ""

# Track results
GATES_PASSED=0
GATES_FAILED=0
FAILED_GATES=""

# Function to run a gate and track result
run_gate() {
    local gate_name=$1
    local gate_script=$2

    echo ""
    echo "----------------------------------------"
    echo "Running $gate_name..."
    echo "----------------------------------------"

    if [ -f "$SCRIPT_DIR/$gate_script" ]; then
        if bash "$SCRIPT_DIR/$gate_script"; then
            echo -e "${GREEN}✓ $gate_name PASSED${NC}"
            GATES_PASSED=$((GATES_PASSED + 1))
            return 0
        else
            echo -e "${RED}✗ $gate_name FAILED${NC}"
            GATES_FAILED=$((GATES_FAILED + 1))
            FAILED_GATES="$FAILED_GATES $gate_name"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ $gate_name script not found: $gate_script${NC}"
        GATES_FAILED=$((GATES_FAILED + 1))
        FAILED_GATES="$FAILED_GATES $gate_name"
        return 1
    fi
}

# Run all S40 gates
cd "$PROJECT_ROOT"

# G20: Contracts & Schemas
run_gate "G20 (Contracts)" "s40_g20_contracts.sh" || true

# G21: Observability
echo ""
echo "----------------------------------------"
echo "Running G21 (Observability)..."
echo "----------------------------------------"
if [ -f "observability/dashboards/s40_truthdb.json" ] && [ -f "observability/alerts/s40_invariants.yaml" ]; then
    echo -e "${GREEN}✓ G21 PASSED - Dashboard and alerts exist${NC}"
    GATES_PASSED=$((GATES_PASSED + 1))
else
    echo -e "${RED}✗ G21 FAILED - Missing dashboard or alerts${NC}"
    GATES_FAILED=$((GATES_FAILED + 1))
    FAILED_GATES="$FAILED_GATES G21"
fi

# G22: ClaimGraph
run_gate "G22 (ClaimGraph)" "s40_g22_claimgraph.sh" || true

# G23: Truth-DB
run_gate "G23 (Truth-DB)" "s40_g23_truthdb.sh" || true

# G24: P4 Exposure
run_gate "G24 (P4 Exposure)" "s40_g24_p4_exposure.sh" || true

# Summary
echo ""
echo "======================================"
echo "S40 Gates Summary"
echo "======================================"
echo -e "Passed: ${GREEN}$GATES_PASSED${NC}"
echo -e "Failed: ${RED}$GATES_FAILED${NC}"

if [ -n "$FAILED_GATES" ]; then
    echo -e "Failed gates:${RED}$FAILED_GATES${NC}"
fi

TOTAL_GATES=$((GATES_PASSED + GATES_FAILED))
echo ""
echo "Total: $GATES_PASSED/$TOTAL_GATES gates passed"
echo ""

# Generate evidence output
mkdir -p "$PROJECT_ROOT/out/evidence"
cat > "$PROJECT_ROOT/out/evidence/S40_all_gates.log" << EOF
S40 All Gates Run
==================
Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Host: $(hostname)

Results:
- Passed: $GATES_PASSED
- Failed: $GATES_FAILED
- Failed gates:$FAILED_GATES

Status: $([ $GATES_FAILED -eq 0 ] && echo "ALL PASS" || echo "SOME FAILED")
EOF

# Exit with appropriate code
if [ $GATES_FAILED -eq 0 ]; then
    echo -e "${GREEN}All S40 gates passed!${NC}"
    exit 0
else
    echo -e "${RED}Some S40 gates failed!${NC}"
    exit 1
fi
