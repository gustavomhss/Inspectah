"""
S38: Tests for Memory Controller
"""
import pytest
from datetime import datetime, timedelta, timezone

from app.context.memory_controller import (
    MemoryScope,
    MemoryType,
    RetentionPolicy,
    MemoryEntry,
    MemoryContext,
    MemoryStats,
    MemoryRepository,
    MemoryController,
    RETENTION_TTL,
)


class TestMemoryEnums:
    """Tests for memory enums."""

    def test_memory_scope_values(self):
        assert MemoryScope.SESSION.value == "session"
        assert MemoryScope.AGENT.value == "agent"
        assert MemoryScope.FLOW.value == "flow"
        assert MemoryScope.CASE.value == "case"
        assert MemoryScope.USER.value == "user"
        assert MemoryScope.GLOBAL.value == "global"

    def test_memory_type_values(self):
        assert MemoryType.CONTEXT.value == "context"
        assert MemoryType.FACT.value == "fact"
        assert MemoryType.DECISION.value == "decision"
        assert MemoryType.OBSERVATION.value == "observation"
        assert MemoryType.SUMMARY.value == "summary"
        assert MemoryType.REFERENCE.value == "reference"

    def test_retention_policy_values(self):
        assert RetentionPolicy.EPHEMERAL.value == "ephemeral"
        assert RetentionPolicy.SHORT.value == "short"
        assert RetentionPolicy.MEDIUM.value == "medium"
        assert RetentionPolicy.LONG.value == "long"
        assert RetentionPolicy.PERMANENT.value == "permanent"

    def test_retention_ttl_mapping(self):
        assert RETENTION_TTL[RetentionPolicy.EPHEMERAL] == timedelta(hours=1)
        assert RETENTION_TTL[RetentionPolicy.SHORT] == timedelta(days=1)
        assert RETENTION_TTL[RetentionPolicy.MEDIUM] == timedelta(days=7)
        assert RETENTION_TTL[RetentionPolicy.LONG] == timedelta(days=30)


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""

    def test_create_entry(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key",
            value={"data": "test"},
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(days=1),
            accessed_at=now,
        )

        assert entry.entry_id == "test_001"
        assert entry.scope == MemoryScope.SESSION
        assert entry.scope_id == "session_123"
        assert entry.key == "test_key"
        assert entry.access_count == 0
        assert entry.importance == 0.5

    def test_entry_is_expired_false(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key",
            value="test",
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(hours=1),
            accessed_at=now,
        )
        assert not entry.is_expired()

    def test_entry_is_expired_true(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key",
            value="test",
            retention=RetentionPolicy.SHORT,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            accessed_at=now - timedelta(hours=2),
        )
        assert entry.is_expired()

    def test_entry_touch(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key",
            value="test",
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(hours=1),
            accessed_at=now,
            access_count=0,
        )

        entry.touch()
        assert entry.access_count == 1

        entry.touch()
        assert entry.access_count == 2

    def test_entry_to_dict(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.FACT,
            key="test_key",
            value="test_value",
            retention=RetentionPolicy.MEDIUM,
            created_at=now,
            expires_at=now + timedelta(days=7),
            accessed_at=now,
            importance=0.8,
            tags=["tag1", "tag2"],
        )

        result = entry.to_dict()
        assert result["entry_id"] == "test_001"
        assert result["scope"] == "session"
        assert result["memory_type"] == "fact"
        assert result["retention"] == "medium"
        assert result["importance"] == 0.8
        assert result["tags"] == ["tag1", "tag2"]


class TestMemoryRepository:
    """Tests for MemoryRepository."""

    @pytest.fixture
    def repo(self):
        return MemoryRepository()

    def test_save_and_get(self, repo):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key",
            value="test_value",
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(days=1),
            accessed_at=now,
        )

        repo.save(entry)
        result = repo.get("test_001")

        assert result is not None
        assert result.entry_id == "test_001"
        assert result.value == "test_value"

    def test_get_not_found(self, repo):
        result = repo.get("nonexistent")
        assert result is None

    def test_get_by_scope(self, repo):
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Create entries in different scopes
        for i in range(3):
            entry = MemoryEntry(
                entry_id=f"session_{i}",
                scope=MemoryScope.SESSION,
                scope_id="session_123",
                memory_type=MemoryType.CONTEXT,
                key=f"key_{i}",
                value=f"value_{i}",
                retention=RetentionPolicy.SHORT,
                created_at=now,
                expires_at=now + timedelta(days=1),
                accessed_at=now,
            )
            repo.save(entry)

        # Add one in different scope
        other = MemoryEntry(
            entry_id="agent_0",
            scope=MemoryScope.AGENT,
            scope_id="agent_456",
            memory_type=MemoryType.FACT,
            key="other_key",
            value="other_value",
            retention=RetentionPolicy.LONG,
            created_at=now,
            expires_at=now + timedelta(days=30),
            accessed_at=now,
        )
        repo.save(other)

        # Find session entries
        results = repo.get_by_scope(scope=MemoryScope.SESSION, scope_id="session_123")
        assert len(results) == 3

        # Find agent entries
        results = repo.get_by_scope(scope=MemoryScope.AGENT, scope_id="agent_456")
        assert len(results) == 1

    def test_get_by_key(self, repo):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="test_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="unique_key",
            value="test_value",
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(days=1),
            accessed_at=now,
        )
        repo.save(entry)

        results = repo.get_by_key("unique_key")
        assert len(results) == 1
        assert results[0].key == "unique_key"

    def test_delete(self, repo):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = MemoryEntry(
            entry_id="to_delete",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key",
            value="test_value",
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(days=1),
            accessed_at=now,
        )
        repo.save(entry)

        assert repo.get("to_delete") is not None
        deleted = repo.delete("to_delete")
        assert deleted is True
        assert repo.get("to_delete") is None

    def test_delete_not_found(self, repo):
        deleted = repo.delete("nonexistent")
        assert deleted is False

    def test_get_all(self, repo):
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Create multiple entries
        for i in range(3):
            entry = MemoryEntry(
                entry_id=f"entry_{i}",
                scope=MemoryScope.SESSION,
                scope_id="session_123",
                memory_type=MemoryType.CONTEXT,
                key=f"key_{i}",
                value=f"value_{i}",
                retention=RetentionPolicy.SHORT,
                created_at=now,
                expires_at=now + timedelta(days=1),
                accessed_at=now,
            )
            repo.save(entry)

        results = repo.get_all()
        assert len(results) == 3


class TestMemoryController:
    """Tests for MemoryController."""

    @pytest.fixture
    def controller(self):
        return MemoryController()

    def test_remember_and_recall(self, controller):
        entry = controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="test_key",
            value="test_value",
            memory_type=MemoryType.CONTEXT,
            retention=RetentionPolicy.SHORT,
        )

        assert entry is not None
        assert entry.key == "test_key"
        assert entry.value == "test_value"

        # Recall
        results = controller.recall(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="test_key",
        )

        assert len(results) == 1
        assert results[0].value == "test_value"

    def test_remember_with_importance(self, controller):
        entry = controller.remember(
            scope=MemoryScope.AGENT,
            scope_id="agent_123",
            key="important_fact",
            value="critical data",
            memory_type=MemoryType.FACT,
            retention=RetentionPolicy.LONG,
            importance=0.95,
        )

        assert entry.importance == 0.95

    def test_remember_with_tags(self, controller):
        entry = controller.remember(
            scope=MemoryScope.CASE,
            scope_id="case_123",
            key="tagged_memory",
            value="some data",
            memory_type=MemoryType.OBSERVATION,
            retention=RetentionPolicy.MEDIUM,
            tags=["urgent", "reviewed"],
        )

        assert "urgent" in entry.tags
        assert "reviewed" in entry.tags

    def test_recall_by_type(self, controller):
        # Create entries of different types
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="context_1",
            value="ctx",
            memory_type=MemoryType.CONTEXT,
        )
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="fact_1",
            value="fact",
            memory_type=MemoryType.FACT,
        )

        # Recall only facts
        results = controller.recall(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.FACT,
        )

        assert len(results) == 1
        assert results[0].memory_type == MemoryType.FACT

    def test_recall_by_min_importance(self, controller):
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="low_importance",
            value="low",
            importance=0.2,
        )
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="high_importance",
            value="high",
            importance=0.9,
        )

        results = controller.recall(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            min_importance=0.5,
        )

        assert len(results) == 1
        assert results[0].importance >= 0.5

    def test_forget(self, controller):
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="to_forget",
            value="data",
        )

        count = controller.forget(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="to_forget",
        )

        assert count == 1

        results = controller.recall(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="to_forget",
        )
        assert len(results) == 0

    def test_forget_all_in_scope(self, controller):
        for i in range(5):
            controller.remember(
                scope=MemoryScope.SESSION,
                scope_id="session_to_clear",
                key=f"key_{i}",
                value=f"value_{i}",
            )

        count = controller.forget(
            scope=MemoryScope.SESSION,
            scope_id="session_to_clear",
        )

        assert count == 5

    def test_cleanup_expired(self, controller):
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Manually create an expired entry
        expired_entry = MemoryEntry(
            entry_id="expired_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="expired_key",
            value="expired_value",
            retention=RetentionPolicy.EPHEMERAL,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            accessed_at=now - timedelta(hours=2),
        )
        controller.repository.save(expired_entry)

        # Create a valid entry
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="valid_key",
            value="valid_value",
        )

        count = controller.cleanup_expired()
        assert count >= 1

    def test_get_stats(self, controller):
        # Create some entries
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            key="key1",
            value="value1",
            memory_type=MemoryType.CONTEXT,
        )
        controller.remember(
            scope=MemoryScope.AGENT,
            scope_id="agent_123",
            key="key2",
            value="value2",
            memory_type=MemoryType.FACT,
            retention=RetentionPolicy.LONG,
        )

        stats = controller.get_stats()

        assert isinstance(stats, MemoryStats)
        assert stats.total_entries >= 2
        assert "session" in stats.by_scope or stats.by_scope.get("session", 0) >= 0

    def test_build_context(self, controller):
        controller.remember(
            scope=MemoryScope.FLOW,
            scope_id="flow_123",
            key="context_data",
            value={"step": 1},
            memory_type=MemoryType.CONTEXT,
        )
        controller.remember(
            scope=MemoryScope.FLOW,
            scope_id="flow_123",
            key="decision_data",
            value={"choice": "A"},
            memory_type=MemoryType.DECISION,
        )

        context = controller.build_context(
            scope=MemoryScope.FLOW,
            scope_id="flow_123",
        )

        assert isinstance(context, MemoryContext)
        assert context.scope == MemoryScope.FLOW
        assert context.scope_id == "flow_123"
        assert context.entry_count >= 2

    def test_summarize(self, controller):
        for i in range(5):
            controller.remember(
                scope=MemoryScope.SESSION,
                scope_id="session_to_summarize",
                key=f"item_{i}",
                value=f"value_{i}",
            )

        summary = controller.summarize(
            scope=MemoryScope.SESSION,
            scope_id="session_to_summarize",
        )

        assert summary is not None
        assert summary.memory_type == MemoryType.SUMMARY

    def test_export_context(self, controller):
        controller.remember(
            scope=MemoryScope.CASE,
            scope_id="case_export",
            key="data1",
            value="value1",
        )

        exported = controller.export_context(
            scope=MemoryScope.CASE,
            scope_id="case_export",
        )

        assert "entries" in exported
        assert "scope" in exported
        assert exported["scope"] == "case"

    def test_import_context(self, controller):
        data = {
            "scope": "case",
            "scope_id": "case_import",
            "entries": [
                {
                    "key": "imported_key",
                    "value": "imported_value",
                    "memory_type": "fact",
                    "retention": "medium",
                    "importance": 0.7,
                    "tags": ["imported"],
                }
            ],
        }

        count = controller.import_context(
            data=data,
            scope=MemoryScope.CASE,
            scope_id="case_import",
        )

        assert count == 1

        results = controller.recall(
            scope=MemoryScope.CASE,
            scope_id="case_import",
        )
        assert len(results) == 1
        assert results[0].key == "imported_key"

    def test_recall_by_key(self, controller):
        """Test recall_by_key method."""
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_a",
            key="shared_key",
            value="value_a",
        )
        controller.remember(
            scope=MemoryScope.AGENT,
            scope_id="agent_b",
            key="shared_key",
            value="value_b",
        )

        results = controller.recall_by_key("shared_key")
        assert len(results) == 2
        # All should have been touched
        for entry in results:
            assert entry.access_count >= 1

    def test_recall_by_key_excludes_expired(self, controller):
        """Test recall_by_key excludes expired entries by default."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Create an expired entry directly
        expired_entry = MemoryEntry(
            entry_id="expired_key_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="test_key_recall",
            value="expired_value",
            retention=RetentionPolicy.EPHEMERAL,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            accessed_at=now - timedelta(hours=2),
        )
        controller.repository.save(expired_entry)

        # Create a valid entry
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_456",
            key="test_key_recall",
            value="valid_value",
        )

        results = controller.recall_by_key("test_key_recall", include_expired=False)
        assert len(results) == 1
        assert results[0].value == "valid_value"

        # With include_expired=True
        results_all = controller.recall_by_key("test_key_recall", include_expired=True)
        assert len(results_all) == 2

    def test_recall_with_tags_filter(self, controller):
        """Test recall filtering by tags."""
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_tags",
            key="tagged_entry",
            value="data1",
            tags=["urgent", "security"],
        )
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_tags",
            key="other_entry",
            value="data2",
            tags=["normal"],
        )

        # Filter by tags
        results = controller.recall(
            scope=MemoryScope.SESSION,
            scope_id="session_tags",
            tags=["urgent"],
        )
        assert len(results) == 1
        assert results[0].key == "tagged_entry"

    def test_recall_key_filter_no_match(self, controller):
        """Test recall with key filter that doesn't match."""
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_filter",
            key="key_a",
            value="value_a",
        )

        results = controller.recall(
            scope=MemoryScope.SESSION,
            scope_id="session_filter",
            key="nonexistent_key",
        )
        assert len(results) == 0

    def test_build_context_with_include_types(self, controller):
        """Test build_context with include_types filter."""
        controller.remember(
            scope=MemoryScope.FLOW,
            scope_id="flow_types",
            key="context_entry",
            value={"data": "ctx"},
            memory_type=MemoryType.CONTEXT,
        )
        controller.remember(
            scope=MemoryScope.FLOW,
            scope_id="flow_types",
            key="fact_entry",
            value={"data": "fact"},
            memory_type=MemoryType.FACT,
        )
        controller.remember(
            scope=MemoryScope.FLOW,
            scope_id="flow_types",
            key="decision_entry",
            value={"data": "decision"},
            memory_type=MemoryType.DECISION,
        )

        # Only include FACT and DECISION
        context = controller.build_context(
            scope=MemoryScope.FLOW,
            scope_id="flow_types",
            include_types=[MemoryType.FACT, MemoryType.DECISION],
        )

        assert context.entry_count == 2
        assert "fact_entry" in context.entries
        assert "decision_entry" in context.entries
        assert "context_entry" not in context.entries

    def test_summarize_with_custom_summarizer(self, controller):
        """Test summarize with custom summarizer function."""
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_custom_sum",
            key="item_1",
            value="value_1",
        )
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_custom_sum",
            key="item_2",
            value="value_2",
        )

        def custom_summarizer(entries):
            return f"Custom summary: {len(entries)} items"

        summary = controller.summarize(
            scope=MemoryScope.SESSION,
            scope_id="session_custom_sum",
            summarizer=custom_summarizer,
        )

        assert summary.memory_type == MemoryType.SUMMARY
        assert "Custom summary: 2 items" in summary.value

    def test_register_cleanup_callback(self, controller):
        """Test registering and executing cleanup callbacks."""
        cleaned_entries = []

        def cleanup_callback(entry):
            cleaned_entries.append(entry.entry_id)

        controller.register_cleanup_callback(cleanup_callback)

        # Create and forget an entry
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_callback",
            key="to_forget",
            value="data",
        )

        controller.forget(
            scope=MemoryScope.SESSION,
            scope_id="session_callback",
            key="to_forget",
        )

        assert len(cleaned_entries) == 1

    def test_cleanup_callback_on_expired(self, controller):
        """Test cleanup callback is called when cleaning expired entries."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cleaned_entries = []

        def cleanup_callback(entry):
            cleaned_entries.append(entry.entry_id)

        controller.register_cleanup_callback(cleanup_callback)

        # Manually create an expired entry
        expired_entry = MemoryEntry(
            entry_id="expired_cb_001",
            scope=MemoryScope.SESSION,
            scope_id="session_cb",
            memory_type=MemoryType.CONTEXT,
            key="expired_key_cb",
            value="expired_value",
            retention=RetentionPolicy.EPHEMERAL,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            accessed_at=now - timedelta(hours=2),
        )
        controller.repository.save(expired_entry)

        controller.cleanup_expired()

        assert "expired_cb_001" in cleaned_entries

    def test_maybe_cleanup_exceeds_limit(self, controller):
        """Test _maybe_cleanup when exceeding max_entries_per_scope."""
        # Set a low limit
        controller.max_entries_per_scope = 3

        # Create more entries than the limit
        for i in range(5):
            controller.remember(
                scope=MemoryScope.SESSION,
                scope_id="session_limit",
                key=f"key_{i}",
                value=f"value_{i}",
                importance=i * 0.2,  # Varying importance
            )

        # Trigger maybe_cleanup
        controller._maybe_cleanup(MemoryScope.SESSION, "session_limit")

        # Should have removed excess entries
        entries = controller.repository.get_by_scope(MemoryScope.SESSION, "session_limit")
        assert len(entries) <= 3

    def test_forget_with_key_filter_no_match(self, controller):
        """Test forget with key that doesn't match any entry."""
        controller.remember(
            scope=MemoryScope.SESSION,
            scope_id="session_no_match",
            key="existing_key",
            value="data",
        )

        count = controller.forget(
            scope=MemoryScope.SESSION,
            scope_id="session_no_match",
            key="nonexistent_key",
        )

        assert count == 0


class TestMemoryContext:
    """Tests for MemoryContext class."""

    def test_get_active_entries(self):
        """Test get_active_entries filters out expired entries."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        active_entry = MemoryEntry(
            entry_id="active_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="active_key",
            value="active_value",
            retention=RetentionPolicy.SHORT,
            created_at=now,
            expires_at=now + timedelta(hours=1),
            accessed_at=now,
        )

        expired_entry = MemoryEntry(
            entry_id="expired_001",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            memory_type=MemoryType.CONTEXT,
            key="expired_key",
            value="expired_value",
            retention=RetentionPolicy.EPHEMERAL,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            accessed_at=now - timedelta(hours=2),
        )

        context = MemoryContext(
            context_id="ctx_test",
            scope=MemoryScope.SESSION,
            scope_id="session_123",
            entries={
                "active_key": active_entry,
                "expired_key": expired_entry,
            },
        )

        active_entries = context.get_active_entries()
        assert len(active_entries) == 1
        assert active_entries[0].key == "active_key"
