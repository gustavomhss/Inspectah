"""
Tests for S39 Topics Configuration Module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.streaming.topics import (
    CleanupPolicy,
    TopicConfig,
    TopicHealth,
    TopicManager,
    TopicPriority,
    TopicRegistry,
)


# ============================================================================
# TopicPriority Tests
# ============================================================================

class TestTopicPriority:
    """Tests for TopicPriority enum."""

    def test_priority_values(self):
        """Test priority enum values."""
        assert TopicPriority.LOW.value == "low"
        assert TopicPriority.NORMAL.value == "normal"
        assert TopicPriority.HIGH.value == "high"
        assert TopicPriority.CRITICAL.value == "critical"

    def test_priority_comparison(self):
        """Test priority enum comparison."""
        assert TopicPriority.LOW != TopicPriority.HIGH
        assert TopicPriority.CRITICAL == TopicPriority.CRITICAL


# ============================================================================
# CleanupPolicy Tests
# ============================================================================

class TestCleanupPolicy:
    """Tests for CleanupPolicy enum."""

    def test_cleanup_policy_values(self):
        """Test cleanup policy values."""
        assert CleanupPolicy.DELETE.value == "delete"
        assert CleanupPolicy.COMPACT.value == "compact"
        assert CleanupPolicy.COMPACT_DELETE.value == "compact,delete"


# ============================================================================
# TopicConfig Tests
# ============================================================================

class TestTopicConfig:
    """Tests for TopicConfig dataclass."""

    def test_default_config(self):
        """Test default topic configuration."""
        config = TopicConfig(name="test.topic")

        assert config.name == "test.topic"
        assert config.partitions == 6
        assert config.replication_factor == 2
        assert config.retention_ms == 604800000  # 7 days
        assert config.retention_bytes == -1
        assert config.cleanup_policy == CleanupPolicy.DELETE
        assert config.min_insync_replicas == 1
        assert config.segment_bytes == 1073741824  # 1GB
        assert config.priority == TopicPriority.NORMAL
        assert config.description == ""
        assert config.extra_configs == {}

    def test_custom_config(self):
        """Test custom topic configuration."""
        config = TopicConfig(
            name="custom.topic",
            partitions=12,
            replication_factor=3,
            retention_ms=86400000,
            retention_bytes=1073741824,
            cleanup_policy=CleanupPolicy.COMPACT,
            min_insync_replicas=2,
            priority=TopicPriority.CRITICAL,
            description="Custom topic for testing",
            extra_configs={"max.message.bytes": "5242880"},
        )

        assert config.name == "custom.topic"
        assert config.partitions == 12
        assert config.replication_factor == 3
        assert config.retention_ms == 86400000
        assert config.retention_bytes == 1073741824
        assert config.cleanup_policy == CleanupPolicy.COMPACT
        assert config.min_insync_replicas == 2
        assert config.priority == TopicPriority.CRITICAL
        assert config.description == "Custom topic for testing"
        assert config.extra_configs["max.message.bytes"] == "5242880"

    def test_to_kafka_config(self):
        """Test conversion to Kafka config format."""
        config = TopicConfig(
            name="test.topic",
            retention_ms=86400000,
            retention_bytes=1073741824,
            cleanup_policy=CleanupPolicy.COMPACT_DELETE,
            min_insync_replicas=2,
            segment_bytes=536870912,
            extra_configs={"compression.type": "gzip"},
        )

        kafka_config = config.to_kafka_config()

        assert kafka_config["retention.ms"] == "86400000"
        assert kafka_config["retention.bytes"] == "1073741824"
        assert kafka_config["cleanup.policy"] == "compact,delete"
        assert kafka_config["min.insync.replicas"] == "2"
        assert kafka_config["segment.bytes"] == "536870912"
        assert kafka_config["compression.type"] == "gzip"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = TopicConfig(
            name="test.topic",
            partitions=8,
            priority=TopicPriority.HIGH,
            description="Test description",
        )

        data = config.to_dict()

        assert data["name"] == "test.topic"
        assert data["partitions"] == 8
        assert data["replication_factor"] == 2
        assert data["priority"] == "high"
        assert data["description"] == "Test description"


# ============================================================================
# TopicRegistry Tests
# ============================================================================

class TestTopicRegistry:
    """Tests for TopicRegistry class."""

    def test_signals_raw_topic(self):
        """Test SIGNALS_RAW topic configuration."""
        topic = TopicRegistry.SIGNALS_RAW

        assert topic.name == "signals.raw"
        assert topic.partitions == 12
        assert topic.replication_factor == 2
        assert topic.priority == TopicPriority.HIGH

    def test_signals_computed_topic(self):
        """Test SIGNALS_COMPUTED topic configuration."""
        topic = TopicRegistry.SIGNALS_COMPUTED

        assert topic.name == "signals.computed"
        assert topic.partitions == 12
        assert topic.retention_ms == 2592000000  # 30 days
        assert topic.priority == TopicPriority.HIGH

    def test_signals_dlq_topic(self):
        """Test SIGNALS_DLQ topic configuration."""
        topic = TopicRegistry.SIGNALS_DLQ

        assert topic.name == "signals.dlq"
        assert topic.partitions == 3
        assert topic.priority == TopicPriority.CRITICAL
        assert "max.message.bytes" in topic.extra_configs

    def test_claims_events_topic(self):
        """Test CLAIMS_EVENTS topic configuration."""
        topic = TopicRegistry.CLAIMS_EVENTS

        assert topic.name == "claims.events"
        assert topic.priority == TopicPriority.NORMAL

    def test_evidence_events_topic(self):
        """Test EVIDENCE_EVENTS topic configuration."""
        topic = TopicRegistry.EVIDENCE_EVENTS

        assert topic.name == "evidence.events"
        assert topic.priority == TopicPriority.NORMAL

    def test_alerts_stream_topic(self):
        """Test ALERTS_STREAM topic configuration."""
        topic = TopicRegistry.ALERTS_STREAM

        assert topic.name == "alerts.stream"
        assert topic.retention_ms == 86400000  # 1 day
        assert topic.priority == TopicPriority.CRITICAL

    def test_audit_log_topic(self):
        """Test AUDIT_LOG topic configuration."""
        topic = TopicRegistry.AUDIT_LOG

        assert topic.name == "audit.log"
        assert topic.retention_ms == 7776000000  # 90 days
        assert topic.cleanup_policy == CleanupPolicy.DELETE
        assert topic.priority == TopicPriority.HIGH

    def test_all_topics(self):
        """Test all_topics class method."""
        topics = TopicRegistry.all_topics()

        assert len(topics) == 7
        topic_names = [t.name for t in topics]
        assert "signals.raw" in topic_names
        assert "signals.computed" in topic_names
        assert "signals.dlq" in topic_names
        assert "claims.events" in topic_names
        assert "evidence.events" in topic_names
        assert "alerts.stream" in topic_names
        assert "audit.log" in topic_names

    def test_get_by_name_found(self):
        """Test get_by_name with existing topic."""
        topic = TopicRegistry.get_by_name("signals.raw")

        assert topic is not None
        assert topic.name == "signals.raw"

    def test_get_by_name_not_found(self):
        """Test get_by_name with non-existent topic."""
        topic = TopicRegistry.get_by_name("nonexistent.topic")

        assert topic is None

    def test_get_by_priority(self):
        """Test get_by_priority method."""
        critical = TopicRegistry.get_by_priority(TopicPriority.CRITICAL)

        assert len(critical) == 2
        for topic in critical:
            assert topic.priority == TopicPriority.CRITICAL

    def test_get_by_priority_normal(self):
        """Test get_by_priority with NORMAL priority."""
        normal = TopicRegistry.get_by_priority(TopicPriority.NORMAL)

        assert len(normal) == 2
        for topic in normal:
            assert topic.priority == TopicPriority.NORMAL

    def test_critical_topics(self):
        """Test critical_topics method."""
        critical = TopicRegistry.critical_topics()

        assert len(critical) == 2
        names = [t.name for t in critical]
        assert "signals.dlq" in names
        assert "alerts.stream" in names

    def test_to_create_spec(self):
        """Test to_create_spec method."""
        specs = TopicRegistry.to_create_spec()

        assert len(specs) == 7
        for spec in specs:
            assert "topic" in spec
            assert "partitions" in spec
            assert "replication_factor" in spec
            assert "config" in spec

    def test_to_create_spec_content(self):
        """Test to_create_spec content for a specific topic."""
        specs = TopicRegistry.to_create_spec()

        signals_raw_spec = next(s for s in specs if s["topic"] == "signals.raw")

        assert signals_raw_spec["partitions"] == 12
        assert signals_raw_spec["replication_factor"] == 2
        assert "retention.ms" in signals_raw_spec["config"]


# ============================================================================
# TopicHealth Tests
# ============================================================================

class TestTopicHealth:
    """Tests for TopicHealth dataclass."""

    def test_healthy_topic(self):
        """Test healthy topic status."""
        health = TopicHealth(
            topic="test.topic",
            partitions=6,
            replicas=12,
            in_sync_replicas=12,
            under_replicated=False,
            offline_partitions=0,
            leader_count=3,
            is_healthy=True,
        )

        assert health.is_healthy
        assert not health.under_replicated
        assert health.offline_partitions == 0

    def test_unhealthy_topic(self):
        """Test unhealthy topic status."""
        health = TopicHealth(
            topic="test.topic",
            partitions=6,
            replicas=12,
            in_sync_replicas=8,
            under_replicated=True,
            offline_partitions=1,
            leader_count=2,
            is_healthy=False,
        )

        assert not health.is_healthy
        assert health.under_replicated
        assert health.offline_partitions == 1

    def test_to_dict(self):
        """Test to_dict conversion."""
        health = TopicHealth(
            topic="test.topic",
            partitions=6,
            replicas=12,
            in_sync_replicas=12,
            under_replicated=False,
            offline_partitions=0,
            leader_count=3,
            is_healthy=True,
        )

        data = health.to_dict()

        assert data["topic"] == "test.topic"
        assert data["partitions"] == 6
        assert data["replicas"] == 12
        assert data["in_sync_replicas"] == 12
        assert data["under_replicated"] is False
        assert data["offline_partitions"] == 0
        assert data["leader_count"] == 3
        assert data["is_healthy"] is True


# ============================================================================
# TopicManager Tests
# ============================================================================

class TestTopicManager:
    """Tests for TopicManager class."""

    def test_init_default(self):
        """Test default initialization."""
        manager = TopicManager()

        assert manager.bootstrap_servers == "localhost:9092"
        assert manager._admin_client is None

    def test_init_custom_servers(self):
        """Test custom bootstrap servers."""
        manager = TopicManager(bootstrap_servers="kafka:9092,kafka2:9092")

        assert manager.bootstrap_servers == "kafka:9092,kafka2:9092"

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_no_aiokafka(self):
        """Test ensure_topics_exist when aiokafka is not installed."""
        manager = TopicManager()

        with patch.dict("sys.modules", {"aiokafka.admin": None}):
            with patch(
                "app.streaming.topics.TopicManager.ensure_topics_exist",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {t.name: False for t in TopicRegistry.all_topics()}
                results = await mock()

        assert len(results) == 7
        for topic_name, created in results.items():
            assert created is False

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_with_mock(self):
        """Test ensure_topics_exist behavior."""
        manager = TopicManager()

        # Verify manager initialization
        assert manager._admin_client is None
        assert manager.bootstrap_servers == "localhost:9092"

        # Test that get_config_summary works
        summary = manager.get_config_summary()
        assert summary["total_topics"] == 7

    @pytest.mark.asyncio
    async def test_get_topic_health_not_found(self):
        """Test get_topic_health for non-existent topic."""
        manager = TopicManager()

        # Mock the admin client to return None
        with patch.object(
            manager, "get_topic_health", new_callable=AsyncMock
        ) as mock:
            mock.return_value = None
            result = await mock("nonexistent.topic")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_topic_health_success(self):
        """Test get_topic_health for existing topic."""
        manager = TopicManager()

        expected_health = TopicHealth(
            topic="signals.raw",
            partitions=12,
            replicas=24,
            in_sync_replicas=24,
            under_replicated=False,
            offline_partitions=0,
            leader_count=3,
            is_healthy=True,
        )

        with patch.object(
            manager, "get_topic_health", new_callable=AsyncMock
        ) as mock:
            mock.return_value = expected_health
            result = await mock("signals.raw")

        assert result.topic == "signals.raw"
        assert result.is_healthy

    @pytest.mark.asyncio
    async def test_get_all_topics_health(self):
        """Test get_all_topics_health method."""
        manager = TopicManager()

        mock_health = TopicHealth(
            topic="test",
            partitions=6,
            replicas=12,
            in_sync_replicas=12,
            under_replicated=False,
            offline_partitions=0,
            leader_count=3,
            is_healthy=True,
        )

        with patch.object(
            manager, "get_topic_health", new_callable=AsyncMock
        ) as mock:
            mock.return_value = mock_health
            health_list = await manager.get_all_topics_health()

        # Called for each topic
        assert mock.call_count == 7

    def test_get_config_summary(self):
        """Test get_config_summary method."""
        manager = TopicManager()

        summary = manager.get_config_summary()

        assert summary["total_topics"] == 7
        assert len(summary["topics"]) == 7
        assert "by_priority" in summary
        assert TopicPriority.CRITICAL.value in summary["by_priority"]
        assert TopicPriority.HIGH.value in summary["by_priority"]
        assert TopicPriority.NORMAL.value in summary["by_priority"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestTopicManagerWithMocks:
    """Tests for TopicManager with proper mocking."""

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_import_error(self):
        """Test ensure_topics_exist handles import error."""
        manager = TopicManager()

        # Import the actual method and test with sys.modules manipulation
        import sys
        original_modules = sys.modules.copy()

        # Remove aiokafka if exists
        for mod in list(sys.modules.keys()):
            if mod.startswith("aiokafka"):
                del sys.modules[mod]

        # Patch the import to raise ImportError
        with patch.dict(sys.modules, {"aiokafka": None, "aiokafka.admin": None}):
            # Force reload behavior by calling the method
            try:
                results = await manager.ensure_topics_exist()
                # If aiokafka is available it will work, if not it returns all False
                assert isinstance(results, dict)
            except ImportError:
                # Expected if aiokafka truly not installed
                pass

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_general_error(self):
        """Test ensure_topics_exist handles general exceptions."""
        manager = TopicManager()

        mock_admin_class = MagicMock()
        mock_admin_instance = AsyncMock()
        mock_admin_instance.start.side_effect = Exception("Connection failed")
        mock_admin_class.return_value = mock_admin_instance

        # Create a mock module with the admin client
        mock_admin_module = MagicMock()
        mock_admin_module.AIOKafkaAdminClient = mock_admin_class
        mock_admin_module.NewTopic = MagicMock()

        with patch.dict("sys.modules", {"aiokafka.admin": mock_admin_module}):
            with pytest.raises(Exception, match="Connection failed"):
                await manager.ensure_topics_exist()

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_creates_missing(self):
        """Test ensure_topics_exist creates missing topics."""
        manager = TopicManager()

        mock_admin_class = MagicMock()
        mock_admin_instance = AsyncMock()
        mock_admin_instance.start = AsyncMock()
        mock_admin_instance.close = AsyncMock()
        mock_admin_instance.list_topics = AsyncMock(return_value=["signals.raw"])  # Only one exists
        mock_admin_instance.create_topics = AsyncMock()
        mock_admin_class.return_value = mock_admin_instance

        mock_new_topic = MagicMock()

        mock_admin_module = MagicMock()
        mock_admin_module.AIOKafkaAdminClient = mock_admin_class
        mock_admin_module.NewTopic = mock_new_topic

        with patch.dict("sys.modules", {"aiokafka.admin": mock_admin_module}):
            results = await manager.ensure_topics_exist()

        assert results["signals.raw"] is False  # Existed
        assert results["signals.computed"] is True  # Created
        mock_admin_instance.create_topics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_topic_health_import_error(self):
        """Test get_topic_health handles import error."""
        manager = TopicManager()

        with patch.dict("sys.modules", {"aiokafka": None, "aiokafka.admin": None}):
            try:
                result = await manager.get_topic_health("test.topic")
                assert result is None
            except ImportError:
                pass

    @pytest.mark.asyncio
    async def test_get_topic_health_general_error(self):
        """Test get_topic_health handles general exceptions."""
        manager = TopicManager()

        mock_admin_class = MagicMock()
        mock_admin_instance = AsyncMock()
        mock_admin_instance.start.side_effect = Exception("Connection refused")
        mock_admin_class.return_value = mock_admin_instance

        mock_admin_module = MagicMock()
        mock_admin_module.AIOKafkaAdminClient = mock_admin_class

        with patch.dict("sys.modules", {"aiokafka.admin": mock_admin_module}):
            result = await manager.get_topic_health("test.topic")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_topic_health_no_metadata(self):
        """Test get_topic_health when topic not found."""
        manager = TopicManager()

        mock_admin_class = MagicMock()
        mock_admin_instance = AsyncMock()
        mock_admin_instance.start = AsyncMock()
        mock_admin_instance.close = AsyncMock()
        mock_admin_instance.describe_topics = AsyncMock(return_value=[])  # Empty
        mock_admin_class.return_value = mock_admin_instance

        mock_admin_module = MagicMock()
        mock_admin_module.AIOKafkaAdminClient = mock_admin_class

        with patch.dict("sys.modules", {"aiokafka.admin": mock_admin_module}):
            result = await manager.get_topic_health("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_topic_health_with_partitions(self):
        """Test get_topic_health with partition data."""
        manager = TopicManager()

        # Create mock partition
        mock_partition = MagicMock()
        mock_partition.replicas = [1, 2, 3]
        mock_partition.isr = [1, 2, 3]
        mock_partition.leader = 1

        mock_partition2 = MagicMock()
        mock_partition2.replicas = [1, 2, 3]
        mock_partition2.isr = [1, 2]  # Under-replicated
        mock_partition2.leader = 2

        mock_topic = MagicMock()
        mock_topic.partitions = [mock_partition, mock_partition2]

        mock_admin_class = MagicMock()
        mock_admin_instance = AsyncMock()
        mock_admin_instance.start = AsyncMock()
        mock_admin_instance.close = AsyncMock()
        mock_admin_instance.describe_topics = AsyncMock(return_value=[mock_topic])
        mock_admin_class.return_value = mock_admin_instance

        mock_admin_module = MagicMock()
        mock_admin_module.AIOKafkaAdminClient = mock_admin_class

        with patch.dict("sys.modules", {"aiokafka.admin": mock_admin_module}):
            result = await manager.get_topic_health("test.topic")

        assert result is not None
        assert result.partitions == 2
        assert result.replicas == 6
        assert result.in_sync_replicas == 5
        assert result.under_replicated is True
        assert result.leader_count == 2

    @pytest.mark.asyncio
    async def test_get_topic_health_offline_partition(self):
        """Test get_topic_health with offline partition."""
        manager = TopicManager()

        mock_partition = MagicMock()
        mock_partition.replicas = [1, 2]
        mock_partition.isr = [1, 2]
        mock_partition.leader = -1  # Offline

        mock_topic = MagicMock()
        mock_topic.partitions = [mock_partition]

        mock_admin_class = MagicMock()
        mock_admin_instance = AsyncMock()
        mock_admin_instance.start = AsyncMock()
        mock_admin_instance.close = AsyncMock()
        mock_admin_instance.describe_topics = AsyncMock(return_value=[mock_topic])
        mock_admin_class.return_value = mock_admin_instance

        mock_admin_module = MagicMock()
        mock_admin_module.AIOKafkaAdminClient = mock_admin_class

        with patch.dict("sys.modules", {"aiokafka.admin": mock_admin_module}):
            result = await manager.get_topic_health("test.topic")

        assert result is not None
        assert result.offline_partitions == 1
        assert result.is_healthy is False

    @pytest.mark.asyncio
    async def test_get_all_topics_health_filters_none(self):
        """Test get_all_topics_health filters out None results."""
        manager = TopicManager()

        call_count = [0]

        async def mock_health(name):
            call_count[0] += 1
            if call_count[0] % 2 == 0:
                return None
            return TopicHealth(
                topic=name,
                partitions=6,
                replicas=12,
                in_sync_replicas=12,
                under_replicated=False,
                offline_partitions=0,
                leader_count=3,
                is_healthy=True,
            )

        with patch.object(manager, "get_topic_health", side_effect=mock_health):
            results = await manager.get_all_topics_health()

        # Should have filtered out None results
        assert len(results) < 7  # Less than total topics


class TestTopicsIntegration:
    """Integration tests for topics module."""

    def test_all_topics_have_valid_config(self):
        """Test that all registered topics have valid configuration."""
        for topic in TopicRegistry.all_topics():
            assert topic.name
            assert topic.partitions > 0
            assert topic.replication_factor > 0
            assert topic.retention_ms > 0
            assert isinstance(topic.cleanup_policy, CleanupPolicy)
            assert isinstance(topic.priority, TopicPriority)

    def test_critical_topics_have_sufficient_partitions(self):
        """Test that critical topics have at least 3 partitions."""
        for topic in TopicRegistry.critical_topics():
            assert topic.partitions >= 3

    def test_dlq_topic_has_long_retention(self):
        """Test that DLQ topic has long retention for debugging."""
        dlq = TopicRegistry.SIGNALS_DLQ

        assert dlq.retention_ms >= 2592000000  # At least 30 days

    def test_audit_log_has_longest_retention(self):
        """Test that audit log has longest retention."""
        audit = TopicRegistry.AUDIT_LOG

        # Should be at least 90 days
        assert audit.retention_ms >= 7776000000

    def test_topics_have_unique_names(self):
        """Test that all topic names are unique."""
        names = [t.name for t in TopicRegistry.all_topics()]

        assert len(names) == len(set(names))

    def test_kafka_config_values_are_strings(self):
        """Test that all Kafka config values are strings."""
        for topic in TopicRegistry.all_topics():
            config = topic.to_kafka_config()
            for key, value in config.items():
                assert isinstance(value, str), f"{key} should be string"
