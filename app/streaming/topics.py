"""
S39 - Topics Configuration Module

Centralized Kafka topic configuration with retention, partitions, and replication settings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TopicPriority(str, Enum):
    """Topic priority levels for resource allocation."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CleanupPolicy(str, Enum):
    """Kafka topic cleanup policies."""
    DELETE = "delete"
    COMPACT = "compact"
    COMPACT_DELETE = "compact,delete"


@dataclass
class TopicConfig:
    """
    Configuration for a Kafka topic.

    Attributes:
        name: Topic name
        partitions: Number of partitions (default 6)
        replication_factor: Replication factor (default 2)
        retention_ms: Message retention in milliseconds (default 7 days)
        retention_bytes: Max bytes per partition (-1 = unlimited)
        cleanup_policy: How to clean up old messages
        min_insync_replicas: Minimum ISR for acks=all
        segment_bytes: Segment file size
        priority: Topic priority for monitoring
        description: Human-readable description
    """
    name: str
    partitions: int = 6
    replication_factor: int = 2
    retention_ms: int = 604800000  # 7 days
    retention_bytes: int = -1  # Unlimited
    cleanup_policy: CleanupPolicy = CleanupPolicy.DELETE
    min_insync_replicas: int = 1
    segment_bytes: int = 1073741824  # 1GB
    priority: TopicPriority = TopicPriority.NORMAL
    description: str = ""
    extra_configs: Dict[str, str] = field(default_factory=dict)

    def to_kafka_config(self) -> Dict[str, str]:
        """Convert to Kafka admin config format."""
        config = {
            "retention.ms": str(self.retention_ms),
            "retention.bytes": str(self.retention_bytes),
            "cleanup.policy": self.cleanup_policy.value,
            "min.insync.replicas": str(self.min_insync_replicas),
            "segment.bytes": str(self.segment_bytes),
        }
        config.update(self.extra_configs)
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "partitions": self.partitions,
            "replication_factor": self.replication_factor,
            "retention_ms": self.retention_ms,
            "retention_bytes": self.retention_bytes,
            "cleanup_policy": self.cleanup_policy.value,
            "min_insync_replicas": self.min_insync_replicas,
            "segment_bytes": self.segment_bytes,
            "priority": self.priority.value,
            "description": self.description,
        }


class TopicRegistry:
    """
    Registry of all Kafka topics used by the application.

    Provides centralized topic configuration and management.
    """

    # Core signal topics
    SIGNALS_RAW = TopicConfig(
        name="signals.raw",
        partitions=12,
        replication_factor=2,
        retention_ms=604800000,  # 7 days
        priority=TopicPriority.HIGH,
        description="Raw signals from claim processing",
        extra_configs={
            "max.message.bytes": "1048576",  # 1MB
        },
    )

    SIGNALS_COMPUTED = TopicConfig(
        name="signals.computed",
        partitions=12,
        replication_factor=2,
        retention_ms=2592000000,  # 30 days
        priority=TopicPriority.HIGH,
        description="Computed/derived signals after processing",
    )

    SIGNALS_DLQ = TopicConfig(
        name="signals.dlq",
        partitions=3,
        replication_factor=2,
        retention_ms=2592000000,  # 30 days
        priority=TopicPriority.CRITICAL,
        description="Dead letter queue for failed signal processing",
        extra_configs={
            "max.message.bytes": "5242880",  # 5MB for error context
        },
    )

    # Event topics
    CLAIMS_EVENTS = TopicConfig(
        name="claims.events",
        partitions=6,
        replication_factor=2,
        retention_ms=604800000,  # 7 days
        priority=TopicPriority.NORMAL,
        description="Claim lifecycle events",
    )

    EVIDENCE_EVENTS = TopicConfig(
        name="evidence.events",
        partitions=6,
        replication_factor=2,
        retention_ms=604800000,  # 7 days
        priority=TopicPriority.NORMAL,
        description="Evidence addition and update events",
    )

    # Alert topics
    ALERTS_STREAM = TopicConfig(
        name="alerts.stream",
        partitions=3,
        replication_factor=2,
        retention_ms=86400000,  # 1 day
        priority=TopicPriority.CRITICAL,
        description="Real-time alert notifications",
    )

    # Audit topics
    AUDIT_LOG = TopicConfig(
        name="audit.log",
        partitions=6,
        replication_factor=2,
        retention_ms=7776000000,  # 90 days
        cleanup_policy=CleanupPolicy.DELETE,
        priority=TopicPriority.HIGH,
        description="Audit trail for all operations",
    )

    @classmethod
    def all_topics(cls) -> List[TopicConfig]:
        """Get all registered topics."""
        return [
            cls.SIGNALS_RAW,
            cls.SIGNALS_COMPUTED,
            cls.SIGNALS_DLQ,
            cls.CLAIMS_EVENTS,
            cls.EVIDENCE_EVENTS,
            cls.ALERTS_STREAM,
            cls.AUDIT_LOG,
        ]

    @classmethod
    def get_by_name(cls, name: str) -> Optional[TopicConfig]:
        """Get topic config by name."""
        for topic in cls.all_topics():
            if topic.name == name:
                return topic
        return None

    @classmethod
    def get_by_priority(cls, priority: TopicPriority) -> List[TopicConfig]:
        """Get topics by priority level."""
        return [t for t in cls.all_topics() if t.priority == priority]

    @classmethod
    def critical_topics(cls) -> List[TopicConfig]:
        """Get critical priority topics."""
        return cls.get_by_priority(TopicPriority.CRITICAL)

    @classmethod
    def to_create_spec(cls) -> List[Dict[str, Any]]:
        """
        Generate topic creation specifications.

        Useful for kafka-topics.sh or admin client.
        """
        specs = []
        for topic in cls.all_topics():
            specs.append({
                "topic": topic.name,
                "partitions": topic.partitions,
                "replication_factor": topic.replication_factor,
                "config": topic.to_kafka_config(),
            })
        return specs


@dataclass
class TopicHealth:
    """Health status of a Kafka topic."""
    topic: str
    partitions: int
    replicas: int
    in_sync_replicas: int
    under_replicated: bool
    offline_partitions: int
    leader_count: int
    is_healthy: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "partitions": self.partitions,
            "replicas": self.replicas,
            "in_sync_replicas": self.in_sync_replicas,
            "under_replicated": self.under_replicated,
            "offline_partitions": self.offline_partitions,
            "leader_count": self.leader_count,
            "is_healthy": self.is_healthy,
        }


class TopicManager:
    """
    Manager for Kafka topic operations.

    Handles topic creation, configuration updates, and health checks.
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize TopicManager.

        Args:
            bootstrap_servers: Kafka bootstrap servers
        """
        self.bootstrap_servers = bootstrap_servers
        self._admin_client = None

    async def ensure_topics_exist(self) -> Dict[str, bool]:
        """
        Ensure all registered topics exist.

        Returns:
            Dict mapping topic name to creation status (True = created, False = exists)
        """
        results = {}

        try:
            from aiokafka.admin import AIOKafkaAdminClient, NewTopic

            admin = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
            await admin.start()

            try:
                existing = await admin.list_topics()

                topics_to_create = []
                for topic_config in TopicRegistry.all_topics():
                    if topic_config.name not in existing:
                        new_topic = NewTopic(
                            name=topic_config.name,
                            num_partitions=topic_config.partitions,
                            replication_factor=topic_config.replication_factor,
                            topic_configs=topic_config.to_kafka_config(),
                        )
                        topics_to_create.append(new_topic)
                        results[topic_config.name] = True
                    else:
                        results[topic_config.name] = False

                if topics_to_create:
                    await admin.create_topics(topics_to_create)
                    logger.info(f"Created {len(topics_to_create)} topics")

            finally:
                await admin.close()

        except ImportError:
            logger.warning("aiokafka not installed, skipping topic creation")
            for topic_config in TopicRegistry.all_topics():
                results[topic_config.name] = False
        except Exception as e:
            logger.error(f"Failed to ensure topics: {e}")
            raise

        return results

    async def get_topic_health(self, topic_name: str) -> Optional[TopicHealth]:
        """
        Get health status of a topic.

        Args:
            topic_name: Topic to check

        Returns:
            TopicHealth or None if not found
        """
        try:
            from aiokafka.admin import AIOKafkaAdminClient

            admin = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
            await admin.start()

            try:
                metadata = await admin.describe_topics([topic_name])

                if not metadata:
                    return None

                topic_meta = metadata[0]
                partitions = len(topic_meta.partitions)

                total_replicas = 0
                total_isr = 0
                offline = 0
                leaders = set()

                for partition in topic_meta.partitions:
                    total_replicas += len(partition.replicas)
                    total_isr += len(partition.isr)
                    if partition.leader < 0:
                        offline += 1
                    else:
                        leaders.add(partition.leader)

                under_replicated = total_isr < total_replicas
                is_healthy = offline == 0 and not under_replicated

                return TopicHealth(
                    topic=topic_name,
                    partitions=partitions,
                    replicas=total_replicas,
                    in_sync_replicas=total_isr,
                    under_replicated=under_replicated,
                    offline_partitions=offline,
                    leader_count=len(leaders),
                    is_healthy=is_healthy,
                )

            finally:
                await admin.close()

        except ImportError:
            logger.warning("aiokafka not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to get topic health: {e}")
            return None

    async def get_all_topics_health(self) -> List[TopicHealth]:
        """Get health status of all registered topics."""
        health_list = []
        for topic_config in TopicRegistry.all_topics():
            health = await self.get_topic_health(topic_config.name)
            if health:
                health_list.append(health)
        return health_list

    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of all topic configurations."""
        return {
            "total_topics": len(TopicRegistry.all_topics()),
            "topics": [t.to_dict() for t in TopicRegistry.all_topics()],
            "by_priority": {
                p.value: len(TopicRegistry.get_by_priority(p))
                for p in TopicPriority
            },
        }
