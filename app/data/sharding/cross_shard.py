"""
S39 - Cross-Shard Query Executor

Executes scatter-gather queries across all shards with:
- Parallel execution with timeout per shard
- Aggregation support (SUM, COUNT, AVG, MAX, MIN)
- Search with merge and sort
- Partial results on shard failures
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

from app.data.sharding.router import Domain, ShardRouter

logger = logging.getLogger(__name__)

# Valid SQL identifier pattern (prevents SQL injection)
_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _validate_identifier(name: str, kind: str = "identifier") -> None:
    """
    Validate that a string is a safe SQL identifier.

    Args:
        name: The identifier to validate
        kind: Description for error message (e.g., "table", "column")

    Raises:
        ValueError: If identifier is invalid
    """
    if not name or not _IDENTIFIER_PATTERN.match(name):
        raise ValueError(f"Invalid {kind} name: {name!r}")

T = TypeVar("T")


class AggregationType(str, Enum):
    """Types of aggregation for cross-shard queries."""

    SUM = "SUM"
    COUNT = "COUNT"
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"
    COLLECT = "COLLECT"  # No aggregation, just collect


@dataclass
class CrossShardResult:
    """Result of a cross-shard query."""

    data: List[Dict[str, Any]]
    shards_queried: List[str]
    shards_succeeded: List[str]
    shards_failed: List[str]
    is_partial: bool
    total_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate of shard queries."""
        if not self.shards_queried:
            return 0.0
        return len(self.shards_succeeded) / len(self.shards_queried)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "shards_queried": self.shards_queried,
            "shards_succeeded": self.shards_succeeded,
            "shards_failed": self.shards_failed,
            "is_partial": self.is_partial,
            "total_time_ms": self.total_time_ms,
            "success_rate": self.success_rate,
            "metadata": self.metadata,
        }


@dataclass
class ShardQueryResult:
    """Result from a single shard query."""

    domain: Domain
    success: bool
    data: Any
    error: Optional[str] = None
    latency_ms: float = 0.0


class CrossShardQueryExecutor:
    """
    Executes queries across all shards using scatter-gather pattern.

    Features:
    - Parallel execution with configurable timeout
    - Supports aggregations (SUM, COUNT, AVG, MAX, MIN)
    - Search with merge and sort capabilities
    - Returns partial results when some shards fail
    - Detailed metrics on query execution

    Usage:
        executor = CrossShardQueryExecutor(router)

        # Aggregate across shards
        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims WHERE status = $1",
            params=("verified",),
            aggregation=AggregationType.SUM,
        )

        # Search across shards
        result = await executor.search(
            "SELECT * FROM claims WHERE text ILIKE $1 ORDER BY created_at DESC",
            params=("%vaccine%",),
            limit=100,
            sort_key="created_at",
            sort_reverse=True,
        )
    """

    def __init__(
        self,
        router: ShardRouter,
        timeout_seconds: float = 5.0,
        retry_count: int = 1,
    ):
        self.router = router
        self.timeout = timeout_seconds
        self.retry_count = retry_count

    async def _query_single_shard(
        self,
        domain: Domain,
        query: str,
        params: tuple,
        fetch_method: str = "fetch",
    ) -> ShardQueryResult:
        """Query a single shard with timeout and retry."""
        start = time.time()
        last_error = None

        for attempt in range(self.retry_count + 1):
            try:
                async with asyncio.timeout(self.timeout):
                    async with self.router.get_connection(domain) as conn:
                        if fetch_method == "fetchval":
                            result = await conn.fetchval(query, *params)
                        elif fetch_method == "fetchrow":
                            row = await conn.fetchrow(query, *params)
                            result = dict(row) if row else None
                        else:
                            rows = await conn.fetch(query, *params)
                            result = [dict(row) for row in rows]

                        return ShardQueryResult(
                            domain=domain,
                            success=True,
                            data=result,
                            latency_ms=(time.time() - start) * 1000,
                        )
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout}s"
                logger.warning(
                    f"Shard {domain.value} timeout (attempt {attempt + 1}/{self.retry_count + 1})"
                )
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Shard {domain.value} error (attempt {attempt + 1}): {e}"
                )

            if attempt < self.retry_count:
                await asyncio.sleep(0.1 * (attempt + 1))  # Backoff

        return ShardQueryResult(
            domain=domain,
            success=False,
            data=None,
            error=last_error,
            latency_ms=(time.time() - start) * 1000,
        )

    async def aggregate(
        self,
        query: str,
        params: tuple = (),
        aggregation: AggregationType = AggregationType.SUM,
        domains: Optional[List[Domain]] = None,
    ) -> CrossShardResult:
        """
        Execute an aggregation query across shards.

        Args:
            query: SQL query that returns a single value (e.g., SELECT COUNT(*) FROM ...)
            params: Query parameters
            aggregation: Type of aggregation to perform on results
            domains: Specific domains to query (None = all)

        Returns:
            CrossShardResult with aggregated data
        """
        start = time.time()
        target_domains = domains or list(Domain)

        # Execute queries in parallel
        tasks = [
            self._query_single_shard(d, query, params, fetch_method="fetchval")
            for d in target_domains
        ]
        shard_results = await asyncio.gather(*tasks)

        # Process results
        succeeded = []
        failed = []
        values = []

        for result in shard_results:
            if result.success and result.data is not None:
                succeeded.append(result.domain.value)
                values.append(result.data)
            else:
                failed.append(result.domain.value)

        # Aggregate values
        if not values:
            aggregated = None
        elif aggregation == AggregationType.SUM:
            aggregated = sum(values)
        elif aggregation == AggregationType.COUNT:
            aggregated = sum(values)
        elif aggregation == AggregationType.AVG:
            aggregated = sum(values) / len(values)
        elif aggregation == AggregationType.MAX:
            aggregated = max(values)
        elif aggregation == AggregationType.MIN:
            aggregated = min(values)
        else:  # COLLECT
            aggregated = values

        return CrossShardResult(
            data=[{"result": aggregated, "per_shard": dict(zip(succeeded, values))}],
            shards_queried=[d.value for d in target_domains],
            shards_succeeded=succeeded,
            shards_failed=failed,
            is_partial=len(failed) > 0,
            total_time_ms=(time.time() - start) * 1000,
            metadata={
                "aggregation_type": aggregation.value,
                "values_count": len(values),
            },
        )

    async def search(
        self,
        query: str,
        params: tuple = (),
        limit: int = 100,
        sort_key: Optional[str] = None,
        sort_reverse: bool = True,
        domains: Optional[List[Domain]] = None,
        merge_fn: Optional[Callable[[List[Dict]], List[Dict]]] = None,
    ) -> CrossShardResult:
        """
        Execute a search query across shards with merge and sort.

        Args:
            query: SQL query that returns rows
            params: Query parameters
            limit: Maximum number of results to return
            sort_key: Key to sort merged results by
            sort_reverse: Sort in descending order if True
            domains: Specific domains to query (None = all)
            merge_fn: Custom merge function (receives list of all rows)

        Returns:
            CrossShardResult with merged and sorted data
        """
        start = time.time()
        target_domains = domains or list(Domain)

        # Execute queries in parallel
        tasks = [
            self._query_single_shard(d, query, params, fetch_method="fetch")
            for d in target_domains
        ]
        shard_results = await asyncio.gather(*tasks)

        # Process results
        succeeded = []
        failed = []
        all_rows: List[Dict[str, Any]] = []

        for result in shard_results:
            if result.success and result.data is not None:
                succeeded.append(result.domain.value)
                # Add shard info to each row
                for row in result.data:
                    row["_shard"] = result.domain.value
                    all_rows.append(row)
            else:
                failed.append(result.domain.value)

        # Apply custom merge function or default sort
        if merge_fn:
            merged = merge_fn(all_rows)
        elif sort_key and all_rows:
            merged = sorted(
                all_rows,
                key=lambda x: x.get(sort_key, ""),
                reverse=sort_reverse,
            )
        else:
            merged = all_rows

        # Apply limit
        limited = merged[:limit]

        return CrossShardResult(
            data=limited,
            shards_queried=[d.value for d in target_domains],
            shards_succeeded=succeeded,
            shards_failed=failed,
            is_partial=len(failed) > 0,
            total_time_ms=(time.time() - start) * 1000,
            metadata={
                "total_rows_before_limit": len(merged),
                "limit_applied": limit,
                "sort_key": sort_key,
            },
        )

    async def execute_raw(
        self,
        query: str,
        params: tuple = (),
        domains: Optional[List[Domain]] = None,
    ) -> CrossShardResult:
        """
        Execute a raw query across shards without aggregation.

        Args:
            query: SQL query
            params: Query parameters
            domains: Specific domains to query (None = all)

        Returns:
            CrossShardResult with raw results from each shard
        """
        start = time.time()
        target_domains = domains or list(Domain)

        # Execute queries in parallel
        tasks = [
            self._query_single_shard(d, query, params, fetch_method="fetch")
            for d in target_domains
        ]
        shard_results = await asyncio.gather(*tasks)

        # Process results
        succeeded = []
        failed = []
        results_by_shard: Dict[str, List[Dict]] = {}

        for result in shard_results:
            if result.success and result.data is not None:
                succeeded.append(result.domain.value)
                results_by_shard[result.domain.value] = result.data
            else:
                failed.append(result.domain.value)
                results_by_shard[result.domain.value] = []

        return CrossShardResult(
            data=[results_by_shard],
            shards_queried=[d.value for d in target_domains],
            shards_succeeded=succeeded,
            shards_failed=failed,
            is_partial=len(failed) > 0,
            total_time_ms=(time.time() - start) * 1000,
        )

    async def count_all(
        self,
        table: str,
        where: Optional[str] = None,
        params: tuple = (),
    ) -> CrossShardResult:
        """
        Count rows in a table across all shards.

        Args:
            table: Table name (must be a valid SQL identifier)
            where: Optional WHERE clause (without 'WHERE' keyword)
            params: Query parameters for WHERE clause

        Returns:
            CrossShardResult with total count

        Raises:
            ValueError: If table name is invalid
        """
        _validate_identifier(table, "table")
        query = f"SELECT COUNT(*) FROM {table}"
        if where:
            query += f" WHERE {where}"
        return await self.aggregate(query, params, AggregationType.SUM)

    async def find_by_id(
        self,
        table: str,
        id_column: str,
        id_value: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single row by ID across all shards.

        Args:
            table: Table name (must be a valid SQL identifier)
            id_column: ID column name (must be a valid SQL identifier)
            id_value: ID value to search for

        Returns:
            Row dict if found, None otherwise

        Raises:
            ValueError: If table or column name is invalid
        """
        _validate_identifier(table, "table")
        _validate_identifier(id_column, "column")
        query = f"SELECT * FROM {table} WHERE {id_column} = $1 LIMIT 1"
        result = await self.search(query, (id_value,), limit=1)

        if result.data:
            return result.data[0]
        return None
