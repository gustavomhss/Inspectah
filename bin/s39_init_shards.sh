#!/bin/bash
# =============================================================================
# S39: Shard Initialization Script
#
# Applies the sharding migration to all PostgreSQL shards.
# Usage: bin/s39_init_shards.sh [--dry-run]
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MIGRATION_FILE="${PROJECT_DIR}/db/migrations/031_sprint39_sharding.sql"

# Configuration
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-inspectah}"
DRY_RUN=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
    esac
done

# Shard configuration
declare -A SHARDS=(
    ["default"]="pg-shard-default:5432:inspectah_default"
    ["politica"]="pg-shard-politica:5432:inspectah_politica"
    ["economia"]="pg-shard-economia:5432:inspectah_economia"
    ["saude"]="pg-shard-saude:5432:inspectah_saude"
)

echo "==================================================================="
echo "S39 Shard Initialization"
echo "==================================================================="
echo "Migration file: ${MIGRATION_FILE}"
echo "Dry run: ${DRY_RUN}"
echo ""

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "ERROR: Migration file not found: ${MIGRATION_FILE}"
    exit 1
fi

# Function to apply migration to a shard
apply_migration() {
    local domain=$1
    local config=$2

    IFS=':' read -r host port database <<< "$config"

    echo "-------------------------------------------------------------------"
    echo "Applying migration to shard: ${domain}"
    echo "Host: ${host}, Port: ${port}, Database: ${database}"
    echo ""

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would execute:"
        echo "PGPASSWORD=*** psql -h ${host} -p ${port} -U inspectah -d ${database} -f ${MIGRATION_FILE}"
        echo ""
        return 0
    fi

    # Apply migration
    PGPASSWORD="${POSTGRES_PASSWORD}" psql \
        -h "${host}" \
        -p "${port}" \
        -U inspectah \
        -d "${database}" \
        -f "${MIGRATION_FILE}" \
        -v ON_ERROR_STOP=1

    if [ $? -eq 0 ]; then
        echo "SUCCESS: Migration applied to ${domain}"

        # Insert shard metadata
        PGPASSWORD="${POSTGRES_PASSWORD}" psql \
            -h "${host}" \
            -p "${port}" \
            -U inspectah \
            -d "${database}" \
            -c "INSERT INTO shard_metadata (domain, shard_id) VALUES ('${domain}', ${!SHARD_IDS[${domain}]:-0}) ON CONFLICT (domain) DO NOTHING;"

        echo ""
    else
        echo "ERROR: Migration failed for ${domain}"
        return 1
    fi
}

# Shard IDs mapping
declare -A SHARD_IDS=(
    ["default"]=0
    ["politica"]=1
    ["economia"]=2
    ["saude"]=3
)

# Apply migrations to all shards
FAILED_SHARDS=()
for domain in "${!SHARDS[@]}"; do
    if ! apply_migration "$domain" "${SHARDS[$domain]}"; then
        FAILED_SHARDS+=("$domain")
    fi
done

echo "==================================================================="
echo "Migration Summary"
echo "==================================================================="

if [ ${#FAILED_SHARDS[@]} -eq 0 ]; then
    echo "All shards initialized successfully!"
    exit 0
else
    echo "Failed shards: ${FAILED_SHARDS[*]}"
    exit 1
fi
