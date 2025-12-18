"""
S39 - Data Layer Module

Provides data access components including:
- Sharding: Domain-based PostgreSQL sharding
"""

from app.data.sharding import (
    Domain,
    ShardConfig,
    ShardRouter,
    router,
    CrossShardResult,
    CrossShardQueryExecutor,
    MigrationPhase,
    MigrationManager,
    ShadowModeWriter,
)

__all__ = [
    "Domain",
    "ShardConfig",
    "ShardRouter",
    "router",
    "CrossShardResult",
    "CrossShardQueryExecutor",
    "MigrationPhase",
    "MigrationManager",
    "ShadowModeWriter",
]
