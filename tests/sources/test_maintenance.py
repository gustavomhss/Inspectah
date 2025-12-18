"""
Tests for Sources Maintenance — S37

Tests for source normalization and deduplication.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

from app.sources.maintenance import (
    _state_priority,
    normalize_all_sources,
    deduplicate_sources,
)
from app.sources.models import Source, SourceState


class TestStatePriority:
    """Tests for _state_priority function."""

    def test_active_highest_priority(self):
        """ACTIVE has highest priority (0)."""
        result = _state_priority(SourceState.ACTIVE)

        assert result == 0

    def test_testing_second_priority(self):
        """TESTING has second priority."""
        result = _state_priority(SourceState.TESTING)

        assert result == 1

    def test_under_review_third(self):
        """UNDER_REVIEW has third priority."""
        result = _state_priority(SourceState.UNDER_REVIEW)

        assert result == 2

    def test_suspect_fourth(self):
        """SUSPECT has fourth priority."""
        result = _state_priority(SourceState.SUSPECT)

        assert result == 3

    def test_proposed_fifth(self):
        """PROPOSED has fifth priority."""
        result = _state_priority(SourceState.PROPOSED)

        assert result == 4

    def test_disabled_temp_sixth(self):
        """DISABLED_TEMP has sixth priority."""
        result = _state_priority(SourceState.DISABLED_TEMP)

        assert result == 5

    def test_disabled_perm_lowest(self):
        """DISABLED_PERM has lowest priority."""
        result = _state_priority(SourceState.DISABLED_PERM)

        assert result == 6

    def test_unknown_state_returns_99(self):
        """Unknown state returns 99."""
        result = _state_priority("unknown_state")

        assert result == 99


class TestNormalizeAllSources:
    """Tests for normalize_all_sources function."""

    def test_normalize_all_sources_empty(self):
        """Normalize with no sources."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            mock_service.list_sources.return_value = []
            mock_service.get_connection.return_value = mock_conn

            result = normalize_all_sources()

        assert result["normalized"] == 0
        assert result["lab_ingestion_adjusted"] == 0

    def test_normalize_all_sources_updates_changed(self):
        """Normalize updates changed sources."""
        mock_source = MagicMock(spec=Source)
        mock_source.id = "src_1"
        mock_source.state = SourceState.ACTIVE
        mock_source.endpoint = "https://example.com/feed"

        mock_normalized = MagicMock(spec=Source)
        mock_normalized.state = SourceState.TESTING  # Different state

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            with patch("app.sources.maintenance.normalize_source_model") as mock_normalize:
                with patch("app.sources.maintenance.is_lab_endpoint") as mock_is_lab:
                    mock_service.list_sources.return_value = [mock_source]
                    mock_service.get_connection.return_value = mock_conn
                    mock_normalize.return_value = mock_normalized
                    mock_is_lab.return_value = False

                    result = normalize_all_sources(changed_by="test_user")

        assert result["normalized"] == 1

    def test_normalize_all_sources_no_changes(self):
        """Normalize skips unchanged sources."""
        mock_source = MagicMock(spec=Source)
        mock_source.id = "src_1"
        mock_source.state = SourceState.ACTIVE
        mock_source.endpoint = "https://example.com/feed"

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            with patch("app.sources.maintenance.normalize_source_model") as mock_normalize:
                with patch("app.sources.maintenance.is_lab_endpoint") as mock_is_lab:
                    mock_service.list_sources.return_value = [mock_source]
                    mock_service.get_connection.return_value = mock_conn
                    mock_normalize.return_value = mock_source  # Same source
                    mock_is_lab.return_value = False

                    result = normalize_all_sources()

        assert result["normalized"] == 0

    def test_normalize_all_sources_adjusts_lab_ingestion(self):
        """Normalize adjusts lab endpoints."""
        mock_source = MagicMock(spec=Source)
        mock_source.id = "src_1"
        mock_source.state = SourceState.ACTIVE
        mock_source.endpoint = "http://localhost:8000/feed"

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            with patch("app.sources.maintenance.normalize_source_model") as mock_normalize:
                with patch("app.sources.maintenance.is_lab_endpoint") as mock_is_lab:
                    with patch("app.sources.maintenance.toggle_ingestion_mode") as mock_toggle:
                        mock_service.list_sources.return_value = [mock_source]
                        mock_service.get_connection.return_value = mock_conn
                        mock_normalize.return_value = mock_source
                        mock_is_lab.return_value = True

                        result = normalize_all_sources()

        assert result["lab_ingestion_adjusted"] == 1
        mock_toggle.assert_called_once()

    def test_normalize_all_sources_lab_toggle_error(self):
        """Normalize continues on lab toggle error."""
        mock_source = MagicMock(spec=Source)
        mock_source.id = "src_1"
        mock_source.state = SourceState.ACTIVE
        mock_source.endpoint = "http://localhost:8000/feed"

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            with patch("app.sources.maintenance.normalize_source_model") as mock_normalize:
                with patch("app.sources.maintenance.is_lab_endpoint") as mock_is_lab:
                    with patch("app.sources.maintenance.toggle_ingestion_mode") as mock_toggle:
                        mock_service.list_sources.return_value = [mock_source]
                        mock_service.get_connection.return_value = mock_conn
                        mock_normalize.return_value = mock_source
                        mock_is_lab.return_value = True
                        mock_toggle.side_effect = Exception("Toggle failed")

                        result = normalize_all_sources()

        assert result["lab_ingestion_adjusted"] == 0


class TestDeduplicateSources:
    """Tests for deduplicate_sources function."""

    def test_deduplicate_sources_empty(self):
        """Deduplicate with no sources."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            mock_service.list_sources.return_value = []
            mock_service.get_connection.return_value = mock_conn

            result = deduplicate_sources()

        assert result["deduplicated"] == 0

    def test_deduplicate_sources_no_duplicates(self):
        """Deduplicate with no duplicates."""
        mock_source1 = MagicMock(spec=Source)
        mock_source1.id = "src_1"
        mock_source1.endpoint = "https://example1.com"
        mock_source1.type = "rss"
        mock_source1.category = "news"
        mock_source1.state = SourceState.ACTIVE
        mock_source1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_source1.slug = "source1"
        mock_source1.meta = {}

        mock_source2 = MagicMock(spec=Source)
        mock_source2.id = "src_2"
        mock_source2.endpoint = "https://example2.com"  # Different endpoint
        mock_source2.type = "rss"
        mock_source2.category = "news"
        mock_source2.state = SourceState.ACTIVE
        mock_source2.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)
        mock_source2.slug = "source2"
        mock_source2.meta = {}

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            mock_service.list_sources.return_value = [mock_source1, mock_source2]
            mock_service.get_connection.return_value = mock_conn

            result = deduplicate_sources()

        assert result["deduplicated"] == 0

    def test_deduplicate_sources_with_duplicates(self):
        """Deduplicate removes duplicates."""
        mock_source1 = MagicMock(spec=Source)
        mock_source1.id = "src_1"
        mock_source1.endpoint = "https://example.com"
        mock_source1.type = "rss"
        mock_source1.category = "news"
        mock_source1.state = SourceState.ACTIVE
        mock_source1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_source1.slug = "source1"
        mock_source1.meta = {}

        mock_source2 = MagicMock(spec=Source)
        mock_source2.id = "src_2"
        mock_source2.endpoint = "https://example.com"  # Same endpoint
        mock_source2.type = "rss"
        mock_source2.category = "news"
        mock_source2.state = SourceState.TESTING
        mock_source2.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)
        mock_source2.slug = "source2"
        mock_source2.meta = {}
        mock_source2.state_reason = None

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            mock_service.list_sources.return_value = [mock_source1, mock_source2]
            mock_service.get_connection.return_value = mock_conn

            result = deduplicate_sources()

        assert result["deduplicated"] == 1
        mock_service._apply_state_transition.assert_called()

    def test_deduplicate_sources_keeps_active(self):
        """Deduplicate keeps active source as canonical."""
        now = datetime.now(timezone.utc)

        mock_source_active = MagicMock(spec=Source)
        mock_source_active.id = "src_active"
        mock_source_active.endpoint = "https://example.com"
        mock_source_active.type = "rss"
        mock_source_active.category = "news"
        mock_source_active.state = SourceState.ACTIVE
        mock_source_active.created_at = now
        mock_source_active.slug = "active_source"
        mock_source_active.meta = {}

        mock_source_testing = MagicMock(spec=Source)
        mock_source_testing.id = "src_testing"
        mock_source_testing.endpoint = "https://example.com"
        mock_source_testing.type = "rss"
        mock_source_testing.category = "news"
        mock_source_testing.state = SourceState.TESTING
        mock_source_testing.created_at = now
        mock_source_testing.slug = "testing_source"
        mock_source_testing.meta = {}
        mock_source_testing.state_reason = None

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            mock_service.list_sources.return_value = [mock_source_active, mock_source_testing]
            mock_service.get_connection.return_value = mock_conn

            result = deduplicate_sources()

        # Testing source should be deduplicated, active kept
        assert result["deduplicated"] == 1
        mock_service._apply_state_transition.assert_called_with(
            mock_conn,
            mock_source_testing,
            SourceState.DISABLED_PERM,
            f"Duplicada da fonte '{mock_source_active.slug}'",
            "normalizer",
        )

    def test_deduplicate_sources_already_disabled(self):
        """Deduplicate updates already disabled sources."""
        now = datetime.now(timezone.utc)

        mock_source1 = MagicMock(spec=Source)
        mock_source1.id = "src_1"
        mock_source1.endpoint = "https://example.com"
        mock_source1.type = "rss"
        mock_source1.category = "news"
        mock_source1.state = SourceState.ACTIVE
        mock_source1.created_at = now
        mock_source1.slug = "source1"
        mock_source1.meta = {}

        mock_source2 = MagicMock(spec=Source)
        mock_source2.id = "src_2"
        mock_source2.endpoint = "https://example.com"
        mock_source2.type = "rss"
        mock_source2.category = "news"
        mock_source2.state = SourceState.DISABLED_PERM  # Already disabled
        mock_source2.created_at = now
        mock_source2.slug = "source2"
        mock_source2.meta = {}
        mock_source2.state_reason = None

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("app.sources.maintenance.service") as mock_service:
            mock_service.list_sources.return_value = [mock_source1, mock_source2]
            mock_service.get_connection.return_value = mock_conn

            result = deduplicate_sources()

        assert result["deduplicated"] == 1
        # Should update record, not apply transition
        mock_service._update_source_record.assert_called()
