"""
Tests for obs/metrics — S37

Tests for admin/UI metrics functions.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.obs import metrics


class TestRecordAdminRequest:
    """Tests for record_admin_request function."""

    def test_record_admin_request_basic(self):
        """Record a basic admin request."""
        with patch.object(metrics, "_admin_requests") as mock_counter:
            mock_labels = MagicMock()
            mock_counter.labels.return_value = mock_labels

            metrics.record_admin_request("/api/health", 200)

            mock_counter.labels.assert_called_once_with(route="/api/health", status="200")
            mock_labels.inc.assert_called_once()

    def test_record_admin_request_admin_route(self):
        """Record admin route updates dashboard age."""
        with patch.object(metrics, "_admin_requests") as mock_counter:
            with patch.object(metrics, "_admin_dashboard_age") as mock_gauge:
                mock_labels = MagicMock()
                mock_counter.labels.return_value = mock_labels
                mock_gauge_labels = MagicMock()
                mock_gauge.labels.return_value = mock_gauge_labels

                metrics.record_admin_request("/admin/overview", 200)

                mock_gauge.labels.assert_called_with(dashboard="sf3_obs_overview")
                mock_gauge_labels.set.assert_called_with(0)

    def test_record_admin_request_non_admin_route(self):
        """Non-admin route doesn't update dashboard age."""
        with patch.object(metrics, "_admin_requests") as mock_counter:
            with patch.object(metrics, "_admin_dashboard_age") as mock_gauge:
                mock_labels = MagicMock()
                mock_counter.labels.return_value = mock_labels

                metrics.record_admin_request("/api/sources", 200)

                # Dashboard age should not be updated for non-admin routes
                mock_gauge.labels.assert_not_called()

    def test_record_admin_request_error_status(self):
        """Record request with error status."""
        with patch.object(metrics, "_admin_requests") as mock_counter:
            mock_labels = MagicMock()
            mock_counter.labels.return_value = mock_labels

            metrics.record_admin_request("/api/test", 500)

            mock_counter.labels.assert_called_once_with(route="/api/test", status="500")


class TestSeedDefaults:
    """Tests for seed_defaults function."""

    def test_seed_defaults(self):
        """Seed defaults initializes metrics."""
        with patch.object(metrics, "_admin_requests") as mock_counter:
            with patch.object(metrics, "_admin_dashboard_age") as mock_gauge:
                mock_labels = MagicMock()
                mock_counter.labels.return_value = mock_labels
                mock_gauge_labels = MagicMock()
                mock_gauge.labels.return_value = mock_gauge_labels

                metrics.seed_defaults()

                mock_counter.labels.assert_called_with(route="/admin/health", status="200")
                mock_gauge.labels.assert_called_with(dashboard="sf3_obs_overview")
