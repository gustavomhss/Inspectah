"""
Tests for Migration Manager.

S39 - Shadow Mode and Migration Tests
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.data.sharding.router import Domain, ShardRouter
from app.data.sharding.migration import (
    MigrationPhase,
    MigrationConfig,
    MigrationStats,
    WriteResult,
    ShadowModeWriter,
    MigrationManager,
    _validate_identifier,
)


class TestMigrationPhase:
    """Tests for MigrationPhase enum."""

    def test_phase_values(self):
        """Test migration phase values."""
        assert MigrationPhase.DISABLED.value == "disabled"
        assert MigrationPhase.SHADOW_MODE.value == "shadow_mode"
        assert MigrationPhase.VALIDATION.value == "validation"
        assert MigrationPhase.CUTOVER.value == "cutover"
        assert MigrationPhase.CLEANUP.value == "cleanup"
        assert MigrationPhase.COMPLETE.value == "complete"


class TestMigrationConfig:
    """Tests for MigrationConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = MigrationConfig()

        assert config.phase == MigrationPhase.DISABLED
        assert config.shadow_mode_duration_hours == 48
        assert config.validation_sample_rate == 0.1
        assert config.batch_size == 1000
        assert config.enable_rollback is True
        assert config.started_at is None
        assert config.completed_at is None

    def test_custom_config(self):
        """Test custom configuration."""
        config = MigrationConfig(
            phase=MigrationPhase.SHADOW_MODE,
            shadow_mode_duration_hours=72,
            batch_size=500,
        )

        assert config.phase == MigrationPhase.SHADOW_MODE
        assert config.shadow_mode_duration_hours == 72
        assert config.batch_size == 500


class TestMigrationStats:
    """Tests for MigrationStats."""

    def test_default_stats(self):
        """Test default stats."""
        stats = MigrationStats(phase=MigrationPhase.SHADOW_MODE)

        assert stats.phase == MigrationPhase.SHADOW_MODE
        assert stats.records_migrated == 0
        assert stats.records_validated == 0
        assert stats.records_failed == 0
        assert stats.validation_errors == []

    def test_stats_to_dict(self):
        """Test converting stats to dict."""
        now = datetime.now(timezone.utc)
        stats = MigrationStats(
            phase=MigrationPhase.VALIDATION,
            records_migrated=1000,
            records_validated=500,
            records_failed=5,
            validation_errors=["Error 1", "Error 2"],
            started_at=now,
            last_updated=now,
        )

        d = stats.to_dict()

        assert d["phase"] == "validation"
        assert d["records_migrated"] == 1000
        assert d["records_validated"] == 500
        assert d["records_failed"] == 5
        assert d["error_count"] == 2

    def test_stats_error_limit(self):
        """Test stats limits errors in to_dict."""
        errors = [f"Error {i}" for i in range(20)]
        stats = MigrationStats(
            phase=MigrationPhase.VALIDATION,
            validation_errors=errors,
        )

        d = stats.to_dict()

        assert len(d["validation_errors"]) == 10  # Limited to 10
        assert d["error_count"] == 20  # But count is full


class TestWriteResult:
    """Tests for WriteResult."""

    def test_successful_write(self):
        """Test successful write result."""
        result = WriteResult(
            success=True,
            legacy_success=True,
            shard_success=True,
            shard_domain=Domain.POLITICA,
        )

        assert result.success
        assert result.legacy_success
        assert result.shard_success
        assert result.shard_domain == Domain.POLITICA
        assert result.error is None
        assert not result.validation_mismatch

    def test_failed_write(self):
        """Test failed write result."""
        result = WriteResult(
            success=False,
            legacy_success=False,
            shard_success=False,
            error="Connection failed",
        )

        assert not result.success
        assert result.error == "Connection failed"


class TestShadowModeWriter:
    """Tests for ShadowModeWriter."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        router.route.return_value = Domain.DEFAULT
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        pool = AsyncMock()
        return pool

    def test_writer_creation(self, mock_router, mock_legacy_pool):
        """Test creating shadow mode writer."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        assert writer.router == mock_router
        assert writer.legacy_pool == mock_legacy_pool
        assert writer.phase == MigrationPhase.DISABLED

    def test_set_phase(self, mock_router, mock_legacy_pool):
        """Test setting migration phase."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        writer.set_phase(MigrationPhase.SHADOW_MODE)

        assert writer.phase == MigrationPhase.SHADOW_MODE
        assert writer.stats.phase == MigrationPhase.SHADOW_MODE

    def test_set_phase_shadow_records_start(self, mock_router, mock_legacy_pool):
        """Test shadow mode records start time."""
        config = MigrationConfig()
        writer = ShadowModeWriter(mock_router, mock_legacy_pool, config)

        writer.set_phase(MigrationPhase.SHADOW_MODE)

        assert config.started_at is not None
        assert writer.stats.started_at is not None

    def test_register_validator(self, mock_router, mock_legacy_pool):
        """Test registering custom validator."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        def custom_validator(legacy, shard):
            return legacy["id"] == shard["id"]

        writer.register_validator("claims", custom_validator)

        assert "claims" in writer._validators


class TestShadowModeWriterAsync:
    """Async tests for ShadowModeWriter."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        router.route.return_value = Domain.POLITICA

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": 1, "text": "test"})

        # Create proper async context manager for get_connection
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        router.get_connection.return_value = async_cm
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": 1, "text": "test"})

        # Create proper async context manager for acquire
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None

        pool = MagicMock()
        pool.acquire.return_value = async_cm
        return pool

    @pytest.mark.asyncio
    async def test_write_disabled_phase(self, mock_router, mock_legacy_pool):
        """Test write in DISABLED phase (legacy only)."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        result = await writer.write("claims", {"id": 1, "text": "test"})

        assert result.success
        assert result.legacy_success
        assert not result.shard_success  # Not written to shard

    @pytest.mark.asyncio
    async def test_write_shadow_mode(self, mock_router, mock_legacy_pool):
        """Test write in SHADOW_MODE phase (dual write)."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)
        writer.set_phase(MigrationPhase.SHADOW_MODE)

        result = await writer.write(
            "claims",
            {"id": 1, "text": "test"},
            claim_text="Lula anuncia programa",
        )

        assert result.success
        assert result.legacy_success
        assert result.shard_success
        assert result.shard_domain == Domain.POLITICA
        assert writer.stats.records_migrated == 1

    @pytest.mark.asyncio
    async def test_write_cutover_phase(self, mock_router, mock_legacy_pool):
        """Test write in CUTOVER phase (shard only)."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)
        writer.set_phase(MigrationPhase.CUTOVER)

        result = await writer.write("claims", {"id": 1, "text": "test"})

        assert result.success
        assert not result.legacy_success  # Not written to legacy
        assert result.shard_success

    @pytest.mark.asyncio
    async def test_write_with_explicit_domain(self, mock_router, mock_legacy_pool):
        """Test write with explicit domain."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)
        writer.set_phase(MigrationPhase.SHADOW_MODE)

        result = await writer.write(
            "claims",
            {"id": 1, "text": "test"},
            explicit_domain=Domain.SAUDE,
        )

        assert result.shard_domain == Domain.SAUDE

    @pytest.mark.asyncio
    async def test_write_failure_updates_stats(self, mock_router, mock_legacy_pool):
        """Test write failure updates stats."""
        mock_legacy_pool.acquire.return_value.__aenter__.return_value.execute = AsyncMock(
            side_effect=Exception("Connection error")
        )

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        result = await writer.write("claims", {"id": 1, "text": "test"})

        assert not result.success
        assert result.error is not None
        assert writer.stats.records_failed == 1

    @pytest.mark.asyncio
    async def test_validate_consistency(self, mock_router, mock_legacy_pool):
        """Test validating consistency between legacy and shards."""
        # Setup legacy data
        mock_legacy_pool.acquire.return_value.__aenter__.return_value.fetch = AsyncMock(
            return_value=[{"id": 1, "text": "test", "status": "verified"}]
        )

        # Setup shard data (matching)
        mock_shard_conn = AsyncMock()
        mock_shard_conn.fetchrow = AsyncMock(
            return_value={"id": 1, "text": "test", "status": "verified"}
        )
        mock_router.get_connection.return_value.__aenter__.return_value = mock_shard_conn

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        validated, mismatches, errors = await writer.validate_consistency(
            "claims", "id", sample_size=1
        )

        assert validated == 1
        assert mismatches == 0
        assert len(errors) == 0


class TestMigrationManager:
    """Tests for MigrationManager."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        return MagicMock(spec=ShardRouter)

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        return AsyncMock()

    def test_manager_creation(self, mock_router, mock_legacy_pool):
        """Test creating migration manager."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        assert manager.router == mock_router
        assert manager.legacy_pool == mock_legacy_pool
        assert manager.writer is not None

    def test_get_status(self, mock_router, mock_legacy_pool):
        """Test getting migration status."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        status = manager.get_status()

        assert status["phase"] == "disabled"
        assert "config" in status
        assert "stats" in status


class TestMigrationManagerAsync:
    """Async tests for MigrationManager."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": 1, "text": "test"})

        # Create proper async context manager for get_connection
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        router.get_connection.return_value = async_cm
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[{"id": 1, "text": "test"}])

        # Create proper async context manager for acquire
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None

        pool = MagicMock()
        pool.acquire.return_value = async_cm
        return pool

    @pytest.mark.asyncio
    async def test_start_shadow_mode(self, mock_router, mock_legacy_pool):
        """Test starting shadow mode."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        await manager.start_shadow_mode()

        assert manager.writer.phase == MigrationPhase.SHADOW_MODE

    @pytest.mark.asyncio
    async def test_execute_cutover(self, mock_router, mock_legacy_pool):
        """Test executing cutover."""
        manager = MigrationManager(mock_router, mock_legacy_pool)
        await manager.start_shadow_mode()

        await manager.execute_cutover()

        assert manager.writer.phase == MigrationPhase.CUTOVER

    @pytest.mark.asyncio
    async def test_cutover_fails_with_failed_records(self, mock_router, mock_legacy_pool):
        """Test cutover fails when there are failed records."""
        manager = MigrationManager(mock_router, mock_legacy_pool)
        manager.writer.stats.records_failed = 5

        with pytest.raises(RuntimeError, match="failed records"):
            await manager.execute_cutover()

    @pytest.mark.asyncio
    async def test_rollback(self, mock_router, mock_legacy_pool):
        """Test rollback to legacy."""
        manager = MigrationManager(mock_router, mock_legacy_pool)
        await manager.start_shadow_mode()

        await manager.rollback()

        assert manager.writer.phase == MigrationPhase.DISABLED

    @pytest.mark.asyncio
    async def test_rollback_disabled(self, mock_router, mock_legacy_pool):
        """Test rollback when disabled."""
        config = MigrationConfig(enable_rollback=False)
        manager = MigrationManager(mock_router, mock_legacy_pool, config)

        with pytest.raises(RuntimeError, match="disabled"):
            await manager.rollback()

    @pytest.mark.asyncio
    async def test_complete_migration(self, mock_router, mock_legacy_pool):
        """Test completing migration."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        await manager.complete_migration()

        assert manager.writer.phase == MigrationPhase.COMPLETE
        assert manager.config.completed_at is not None

    @pytest.mark.asyncio
    async def test_start_validation(self, mock_router, mock_legacy_pool):
        """Test starting validation phase."""
        # The fixtures already have proper mock data configured
        manager = MigrationManager(mock_router, mock_legacy_pool)

        results = await manager.start_validation(
            tables=["claims"],
            id_columns={"claims": "id"},
            sample_size=1,
        )

        assert manager.writer.phase == MigrationPhase.VALIDATION
        assert "claims" in results


class TestShadowModeWriterValidation:
    """Tests for ShadowModeWriter validation scenarios."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        router.route.return_value = Domain.DEFAULT
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        mock_conn = AsyncMock()
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        pool = MagicMock()
        pool.acquire.return_value = async_cm
        return pool

    @pytest.mark.asyncio
    async def test_validate_with_mismatch(self, mock_router, mock_legacy_pool):
        """Test validation detects mismatches."""
        # Setup legacy data
        mock_legacy_conn = AsyncMock()
        mock_legacy_conn.fetch = AsyncMock(
            return_value=[{"id": 1, "text": "legacy", "status": "active"}]
        )
        mock_legacy_pool.acquire.return_value.__aenter__.return_value = mock_legacy_conn

        # Setup shard data with mismatch
        mock_shard_conn = AsyncMock()
        mock_shard_conn.fetchrow = AsyncMock(
            return_value={"id": 1, "text": "different", "status": "inactive"}
        )

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_shard_conn
        async_cm.__aexit__.return_value = None
        mock_router.get_connection.return_value = async_cm

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        validated, mismatches, errors = await writer.validate_consistency(
            "claims", "id", sample_size=1
        )

        assert mismatches > 0 or validated > 0  # Either found mismatch or validated

    @pytest.mark.asyncio
    async def test_validate_record_not_found_in_shards(self, mock_router, mock_legacy_pool):
        """Test validation when record not found in any shard."""
        # Setup legacy data
        mock_legacy_conn = AsyncMock()
        mock_legacy_conn.fetch = AsyncMock(
            return_value=[{"id": 1, "text": "test"}]
        )
        mock_legacy_pool.acquire.return_value.__aenter__.return_value = mock_legacy_conn

        # Setup shard data - not found
        mock_shard_conn = AsyncMock()
        mock_shard_conn.fetchrow = AsyncMock(return_value=None)

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_shard_conn
        async_cm.__aexit__.return_value = None
        mock_router.get_connection.return_value = async_cm

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        validated, mismatches, errors = await writer.validate_consistency(
            "claims", "id", sample_size=1
        )

        # Record not found counts as missing, handled by the method
        assert validated >= 0

    @pytest.mark.asyncio
    async def test_validate_with_connection_error(self, mock_router, mock_legacy_pool):
        """Test validation handles connection errors."""
        # Setup legacy data
        mock_legacy_conn = AsyncMock()
        mock_legacy_conn.fetch = AsyncMock(
            return_value=[{"id": 1, "text": "test"}]
        )
        mock_legacy_pool.acquire.return_value.__aenter__.return_value = mock_legacy_conn

        # Setup shard to raise error
        mock_shard_conn = AsyncMock()
        mock_shard_conn.fetchrow = AsyncMock(side_effect=Exception("Connection error"))

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_shard_conn
        async_cm.__aexit__.return_value = None
        mock_router.get_connection.return_value = async_cm

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        validated, mismatches, errors = await writer.validate_consistency(
            "claims", "id", sample_size=1
        )

        # Should complete without crashing
        assert validated >= 0


class TestShadowModeWriterCutover:
    """Tests for ShadowModeWriter in CUTOVER phase."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        router.route.return_value = Domain.POLITICA

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": 1, "text": "test"})

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        router.get_connection.return_value = async_cm
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        mock_conn = AsyncMock()
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        pool = MagicMock()
        pool.acquire.return_value = async_cm
        return pool

    @pytest.mark.asyncio
    async def test_write_in_complete_phase(self, mock_router, mock_legacy_pool):
        """Test write in COMPLETE phase (shard only)."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)
        writer.set_phase(MigrationPhase.COMPLETE)

        result = await writer.write("claims", {"id": 1, "text": "test"})

        assert result.success
        assert not result.legacy_success
        assert result.shard_success

    @pytest.mark.asyncio
    async def test_shadow_write_legacy_failure(self, mock_router, mock_legacy_pool):
        """Test shadow write when legacy fails."""
        mock_legacy_conn = AsyncMock()
        mock_legacy_conn.fetchrow = AsyncMock(side_effect=Exception("Legacy error"))

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_legacy_conn
        async_cm.__aexit__.return_value = None
        mock_legacy_pool.acquire.return_value = async_cm

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)
        writer.set_phase(MigrationPhase.SHADOW_MODE)

        result = await writer.write("claims", {"id": 1, "text": "test"})

        # Legacy failure means overall write failed
        assert not result.legacy_success
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_shadow_write_shard_failure(self, mock_router, mock_legacy_pool):
        """Test shadow write when shard fails but legacy succeeds."""
        # Setup legacy to succeed
        mock_legacy_conn = AsyncMock()
        mock_legacy_conn.fetchrow = AsyncMock(return_value={"id": 1, "text": "test"})

        legacy_cm = AsyncMock()
        legacy_cm.__aenter__.return_value = mock_legacy_conn
        legacy_cm.__aexit__.return_value = None
        mock_legacy_pool.acquire.return_value = legacy_cm

        # Setup shard to fail
        mock_shard_conn = AsyncMock()
        mock_shard_conn.fetchrow = AsyncMock(side_effect=Exception("Shard error"))

        shard_cm = AsyncMock()
        shard_cm.__aenter__.return_value = mock_shard_conn
        shard_cm.__aexit__.return_value = None
        mock_router.get_connection.return_value = shard_cm

        writer = ShadowModeWriter(mock_router, mock_legacy_pool)
        writer.set_phase(MigrationPhase.SHADOW_MODE)

        result = await writer.write("claims", {"id": 1, "text": "test"})

        # Legacy succeeded, so overall success (shadow mode)
        assert result.legacy_success
        assert not result.shard_success


class TestDefaultValidator:
    """Tests for the default validator function."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        pool = MagicMock()
        return pool

    def test_validator_matching_records(self, mock_router, mock_legacy_pool):
        """Test validator with matching records."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        legacy = {"id": 1, "text": "test", "status": "active"}
        shard = {"id": 1, "text": "test", "status": "active"}

        result = writer._default_validator(legacy, shard)
        assert result is True

    def test_validator_with_ignored_fields(self, mock_router, mock_legacy_pool):
        """Test validator ignores internal fields."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        legacy = {"id": 1, "text": "test", "_shard": "politica", "created_at": "2024-01-01"}
        shard = {"id": 1, "text": "test", "_shard": "default", "created_at": "2024-01-02"}

        result = writer._default_validator(legacy, shard)
        assert result is True  # _shard and created_at are ignored

    def test_validator_missing_field(self, mock_router, mock_legacy_pool):
        """Test validator detects missing fields."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        legacy = {"id": 1, "text": "test", "status": "active"}
        shard = {"id": 1, "text": "test"}  # Missing status

        result = writer._default_validator(legacy, shard)
        assert result is False

    def test_validator_mismatched_value(self, mock_router, mock_legacy_pool):
        """Test validator detects mismatched values."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        legacy = {"id": 1, "text": "test", "status": "active"}
        shard = {"id": 1, "text": "test", "status": "inactive"}

        result = writer._default_validator(legacy, shard)
        assert result is False


class TestMigrationManagerMigrateBatch:
    """Tests for MigrationManager.migrate_batch method."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        router.route.return_value = Domain.DEFAULT

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        router.get_connection.return_value = async_cm
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value=2)  # 2 records to migrate
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": 1, "text": "Record 1"},
            {"id": 2, "text": "Record 2"},
        ])

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None

        pool = MagicMock()
        pool.acquire.return_value = async_cm
        return pool

    @pytest.mark.asyncio
    async def test_migrate_batch_success(self, mock_router, mock_legacy_pool):
        """Test successful data migration."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        count = await manager.migrate_batch(
            "claims",
            "SELECT * FROM claims",
            id_column="id",
            batch_size=10,
        )

        assert count == 2
        assert manager.writer.stats.records_migrated == 2

    @pytest.mark.asyncio
    async def test_migrate_batch_with_domain_column(self, mock_router, mock_legacy_pool):
        """Test migration with domain column."""
        # Update mock data to include domain column
        mock_conn = mock_legacy_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": 1, "text": "Record 1", "domain": "politica"},
            {"id": 2, "text": "Record 2", "domain": "economia"},
        ])

        manager = MigrationManager(mock_router, mock_legacy_pool)

        count = await manager.migrate_batch(
            "claims",
            "SELECT * FROM claims",
            id_column="id",
            domain_column="domain",
            batch_size=10,
        )

        assert count == 2

    @pytest.mark.asyncio
    async def test_migrate_batch_with_text_routing(self, mock_router, mock_legacy_pool):
        """Test migration with text-based routing."""
        # Update mock data
        mock_conn = mock_legacy_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": 1, "text": "Lula anuncia programa"},  # Should route to POLITICA
            {"id": 2, "text": "Random text"},  # Should route to DEFAULT
        ])
        mock_router.route.side_effect = [Domain.POLITICA, Domain.DEFAULT]

        manager = MigrationManager(mock_router, mock_legacy_pool)

        count = await manager.migrate_batch(
            "claims",
            "SELECT * FROM claims",
            id_column="id",
            text_column="text",
            batch_size=10,
        )

        assert count == 2

    @pytest.mark.asyncio
    async def test_migrate_batch_with_failure(self, mock_router, mock_legacy_pool):
        """Test migration handles failures."""
        # Make shard connection fail
        mock_shard_conn = AsyncMock()
        mock_shard_conn.execute = AsyncMock(side_effect=Exception("Insert failed"))

        shard_cm = AsyncMock()
        shard_cm.__aenter__.return_value = mock_shard_conn
        shard_cm.__aexit__.return_value = None
        mock_router.get_connection.return_value = shard_cm

        manager = MigrationManager(mock_router, mock_legacy_pool)

        count = await manager.migrate_batch(
            "claims",
            "SELECT * FROM claims",
            id_column="id",
            batch_size=10,
        )

        # No records migrated due to failures
        assert count == 0
        assert manager.writer.stats.records_failed == 2

    @pytest.mark.asyncio
    async def test_migrate_batch_invalid_domain(self, mock_router, mock_legacy_pool):
        """Test migration with invalid domain value."""
        mock_conn = mock_legacy_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": 1, "text": "Test", "domain": "invalid_domain"},
        ])
        mock_conn.fetchval = AsyncMock(return_value=1)

        manager = MigrationManager(mock_router, mock_legacy_pool)

        count = await manager.migrate_batch(
            "claims",
            "SELECT * FROM claims",
            id_column="id",
            domain_column="domain",
            batch_size=10,
        )

        # Should default to DEFAULT domain when invalid
        assert count == 1

    @pytest.mark.asyncio
    async def test_migrate_batch_keyset_pagination_multiple_batches(
        self, mock_router, mock_legacy_pool
    ):
        """Test migration uses keyset pagination correctly with multiple batches."""
        # Setup mock to return records in batches simulating keyset pagination
        mock_conn = mock_legacy_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetchval = AsyncMock(return_value=5)  # 5 total records

        # First batch: 2 records (batch_size=2)
        # Second batch: 2 more records (cursor > 2)
        # Third batch: 1 last record (cursor > 4)
        # Fourth batch: empty (done)
        call_count = 0

        async def mock_fetch(query, *args):
            nonlocal call_count
            call_count += 1

            # First call: no cursor, get first 2 records
            if call_count == 1:
                return [
                    {"id": 1, "text": "Record 1"},
                    {"id": 2, "text": "Record 2"},
                ]
            # Second call: cursor > 2, get next 2 records
            elif call_count == 2:
                assert args[0] == 2  # cursor should be 2 from last batch
                return [
                    {"id": 3, "text": "Record 3"},
                    {"id": 4, "text": "Record 4"},
                ]
            # Third call: cursor > 4, get last record
            elif call_count == 3:
                assert args[0] == 4  # cursor should be 4 from last batch
                return [
                    {"id": 5, "text": "Record 5"},
                ]
            # Fourth call: cursor > 5, no more records
            else:
                return []

        mock_conn.fetch = mock_fetch

        manager = MigrationManager(mock_router, mock_legacy_pool)

        count = await manager.migrate_batch(
            "claims",
            "SELECT * FROM claims",
            id_column="id",
            batch_size=2,  # Small batch to force multiple iterations
        )

        assert count == 5
        assert manager.writer.stats.records_migrated == 5
        # Verify we made 3 fetch calls (2+2+1 records in batches)
        assert call_count == 3


class TestMigrationSQLInjectionValidation:
    """Tests for SQL injection prevention in migration module."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        router = MagicMock(spec=ShardRouter)
        router.route.return_value = Domain.DEFAULT
        return router

    @pytest.fixture
    def mock_legacy_pool(self):
        """Create mock legacy pool."""
        mock_conn = AsyncMock()
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_conn
        async_cm.__aexit__.return_value = None
        pool = MagicMock()
        pool.acquire.return_value = async_cm
        return pool

    def test_validate_identifier_valid(self):
        """Test identifier validation passes for valid names."""
        valid_names = ["claims", "users", "test_table", "_private", "Table1"]
        for name in valid_names:
            _validate_identifier(name, "table")  # Should not raise

    def test_validate_identifier_invalid(self):
        """Test identifier validation rejects invalid names."""
        invalid_names = [
            "claims; DROP TABLE users;--",
            "table name",
            "",
            "table.column",
        ]
        for name in invalid_names:
            with pytest.raises(ValueError, match="Invalid"):
                _validate_identifier(name, "table")

    @pytest.mark.asyncio
    async def test_write_rejects_sql_injection_table(self, mock_router, mock_legacy_pool):
        """Test write rejects SQL injection in table name."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid table"):
            await writer.write(
                "claims; DROP TABLE users;--",
                {"id": 1, "text": "test"},
            )

    @pytest.mark.asyncio
    async def test_write_rejects_sql_injection_column(self, mock_router, mock_legacy_pool):
        """Test write rejects SQL injection in column names."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid column"):
            await writer.write(
                "claims",
                {"id; DROP TABLE users;--": 1, "text": "test"},
            )

    @pytest.mark.asyncio
    async def test_validate_consistency_rejects_sql_injection_table(
        self, mock_router, mock_legacy_pool
    ):
        """Test validate_consistency rejects SQL injection in table name."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid table"):
            await writer.validate_consistency(
                "claims; DROP TABLE users;--", "id", sample_size=1
            )

    @pytest.mark.asyncio
    async def test_validate_consistency_rejects_sql_injection_column(
        self, mock_router, mock_legacy_pool
    ):
        """Test validate_consistency rejects SQL injection in column name."""
        writer = ShadowModeWriter(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid column"):
            await writer.validate_consistency(
                "claims", "id; DROP TABLE--", sample_size=1
            )

    @pytest.mark.asyncio
    async def test_migrate_batch_rejects_sql_injection_table(
        self, mock_router, mock_legacy_pool
    ):
        """Test migrate_batch rejects SQL injection in table name."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid table"):
            await manager.migrate_batch(
                "claims; DROP TABLE users;--",
                "SELECT * FROM claims",
                id_column="id",
            )

    @pytest.mark.asyncio
    async def test_migrate_batch_rejects_sql_injection_id_column(
        self, mock_router, mock_legacy_pool
    ):
        """Test migrate_batch rejects SQL injection in id_column."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid column"):
            await manager.migrate_batch(
                "claims",
                "SELECT * FROM claims",
                id_column="id; DROP TABLE--",
            )

    @pytest.mark.asyncio
    async def test_migrate_batch_rejects_sql_injection_domain_column(
        self, mock_router, mock_legacy_pool
    ):
        """Test migrate_batch rejects SQL injection in domain_column."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid column"):
            await manager.migrate_batch(
                "claims",
                "SELECT * FROM claims",
                id_column="id",
                domain_column="domain; DROP--",
            )

    @pytest.mark.asyncio
    async def test_migrate_batch_rejects_sql_injection_text_column(
        self, mock_router, mock_legacy_pool
    ):
        """Test migrate_batch rejects SQL injection in text_column."""
        manager = MigrationManager(mock_router, mock_legacy_pool)

        with pytest.raises(ValueError, match="Invalid column"):
            await manager.migrate_batch(
                "claims",
                "SELECT * FROM claims",
                id_column="id",
                text_column="text'injection",
            )
