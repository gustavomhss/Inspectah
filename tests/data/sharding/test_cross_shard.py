"""
Tests for CrossShardQueryExecutor.

S39 - Cross-Shard Query Tests
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.data.sharding.router import Domain, ShardRouter
from app.data.sharding.cross_shard import (
    AggregationType,
    CrossShardResult,
    CrossShardQueryExecutor,
    ShardQueryResult,
    _validate_identifier,
)


class TestCrossShardResult:
    """Tests for CrossShardResult."""

    def test_result_creation(self):
        """Test creating cross-shard result."""
        result = CrossShardResult(
            data=[{"count": 100}],
            shards_queried=["default", "politica"],
            shards_succeeded=["default", "politica"],
            shards_failed=[],
            is_partial=False,
            total_time_ms=50.0,
        )

        assert result.data == [{"count": 100}]
        assert len(result.shards_queried) == 2
        assert not result.is_partial

    def test_success_rate_all_success(self):
        """Test success rate when all shards succeed."""
        result = CrossShardResult(
            data=[],
            shards_queried=["default", "politica", "economia", "saude"],
            shards_succeeded=["default", "politica", "economia", "saude"],
            shards_failed=[],
            is_partial=False,
            total_time_ms=50.0,
        )

        assert result.success_rate == 1.0

    def test_success_rate_partial(self):
        """Test success rate with partial failure."""
        result = CrossShardResult(
            data=[],
            shards_queried=["default", "politica", "economia", "saude"],
            shards_succeeded=["default", "politica"],
            shards_failed=["economia", "saude"],
            is_partial=True,
            total_time_ms=50.0,
        )

        assert result.success_rate == 0.5

    def test_success_rate_empty(self):
        """Test success rate with no shards."""
        result = CrossShardResult(
            data=[],
            shards_queried=[],
            shards_succeeded=[],
            shards_failed=[],
            is_partial=False,
            total_time_ms=0.0,
        )

        assert result.success_rate == 0.0

    def test_to_dict(self):
        """Test converting result to dict."""
        result = CrossShardResult(
            data=[{"count": 100}],
            shards_queried=["default"],
            shards_succeeded=["default"],
            shards_failed=[],
            is_partial=False,
            total_time_ms=50.0,
            metadata={"test": "value"},
        )

        d = result.to_dict()

        assert d["data"] == [{"count": 100}]
        assert d["success_rate"] == 1.0
        assert d["metadata"] == {"test": "value"}


class TestShardQueryResult:
    """Tests for ShardQueryResult."""

    def test_successful_result(self):
        """Test successful shard query result."""
        result = ShardQueryResult(
            domain=Domain.DEFAULT,
            success=True,
            data=[{"id": 1}],
            latency_ms=10.0,
        )

        assert result.success
        assert result.error is None

    def test_failed_result(self):
        """Test failed shard query result."""
        result = ShardQueryResult(
            domain=Domain.POLITICA,
            success=False,
            data=None,
            error="Connection timeout",
            latency_ms=5000.0,
        )

        assert not result.success
        assert result.error == "Connection timeout"


class TestAggregationType:
    """Tests for AggregationType enum."""

    def test_aggregation_types(self):
        """Test all aggregation types exist."""
        assert AggregationType.SUM.value == "SUM"
        assert AggregationType.COUNT.value == "COUNT"
        assert AggregationType.AVG.value == "AVG"
        assert AggregationType.MAX.value == "MAX"
        assert AggregationType.MIN.value == "MIN"
        assert AggregationType.COLLECT.value == "COLLECT"


class TestCrossShardQueryExecutor:
    """Tests for CrossShardQueryExecutor."""

    def test_executor_creation(self):
        """Test creating executor."""
        router = ShardRouter()
        executor = CrossShardQueryExecutor(router)

        assert executor.router == router
        assert executor.timeout == 5.0
        assert executor.retry_count == 1

    def test_executor_custom_timeout(self):
        """Test executor with custom timeout."""
        router = ShardRouter()
        executor = CrossShardQueryExecutor(router, timeout_seconds=10.0, retry_count=3)

        assert executor.timeout == 10.0
        assert executor.retry_count == 3


class TestCrossShardQueryExecutorAsync:
    """Async tests for CrossShardQueryExecutor."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        return router

    @pytest.mark.asyncio
    async def test_aggregate_sum(self, mock_router):
        """Test SUM aggregation across shards."""
        # Setup mock connections
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=[10, 20, 30, 40])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            aggregation=AggregationType.SUM,
        )

        assert result.data[0]["result"] == 100  # 10 + 20 + 30 + 40
        assert len(result.shards_succeeded) == 4
        assert not result.is_partial

    @pytest.mark.asyncio
    async def test_aggregate_avg(self, mock_router):
        """Test AVG aggregation across shards."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=[10, 20, 30, 40])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT AVG(score) FROM claims",
            aggregation=AggregationType.AVG,
        )

        assert result.data[0]["result"] == 25  # (10 + 20 + 30 + 40) / 4

    @pytest.mark.asyncio
    async def test_aggregate_max(self, mock_router):
        """Test MAX aggregation across shards."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=[10, 50, 30, 20])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT MAX(created_at) FROM claims",
            aggregation=AggregationType.MAX,
        )

        assert result.data[0]["result"] == 50

    @pytest.mark.asyncio
    async def test_aggregate_min(self, mock_router):
        """Test MIN aggregation across shards."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=[10, 50, 30, 5])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT MIN(created_at) FROM claims",
            aggregation=AggregationType.MIN,
        )

        assert result.data[0]["result"] == 5

    @pytest.mark.asyncio
    async def test_aggregate_with_partial_failure(self, mock_router):
        """Test aggregation with some shards failing."""
        mock_conn = AsyncMock()
        # First two succeed, last two fail
        mock_conn.fetchval = AsyncMock(side_effect=[10, 20, Exception("Timeout"), Exception("Timeout")])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router, retry_count=0)

        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            aggregation=AggregationType.SUM,
        )

        # Should still work with partial results
        assert result.data[0]["result"] == 30  # 10 + 20
        assert result.is_partial
        assert len(result.shards_failed) == 2

    @pytest.mark.asyncio
    async def test_search_merge_and_sort(self, mock_router):
        """Test search with merge and sort."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": 1, "score": 90}],
            [{"id": 2, "score": 80}],
            [{"id": 3, "score": 95}],
            [{"id": 4, "score": 85}],
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.search(
            "SELECT * FROM claims ORDER BY score DESC",
            limit=10,
            sort_key="score",
            sort_reverse=True,
        )

        # Should be sorted by score descending
        scores = [r["score"] for r in result.data]
        assert scores == [95, 90, 85, 80]

    @pytest.mark.asyncio
    async def test_search_with_limit(self, mock_router):
        """Test search with limit."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": i} for i in range(10)],
            [{"id": i} for i in range(10, 20)],
            [{"id": i} for i in range(20, 30)],
            [{"id": i} for i in range(30, 40)],
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.search(
            "SELECT * FROM claims",
            limit=5,
        )

        assert len(result.data) == 5
        assert result.metadata["total_rows_before_limit"] == 40

    @pytest.mark.asyncio
    async def test_search_adds_shard_info(self, mock_router):
        """Test search adds _shard field to results."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[{"id": 1}])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.search("SELECT * FROM claims", limit=100)

        # Each row should have _shard field
        for row in result.data:
            assert "_shard" in row

    @pytest.mark.asyncio
    async def test_count_all(self, mock_router):
        """Test count_all helper."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value=25)

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.count_all("claims")

        assert result.data[0]["result"] == 100  # 25 * 4 shards

    @pytest.mark.asyncio
    async def test_count_all_with_where(self, mock_router):
        """Test count_all with WHERE clause."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value=5)

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.count_all(
            "claims",
            where="status = $1",
            params=("verified",),
        )

        assert result.data[0]["result"] == 20  # 5 * 4 shards

    @pytest.mark.asyncio
    async def test_find_by_id_found(self, mock_router):
        """Test find_by_id when record exists."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=[
            [],  # Not in default
            [{"id": "123", "text": "Found"}],  # Found in politica
            [],  # Not checked (already found)
            [],  # Not checked
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.find_by_id("claims", "id", "123")

        assert result is not None
        assert result["id"] == "123"
        assert result["text"] == "Found"

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, mock_router):
        """Test find_by_id when record doesn't exist."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.find_by_id("claims", "id", "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_execute_raw(self, mock_router):
        """Test execute_raw without aggregation."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": 1}],
            [{"id": 2}],
            [{"id": 3}],
            [{"id": 4}],
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.execute_raw("SELECT * FROM claims")

        # Results should be organized by shard
        assert len(result.data) == 1  # Dict wrapper
        assert "default" in result.data[0]
        assert "politica" in result.data[0]

    @pytest.mark.asyncio
    async def test_specific_domains(self, mock_router):
        """Test querying specific domains only."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value=10)

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            domains=[Domain.POLITICA, Domain.ECONOMIA],
            aggregation=AggregationType.SUM,
        )

        assert len(result.shards_queried) == 2
        assert result.data[0]["result"] == 20  # 10 * 2 shards

    @pytest.mark.asyncio
    async def test_aggregate_count(self, mock_router):
        """Test COUNT aggregation across shards."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=[10, 20, 30, 40])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            aggregation=AggregationType.COUNT,
        )

        assert result.data[0]["result"] == 100  # 10 + 20 + 30 + 40

    @pytest.mark.asyncio
    async def test_aggregate_collect(self, mock_router):
        """Test COLLECT aggregation across shards."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=["a", "b", "c", "d"])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.aggregate(
            "SELECT name FROM claims LIMIT 1",
            aggregation=AggregationType.COLLECT,
        )

        assert set(result.data[0]["result"]) == {"a", "b", "c", "d"}

    @pytest.mark.asyncio
    async def test_aggregate_all_fail_empty_result(self, mock_router):
        """Test aggregation when all shards fail."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=Exception("All fail"))

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router, retry_count=0)

        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            aggregation=AggregationType.SUM,
        )

        assert result.data[0]["result"] is None
        assert result.is_partial
        assert len(result.shards_failed) == 4

    @pytest.mark.asyncio
    async def test_aggregate_with_retry_success(self, mock_router):
        """Test aggregation with single shard to verify retry."""
        mock_conn = AsyncMock()
        # First call fails, second succeeds
        mock_conn.fetchval = AsyncMock(side_effect=[
            Exception("Fail"), 10,  # retry succeeds
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router, retry_count=1)

        # Test with single domain to verify retry logic
        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            aggregation=AggregationType.SUM,
            domains=[Domain.DEFAULT],
        )

        # Should succeed with retry value
        assert result.data[0]["result"] == 10
        assert not result.is_partial

    @pytest.mark.asyncio
    async def test_search_with_fetchrow_path(self, mock_router):
        """Test find_by_id which uses fetch internally."""
        mock_conn = AsyncMock()
        # find_by_id uses fetch, not fetchrow
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": "test_id", "data": "test1"}],  # Found in first shard
            [],  # Not checked
            [],
            [],
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor.find_by_id("claims", "id", "test_id")

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.asyncio
    async def test_timeout_with_retry(self, mock_router):
        """Test timeout handling with retry."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=asyncio.TimeoutError())

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router, timeout_seconds=0.01, retry_count=1)

        result = await executor.aggregate(
            "SELECT COUNT(*) FROM claims",
            aggregation=AggregationType.SUM,
        )

        assert result.is_partial
        assert len(result.shards_failed) == 4

    @pytest.mark.asyncio
    async def test_search_with_failure(self, mock_router):
        """Test search with some shards failing."""
        mock_conn = AsyncMock()
        # First two succeed, last two fail
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": 1, "score": 90}],
            [{"id": 2, "score": 80}],
            Exception("Connection error"),
            Exception("Timeout"),
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router, retry_count=0)

        result = await executor.search(
            "SELECT * FROM claims",
            limit=10,
        )

        assert len(result.shards_failed) == 2
        assert result.is_partial

    @pytest.mark.asyncio
    async def test_search_with_merge_function(self, mock_router):
        """Test search with custom merge function."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": 1, "type": "a"}],
            [{"id": 2, "type": "b"}],
            [{"id": 3, "type": "a"}],
            [{"id": 4, "type": "b"}],
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        # Custom merge function that groups by type
        def group_by_type(rows):
            return sorted(rows, key=lambda x: x["type"])

        result = await executor.search(
            "SELECT * FROM claims",
            limit=10,
            merge_fn=group_by_type,
        )

        # Should be sorted by type due to merge_fn
        types = [r["type"] for r in result.data]
        assert types == sorted(types)

    @pytest.mark.asyncio
    async def test_execute_raw_with_failure(self, mock_router):
        """Test execute_raw with some shards failing."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=[
            [{"id": 1}],
            [{"id": 2}],
            Exception("Shard error"),
            Exception("Timeout"),
        ])

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router, retry_count=0)

        result = await executor.execute_raw("SELECT * FROM claims")

        assert result.is_partial
        assert len(result.shards_failed) == 2

    @pytest.mark.asyncio
    async def test_query_single_shard_fetchrow(self, mock_router):
        """Test _query_single_shard with fetchrow method."""
        mock_conn = AsyncMock()
        mock_row = MagicMock()
        mock_row.__iter__ = MagicMock(return_value=iter([("id", 1), ("text", "test")]))
        mock_row.keys = MagicMock(return_value=["id", "text"])
        mock_row.__getitem__ = MagicMock(side_effect=lambda k: {"id": 1, "text": "test"}[k])
        mock_conn.fetchrow = AsyncMock(return_value=mock_row)

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor._query_single_shard(
            Domain.DEFAULT,
            "SELECT * FROM claims WHERE id = $1",
            (1,),
            fetch_method="fetchrow",
        )

        assert result.success
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_query_single_shard_fetchrow_none(self, mock_router):
        """Test _query_single_shard with fetchrow returning None."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        mock_router.get_connection.return_value.__aenter__.return_value = mock_conn

        executor = CrossShardQueryExecutor(mock_router)

        result = await executor._query_single_shard(
            Domain.DEFAULT,
            "SELECT * FROM claims WHERE id = $1",
            (1,),
            fetch_method="fetchrow",
        )

        assert result.success
        assert result.data is None


class TestSQLInjectionValidation:
    """Tests for SQL injection prevention via identifier validation."""

    def test_validate_identifier_valid_names(self):
        """Test validation passes for valid SQL identifiers."""
        valid_names = [
            "claims",
            "users",
            "test_table",
            "_private",
            "Table1",
            "my_table_2",
        ]
        for name in valid_names:
            # Should not raise
            _validate_identifier(name, "table")

    def test_validate_identifier_invalid_names(self):
        """Test validation rejects invalid SQL identifiers."""
        invalid_names = [
            "claims; DROP TABLE users;--",
            "table name",
            "table-name",
            "123table",
            "",
            "table.column",
            "table'injection",
            'table"injection',
            "table`injection",
        ]
        for name in invalid_names:
            with pytest.raises(ValueError, match="Invalid"):
                _validate_identifier(name, "table")

    def test_validate_identifier_none_raises(self):
        """Test validation rejects None."""
        with pytest.raises(ValueError, match="Invalid"):
            _validate_identifier(None, "table")

    @pytest.mark.asyncio
    async def test_count_all_rejects_sql_injection(self):
        """Test count_all rejects SQL injection attempts."""
        router = MagicMock(spec=ShardRouter)
        executor = CrossShardQueryExecutor(router)

        with pytest.raises(ValueError, match="Invalid table"):
            await executor.count_all("claims; DROP TABLE users;--")

    @pytest.mark.asyncio
    async def test_count_all_rejects_special_chars(self):
        """Test count_all rejects tables with special characters."""
        router = MagicMock(spec=ShardRouter)
        executor = CrossShardQueryExecutor(router)

        with pytest.raises(ValueError, match="Invalid table"):
            await executor.count_all("table'name")

    @pytest.mark.asyncio
    async def test_find_by_id_rejects_sql_injection_table(self):
        """Test find_by_id rejects SQL injection in table name."""
        router = MagicMock(spec=ShardRouter)
        executor = CrossShardQueryExecutor(router)

        with pytest.raises(ValueError, match="Invalid table"):
            await executor.find_by_id("claims; DROP TABLE users;--", "id", "123")

    @pytest.mark.asyncio
    async def test_find_by_id_rejects_sql_injection_column(self):
        """Test find_by_id rejects SQL injection in column name."""
        router = MagicMock(spec=ShardRouter)
        executor = CrossShardQueryExecutor(router)

        with pytest.raises(ValueError, match="Invalid column"):
            await executor.find_by_id("claims", "id; DROP TABLE--", "123")

    @pytest.mark.asyncio
    async def test_find_by_id_rejects_empty_table(self):
        """Test find_by_id rejects empty table name."""
        router = MagicMock(spec=ShardRouter)
        executor = CrossShardQueryExecutor(router)

        with pytest.raises(ValueError, match="Invalid table"):
            await executor.find_by_id("", "id", "123")

    @pytest.mark.asyncio
    async def test_find_by_id_rejects_empty_column(self):
        """Test find_by_id rejects empty column name."""
        router = MagicMock(spec=ShardRouter)
        executor = CrossShardQueryExecutor(router)

        with pytest.raises(ValueError, match="Invalid column"):
            await executor.find_by_id("claims", "", "123")
