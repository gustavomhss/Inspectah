#!/bin/bash
# S40-CI-007: ORR Bundle Generator
# Creates S40_bundle.zip with all deliverables

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "======================================"
echo "S40 ORR Bundle Generator"
echo "======================================"
echo "Project: $PROJECT_ROOT"
echo "Time: $(date)"
echo ""

cd "$PROJECT_ROOT"

# Create output directories
mkdir -p out/bundles
mkdir -p out/evidence

BUNDLE_DIR="out/bundles/s40_bundle_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BUNDLE_DIR"

echo "Creating bundle in: $BUNDLE_DIR"
echo ""

# 1. Run all gates first
echo "Step 1: Running all gates..."
if bash "$SCRIPT_DIR/s40_all_gates.sh" > "$BUNDLE_DIR/gates_output.log" 2>&1; then
    echo -e "${GREEN}✓ All gates passed${NC}"
    GATES_STATUS="PASS"
else
    echo -e "${YELLOW}⚠ Some gates failed (see gates_output.log)${NC}"
    GATES_STATUS="PARTIAL"
fi
echo ""

# 2. Run test coverage
echo "Step 2: Running test coverage..."
PYTHONPATH=. .venv/bin/python -m pytest tests/ \
    --cov=app \
    --cov-report=html:$BUNDLE_DIR/coverage \
    --cov-report=json:$BUNDLE_DIR/coverage.json \
    -q 2>&1 | tail -20 > "$BUNDLE_DIR/test_output.log"

# Extract coverage percentage
COVERAGE=$(python3 -c "import json; d=json.load(open('$BUNDLE_DIR/coverage.json')); print(round(d['totals']['percent_covered'], 1))")
echo "Coverage: ${COVERAGE}%"
echo ""

# 3. Collect S40 artifacts
echo "Step 3: Collecting artifacts..."

# Backend files
mkdir -p "$BUNDLE_DIR/backend"
cp -r app/truth "$BUNDLE_DIR/backend/" 2>/dev/null || true
cp -r app/claims/signals.py "$BUNDLE_DIR/backend/" 2>/dev/null || true
cp -r app/claims/export.py "$BUNDLE_DIR/backend/" 2>/dev/null || true
cp -r app/api/truth_routes.py "$BUNDLE_DIR/backend/" 2>/dev/null || true
cp -r app/api/truth_schemas.py "$BUNDLE_DIR/backend/" 2>/dev/null || true
cp -r app/api/metrics.py "$BUNDLE_DIR/backend/" 2>/dev/null || true
cp -r app/api/middleware/provenance.py "$BUNDLE_DIR/backend/" 2>/dev/null || true

# Frontend files
mkdir -p "$BUNDLE_DIR/frontend"
cp -r frontend/inspectah-ui/src/modules/truth "$BUNDLE_DIR/frontend/" 2>/dev/null || true

# Schemas
mkdir -p "$BUNDLE_DIR/schemas"
cp schemas/decision_block_v1.json "$BUNDLE_DIR/schemas/" 2>/dev/null || true
cp schemas/claimgraph_export_v1.json "$BUNDLE_DIR/schemas/" 2>/dev/null || true
cp schemas/truth_twin_v1.json "$BUNDLE_DIR/schemas/" 2>/dev/null || true

# Tests
mkdir -p "$BUNDLE_DIR/tests"
cp tests/truth/test_e40_5_enforcement.py "$BUNDLE_DIR/tests/" 2>/dev/null || true
cp tests/truth/test_canonical_cases.py "$BUNDLE_DIR/tests/" 2>/dev/null || true
cp tests/claims/test_nogo_signals.py "$BUNDLE_DIR/tests/" 2>/dev/null || true
cp tests/api/test_truth_twin_routes.py "$BUNDLE_DIR/tests/" 2>/dev/null || true
cp tests/api/test_p4_latency.py "$BUNDLE_DIR/tests/" 2>/dev/null || true

# Observability
mkdir -p "$BUNDLE_DIR/observability"
cp observability/dashboards/s40_truthdb.json "$BUNDLE_DIR/observability/" 2>/dev/null || true
cp observability/alerts/s40_invariants.yaml "$BUNDLE_DIR/observability/" 2>/dev/null || true

# CI scripts
mkdir -p "$BUNDLE_DIR/bin"
cp bin/s40_*.sh "$BUNDLE_DIR/bin/" 2>/dev/null || true

# Documentation
mkdir -p "$BUNDLE_DIR/docs"
cp docs/s40_*.md "$BUNDLE_DIR/docs/" 2>/dev/null || true
cp docs/s40_*.yml "$BUNDLE_DIR/docs/" 2>/dev/null || true

echo -e "${GREEN}✓ Artifacts collected${NC}"
echo ""

# 4. Generate manifest
echo "Step 4: Generating manifest..."
cat > "$BUNDLE_DIR/MANIFEST.md" << EOF
# S40 Bundle Manifest

## Sprint: S40 - Truth-DB Estável

### Generated
- Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- Host: $(hostname)
- Gates Status: $GATES_STATUS

### Coverage
- Total: ${COVERAGE}%

### Contents

#### Backend
- app/truth/ - Truth repository and validators
- app/claims/signals.py - NO-GO signal handling
- app/claims/export.py - ClaimGraph export
- app/api/truth_routes.py - P4 API endpoints
- app/api/truth_schemas.py - Response DTOs
- app/api/metrics.py - P4 latency metrics
- app/api/middleware/provenance.py - Provenance validation

#### Frontend
- src/modules/truth/ - Truth Twin UI components

#### Schemas
- decision_block_v1.json
- claimgraph_export_v1.json
- truth_twin_v1.json

#### Tests
- E40.5 enforcement tests
- NO-GO signals tests
- Truth Twin API tests
- P4 latency tests
- Canonical cases A/B/C

#### Observability
- Grafana dashboard: s40_truthdb.json
- Alerts: s40_invariants.yaml

### Wave Summary
- W0: Groundwork (schemas, migration)
- W1: Core (DecisionBlock, References, E40.5)
- W2: Export (ClaimGraph, NO-GO signals)
- W3: Guardian integration
- W4: P4 Exposure (API endpoints, frontend)
- W5: Quality & ORR (this bundle)

### Gates
- G20: Contracts & Schemas
- G21: Observability
- G22: ClaimGraph Export
- G23: Truth-DB Core
- G24: P4 Exposure
EOF

echo -e "${GREEN}✓ Manifest generated${NC}"
echo ""

# 5. Create ZIP bundle
echo "Step 5: Creating ZIP bundle..."
BUNDLE_ZIP="out/bundles/S40_bundle.zip"
rm -f "$BUNDLE_ZIP"

cd "$BUNDLE_DIR"
zip -r "../S40_bundle.zip" . -q
cd "$PROJECT_ROOT"

# Also keep the timestamped copy
cp "$BUNDLE_ZIP" "${BUNDLE_DIR}.zip"

echo -e "${GREEN}✓ Bundle created: $BUNDLE_ZIP${NC}"
echo ""

# 6. Final summary
echo "======================================"
echo "S40 ORR Bundle Complete"
echo "======================================"
echo "Bundle: $BUNDLE_ZIP"
echo "Size: $(du -h $BUNDLE_ZIP | cut -f1)"
echo "Gates: $GATES_STATUS"
echo "Coverage: ${COVERAGE}%"
echo ""
echo "Contents:"
ls -la "$BUNDLE_DIR"
echo ""

# Copy to evidence
cp "$BUNDLE_ZIP" "out/bundles/"
echo "Evidence saved to: out/bundles/S40_bundle.zip"

# Cleanup working directory
rm -rf "$BUNDLE_DIR"

echo ""
echo -e "${GREEN}S40 ORR bundle generation complete!${NC}"
