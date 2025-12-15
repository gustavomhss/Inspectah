"""
Tests for Signal Repository — S37

Tests for SignalRepository persistence layer.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from app.signals.signal_repository import SignalRepository


class TestSignalRepository:
    """Tests for SignalRepository class."""

    @pytest.fixture
    def repo(self):
        """Create in-memory repository for testing."""
        return SignalRepository(db_path=":memory:")

    def test_init_memory_db(self):
        """Initialize in-memory database."""
        repo = SignalRepository(db_path=":memory:")
        assert repo._is_memory is True

    def test_save_snapshot(self, repo):
        """Save a signal snapshot."""
        snapshot = {
            "signal_type": "mentiras_em_circulacao",
            "domain": "pilot_politics",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "values": {"total_claims": 100, "false_claims": 25},
            "metadata": {"version": "v1"},
        }

        snapshot_id = repo.save_snapshot(snapshot)

        assert snapshot_id.startswith("sig_")
        assert len(snapshot_id) == 16  # sig_ + 12 chars

    def test_save_snapshot_minimal(self, repo):
        """Save snapshot with minimal data."""
        snapshot = {
            "signal_type": "campo_batalha",
            "domain": "test_domain",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        snapshot_id = repo.save_snapshot(snapshot)

        assert snapshot_id.startswith("sig_")

    def test_get_latest(self, repo):
        """Get latest snapshot for signal type and domain."""
        # Save multiple snapshots
        for i in range(3):
            snapshot = {
                "signal_type": "radar_silencio",
                "domain": "politics",
                "timestamp": f"2024-01-0{i+1}T00:00:00Z",
                "values": {"index": i},
            }
            repo.save_snapshot(snapshot)

        latest = repo.get_latest("radar_silencio", "politics")

        assert latest is not None
        assert latest["timestamp"] == "2024-01-03T00:00:00Z"
        assert latest["values"]["index"] == 2

    def test_get_latest_not_found(self, repo):
        """Get latest when no snapshots exist."""
        result = repo.get_latest("nonexistent", "domain")
        assert result is None

    def test_get_history(self, repo):
        """Get historical snapshots."""
        for i in range(5):
            snapshot = {
                "signal_type": "fragilidade_narrativa",
                "domain": "health",
                "timestamp": f"2024-01-{i+1:02d}T00:00:00Z",
                "values": {"score": i * 10},
            }
            repo.save_snapshot(snapshot)

        history = repo.get_history("fragilidade_narrativa", "health", limit=3)

        assert len(history) == 3
        # Should be ordered by timestamp DESC
        assert history[0]["timestamp"] == "2024-01-05T00:00:00Z"
        assert history[1]["timestamp"] == "2024-01-04T00:00:00Z"
        assert history[2]["timestamp"] == "2024-01-03T00:00:00Z"

    def test_get_history_empty(self, repo):
        """Get history when no snapshots exist."""
        history = repo.get_history("test", "domain")
        assert history == []

    def test_get_history_limit(self, repo):
        """History respects limit."""
        for i in range(10):
            snapshot = {
                "signal_type": "test",
                "domain": "domain",
                "timestamp": f"2024-01-{i+1:02d}T00:00:00Z",
            }
            repo.save_snapshot(snapshot)

        history = repo.get_history("test", "domain", limit=5)
        assert len(history) == 5

    def test_get_all_latest(self, repo):
        """Get latest snapshot for each signal type."""
        signal_types = [
            "mentiras_em_circulacao",
            "campo_batalha",
            "radar_silencio",
            "fragilidade_narrativa",
        ]

        for sig_type in signal_types:
            snapshot = {
                "signal_type": sig_type,
                "domain": "politics",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "values": {"type": sig_type},
            }
            repo.save_snapshot(snapshot)

        all_latest = repo.get_all_latest("politics")

        assert len(all_latest) == 4
        types_found = {s["signal_type"] for s in all_latest}
        assert types_found == set(signal_types)

    def test_get_all_latest_partial(self, repo):
        """Get all latest when only some signal types exist."""
        snapshot = {
            "signal_type": "mentiras_em_circulacao",
            "domain": "test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        repo.save_snapshot(snapshot)

        all_latest = repo.get_all_latest("test")

        assert len(all_latest) == 1
        assert all_latest[0]["signal_type"] == "mentiras_em_circulacao"

    def test_get_all_latest_empty_domain(self, repo):
        """Get all latest for domain with no data."""
        all_latest = repo.get_all_latest("nonexistent")
        assert all_latest == []

    def test_count_snapshots_all(self, repo):
        """Count all snapshots."""
        for i in range(5):
            snapshot = {
                "signal_type": "test",
                "domain": "domain",
                "timestamp": f"2024-01-0{i+1}T00:00:00Z",
            }
            repo.save_snapshot(snapshot)

        count = repo.count_snapshots()
        assert count == 5

    def test_count_snapshots_by_signal_type(self, repo):
        """Count snapshots by signal type."""
        for sig_type in ["a", "a", "a", "b", "b"]:
            snapshot = {
                "signal_type": sig_type,
                "domain": "domain",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            repo.save_snapshot(snapshot)

        count_a = repo.count_snapshots(signal_type="a")
        count_b = repo.count_snapshots(signal_type="b")

        assert count_a == 3
        assert count_b == 2

    def test_count_snapshots_by_domain(self, repo):
        """Count snapshots by domain."""
        for domain in ["d1", "d1", "d2"]:
            snapshot = {
                "signal_type": "test",
                "domain": domain,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            repo.save_snapshot(snapshot)

        count_d1 = repo.count_snapshots(domain="d1")
        count_d2 = repo.count_snapshots(domain="d2")

        assert count_d1 == 2
        assert count_d2 == 1

    def test_count_snapshots_combined_filters(self, repo):
        """Count with both signal_type and domain filters."""
        snapshots = [
            {"signal_type": "a", "domain": "d1"},
            {"signal_type": "a", "domain": "d1"},
            {"signal_type": "a", "domain": "d2"},
            {"signal_type": "b", "domain": "d1"},
        ]

        for s in snapshots:
            s["timestamp"] = datetime.now(timezone.utc).isoformat()
            repo.save_snapshot(s)

        count = repo.count_snapshots(signal_type="a", domain="d1")
        assert count == 2

    def test_count_snapshots_empty(self, repo):
        """Count with no matching snapshots."""
        count = repo.count_snapshots(signal_type="nonexistent")
        assert count == 0

    def test_snapshot_values_json_roundtrip(self, repo):
        """Values are properly stored and retrieved as JSON."""
        original_values = {
            "nested": {"key": "value"},
            "array": [1, 2, 3],
            "number": 42.5,
            "boolean": True,
        }

        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "values": original_values,
        }
        repo.save_snapshot(snapshot)

        retrieved = repo.get_latest("test", "domain")

        assert retrieved["values"] == original_values

    def test_snapshot_metadata_json_roundtrip(self, repo):
        """Metadata is properly stored and retrieved as JSON."""
        original_metadata = {
            "source": "batch_calculator",
            "version": "1.0",
            "params": {"threshold": 0.5},
        }

        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": original_metadata,
        }
        repo.save_snapshot(snapshot)

        retrieved = repo.get_latest("test", "domain")

        assert retrieved["metadata"] == original_metadata

    def test_multiple_domains_isolation(self, repo):
        """Snapshots from different domains are isolated."""
        snapshot1 = {
            "signal_type": "test",
            "domain": "domain1",
            "timestamp": "2024-01-01T00:00:00Z",
            "values": {"domain": 1},
        }
        snapshot2 = {
            "signal_type": "test",
            "domain": "domain2",
            "timestamp": "2024-01-02T00:00:00Z",
            "values": {"domain": 2},
        }

        repo.save_snapshot(snapshot1)
        repo.save_snapshot(snapshot2)

        result1 = repo.get_latest("test", "domain1")
        result2 = repo.get_latest("test", "domain2")

        assert result1["values"]["domain"] == 1
        assert result2["values"]["domain"] == 2

    def test_unique_snapshot_ids(self, repo):
        """Each snapshot gets a unique ID."""
        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        id1 = repo.save_snapshot(snapshot)
        id2 = repo.save_snapshot(snapshot)

        assert id1 != id2

    def test_init_default_path(self, tmp_path):
        """Initialize with default path (file-based)."""
        from unittest.mock import patch

        db_file = tmp_path / "signals.sqlite"
        with patch("app.signals.signal_repository.DEFAULT_DB_PATH", db_file):
            repo = SignalRepository()

        assert repo.db_path == db_file
        assert repo._is_memory is False

    def test_file_based_db_creates_parent(self, tmp_path):
        """File-based db creates parent directory."""
        nested_path = tmp_path / "nested" / "dir" / "signals.sqlite"
        repo = SignalRepository(db_path=nested_path)

        assert nested_path.parent.exists()

    def test_conn_property_raises_for_file_based(self, tmp_path):
        """conn property raises for file-based db."""
        db_file = tmp_path / "test.sqlite"
        repo = SignalRepository(db_path=db_file)

        with pytest.raises(ValueError, match="Direct conn access"):
            _ = repo.conn

    def test_conn_property_in_memory_after_operation(self, repo):
        """conn property works for in-memory db after operation."""
        # First, trigger a connection
        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        repo.save_snapshot(snapshot)

        # Now conn should be accessible
        conn = repo.conn
        assert conn is not None

    def test_row_to_snapshot_invalid_values_json(self, repo):
        """Handle invalid values_json gracefully."""
        from unittest.mock import MagicMock

        # Create a mock row with invalid JSON
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {
            "id": "sig_test",
            "signal_type": "test",
            "domain": "domain",
            "timestamp": "2024-01-01T00:00:00Z",
            "values_json": "not valid json {{{",
            "metadata_json": "{}",
            "created_at": "2024-01-01T00:00:00Z",
        }.get(key)

        result = repo._row_to_snapshot(mock_row)

        assert result["values"] == {}

    def test_row_to_snapshot_invalid_metadata_json(self, repo):
        """Handle invalid metadata_json gracefully."""
        from unittest.mock import MagicMock

        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {
            "id": "sig_test",
            "signal_type": "test",
            "domain": "domain",
            "timestamp": "2024-01-01T00:00:00Z",
            "values_json": "{}",
            "metadata_json": "invalid json [[[",
            "created_at": "2024-01-01T00:00:00Z",
        }.get(key)

        result = repo._row_to_snapshot(mock_row)

        assert result["metadata"] == {}

    def test_row_to_snapshot_none_json_fields(self, repo):
        """Handle None json fields gracefully."""
        from unittest.mock import MagicMock

        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {
            "id": "sig_test",
            "signal_type": "test",
            "domain": "domain",
            "timestamp": "2024-01-01T00:00:00Z",
            "values_json": None,
            "metadata_json": None,
            "created_at": "2024-01-01T00:00:00Z",
        }.get(key)

        result = repo._row_to_snapshot(mock_row)

        assert result["values"] == {}
        assert result["metadata"] == {}

    def test_file_based_save_and_retrieve(self, tmp_path):
        """Save and retrieve from file-based db."""
        db_file = tmp_path / "test_signals.sqlite"
        repo = SignalRepository(db_path=db_file)

        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "values": {"key": "value"},
        }

        snapshot_id = repo.save_snapshot(snapshot)
        retrieved = repo.get_latest("test", "domain")

        assert retrieved is not None
        assert retrieved["id"] == snapshot_id

    def test_rollback_on_error_in_memory(self, repo):
        """Test rollback on error in in-memory db."""
        # Save a valid snapshot first
        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        repo.save_snapshot(snapshot)

        # Try to insert with duplicate ID (will fail)
        from unittest.mock import patch

        with patch("app.signals.signal_repository._generate_id", return_value="fixed_id"):
            repo.save_snapshot(snapshot)

            # Second insert with same ID should trigger rollback
            try:
                repo.save_snapshot(snapshot)
            except Exception:
                pass  # Expected error from duplicate ID

        # Repo should still work after rollback
        count = repo.count_snapshots()
        assert count >= 1

    def test_rollback_on_error_file_based(self, tmp_path):
        """Test rollback on error in file-based db."""
        db_file = tmp_path / "test.sqlite"
        repo = SignalRepository(db_path=db_file)

        snapshot = {
            "signal_type": "test",
            "domain": "domain",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        repo.save_snapshot(snapshot)

        # Try invalid operation
        from unittest.mock import patch

        with patch("app.signals.signal_repository._generate_id", return_value="fixed_id"):
            repo.save_snapshot(snapshot)
            try:
                repo.save_snapshot(snapshot)
            except Exception:
                pass

        count = repo.count_snapshots()
        assert count >= 1
