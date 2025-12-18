#!/bin/bash
# =============================================================================
# S39: Sharding Validation Script
#
# Validates the sharding infrastructure setup.
# Usage: bin/s39_validate_sharding.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==================================================================="
echo "S39 Sharding Validation"
echo "==================================================================="

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo "[PASS] $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

check_fail() {
    echo "[FAIL] $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

# Check 1: Docker compose files exist
echo ""
echo "--- Checking Docker Compose Files ---"
if [ -f "${PROJECT_DIR}/docker/docker-compose.shards.yml" ]; then
    check_pass "docker-compose.shards.yml exists"
else
    check_fail "docker-compose.shards.yml missing"
fi

if [ -f "${PROJECT_DIR}/docker/docker-compose.kafka.yml" ]; then
    check_pass "docker-compose.kafka.yml exists"
else
    check_fail "docker-compose.kafka.yml missing"
fi

if [ -f "${PROJECT_DIR}/docker/docker-compose.redis.yml" ]; then
    check_pass "docker-compose.redis.yml exists"
else
    check_fail "docker-compose.redis.yml missing"
fi

if [ -f "${PROJECT_DIR}/docker/docker-compose.full.yml" ]; then
    check_pass "docker-compose.full.yml exists"
else
    check_fail "docker-compose.full.yml missing"
fi

# Check 2: Sharding module files exist
echo ""
echo "--- Checking Sharding Module ---"
if [ -f "${PROJECT_DIR}/app/data/sharding/__init__.py" ]; then
    check_pass "app/data/sharding/__init__.py exists"
else
    check_fail "app/data/sharding/__init__.py missing"
fi

if [ -f "${PROJECT_DIR}/app/data/sharding/router.py" ]; then
    check_pass "app/data/sharding/router.py exists"
else
    check_fail "app/data/sharding/router.py missing"
fi

if [ -f "${PROJECT_DIR}/app/data/sharding/cross_shard.py" ]; then
    check_pass "app/data/sharding/cross_shard.py exists"
else
    check_fail "app/data/sharding/cross_shard.py missing"
fi

if [ -f "${PROJECT_DIR}/app/data/sharding/migration.py" ]; then
    check_pass "app/data/sharding/migration.py exists"
else
    check_fail "app/data/sharding/migration.py missing"
fi

# Check 3: Feature flags exist
echo ""
echo "--- Checking Feature Flags ---"
if [ -f "${PROJECT_DIR}/app/config/feature_flags.py" ]; then
    check_pass "app/config/feature_flags.py exists"
else
    check_fail "app/config/feature_flags.py missing"
fi

# Check 4: Migration file exists
echo ""
echo "--- Checking Migration File ---"
if [ -f "${PROJECT_DIR}/db/migrations/031_sprint39_sharding.sql" ]; then
    check_pass "031_sprint39_sharding.sql exists"
else
    check_fail "031_sprint39_sharding.sql missing"
fi

# Check 5: Test files exist
echo ""
echo "--- Checking Test Files ---"
if [ -f "${PROJECT_DIR}/tests/data/sharding/test_router.py" ]; then
    check_pass "tests/data/sharding/test_router.py exists"
else
    check_fail "tests/data/sharding/test_router.py missing"
fi

if [ -f "${PROJECT_DIR}/tests/data/sharding/test_cross_shard.py" ]; then
    check_pass "tests/data/sharding/test_cross_shard.py exists"
else
    check_fail "tests/data/sharding/test_cross_shard.py missing"
fi

if [ -f "${PROJECT_DIR}/tests/data/sharding/test_migration.py" ]; then
    check_pass "tests/data/sharding/test_migration.py exists"
else
    check_fail "tests/data/sharding/test_migration.py missing"
fi

if [ -f "${PROJECT_DIR}/tests/config/test_feature_flags.py" ]; then
    check_pass "tests/config/test_feature_flags.py exists"
else
    check_fail "tests/config/test_feature_flags.py missing"
fi

# Check 6: Run sharding tests
echo ""
echo "--- Running Sharding Tests ---"
cd "${PROJECT_DIR}"
if PYTHONPATH=. .venv/bin/python -m pytest tests/data/sharding/ tests/config/test_feature_flags.py -v --tb=short -q 2>&1 | tail -5; then
    check_pass "Sharding tests pass"
else
    check_fail "Sharding tests fail"
fi

# Check 7: Coverage check
echo ""
echo "--- Checking Coverage ---"
COVERAGE_OUTPUT=$(PYTHONPATH=. .venv/bin/python -m pytest tests/data/sharding/ tests/config/test_feature_flags.py --cov=app/data/sharding --cov=app/config --cov-fail-under=0 -q 2>&1 | grep "TOTAL")
if [ -n "$COVERAGE_OUTPUT" ]; then
    COVERAGE=$(echo "$COVERAGE_OUTPUT" | awk '{print $NF}' | sed 's/%//')
    if [ "${COVERAGE%.*}" -ge 97 ]; then
        check_pass "Coverage >= 97% (${COVERAGE}%)"
    else
        check_fail "Coverage < 97% (${COVERAGE}%)"
    fi
else
    check_fail "Could not determine coverage"
fi

# Summary
echo ""
echo "==================================================================="
echo "Validation Summary"
echo "==================================================================="
echo "Passed: ${PASS_COUNT}"
echo "Failed: ${FAIL_COUNT}"
echo ""

if [ ${FAIL_COUNT} -eq 0 ]; then
    echo "ALL CHECKS PASSED - Sharding infrastructure ready for W0"
    exit 0
else
    echo "SOME CHECKS FAILED - Review and fix issues before proceeding"
    exit 1
fi
