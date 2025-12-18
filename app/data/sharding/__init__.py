"""
S39 - Database Sharding Module

Provides domain-based sharding for PostgreSQL with:
- ShardRouter: Routes claims to appropriate shards based on domain
- CrossShardQueryExecutor: Executes scatter-gather queries across shards
- MigrationManager: Handles shadow mode and data migration
"""

from app.data.sharding.router import (
    Domain,
    ShardConfig,
    ShardRouter,
    SHARD_CONFIGS,
    DOMAIN_KEYWORDS,
    router,
)
from app.data.sharding.cross_shard import (
    AggregationType,
    CrossShardResult,
    CrossShardQueryExecutor,
    ShardQueryResult,
)
from app.data.sharding.migration import (
    MigrationPhase,
    MigrationManager,
    ShadowModeWriter,
)

__all__ = [
    # Router
    "Domain",
    "ShardConfig",
    "ShardRouter",
    "SHARD_CONFIGS",
    "DOMAIN_KEYWORDS",
    "router",
    # Cross-shard
    "AggregationType",
    "CrossShardResult",
    "CrossShardQueryExecutor",
    "ShardQueryResult",
    # Migration
    "MigrationPhase",
    "MigrationManager",
    "ShadowModeWriter",
]
