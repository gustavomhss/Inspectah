#!/usr/bin/env bash
# S38 Gate G13: Policy Versioning & Memory
# Verifica implementacao completa de policies e memoria

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "S38 Gate G13: Policy Versioning & Memory"
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
echo "=== Policy Version Service ==="
check "version_service.py exists" "test -f $PROJECT_ROOT/app/policies/version_service.py"
check "PolicyVersionService class exists" "grep -q 'class PolicyVersionService' $PROJECT_ROOT/app/policies/version_service.py"
check "PolicyStatus enum exists" "grep -q 'class PolicyStatus' $PROJECT_ROOT/app/policies/version_service.py"
check "create_version method" "grep -q 'def create_version' $PROJECT_ROOT/app/policies/version_service.py"
check "approve method" "grep -q 'def approve' $PROJECT_ROOT/app/policies/version_service.py"
check "activate method" "grep -q 'def activate' $PROJECT_ROOT/app/policies/version_service.py"
check "rollback method" "grep -q 'def rollback' $PROJECT_ROOT/app/policies/version_service.py"

echo ""
echo "=== Memory Controller ==="
check "memory_controller.py exists" "test -f $PROJECT_ROOT/app/context/memory_controller.py"
check "MemoryController class exists" "grep -q 'class MemoryController' $PROJECT_ROOT/app/context/memory_controller.py"
check "MemoryScope enum exists" "grep -q 'class MemoryScope' $PROJECT_ROOT/app/context/memory_controller.py"
check "remember method" "grep -q 'def remember' $PROJECT_ROOT/app/context/memory_controller.py"
check "recall method" "grep -q 'def recall' $PROJECT_ROOT/app/context/memory_controller.py"
check "forget method" "grep -q 'def forget' $PROJECT_ROOT/app/context/memory_controller.py"

echo ""
echo "=== APIs ==="
check "Policies API router exists" "grep -q 'router = APIRouter' $PROJECT_ROOT/app/api/policies_routes.py"
check "Memory API router exists" "grep -q 'router = APIRouter' $PROJECT_ROOT/app/api/memory_routes.py"

echo ""
echo "=== Tests ==="
check "Policy tests directory exists" "test -d $PROJECT_ROOT/tests/policies"
check "Version service tests exist" "test -f $PROJECT_ROOT/tests/policies/test_version_service.py"

echo ""
echo "=========================================="
echo "Gate G13 Results: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
echo "Gate G13: PASSED"
