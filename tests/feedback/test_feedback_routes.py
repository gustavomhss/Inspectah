"""
Tests for Feedback Routes — S37

Tests for feedback API routes.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestListFeedbacks:
    """Tests for list_feedbacks function."""

    def test_list_feedbacks_no_filter(self):
        """List feedbacks without filter."""
        mock_service = MagicMock()
        mock_entry = MagicMock()
        mock_entry.to_dict.return_value = {"id": "fb_1", "status": "pending"}
        mock_service.list_feedbacks.return_value = [mock_entry]

        with patch("app.feedback.routes.DEFAULT_FEEDBACK_SERVICE", mock_service):
            with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
                from app.feedback.routes import list_feedbacks

                result = list_feedbacks()

        assert result["status"] == "todos"
        assert len(result["items"]) == 1

    def test_list_feedbacks_with_status(self):
        """List feedbacks filtered by status."""
        mock_service = MagicMock()
        mock_entry = MagicMock()
        mock_entry.to_dict.return_value = {"id": "fb_1", "status": "pending"}
        mock_service.list_feedbacks.return_value = [mock_entry]

        with patch("app.feedback.routes.DEFAULT_FEEDBACK_SERVICE", mock_service):
            with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
                from app.feedback.routes import list_feedbacks

                result = list_feedbacks(status="pending")

        assert result["status"] == "pending"
        mock_service.list_feedbacks.assert_called_with("pending")

    def test_list_feedbacks_invalid_status(self):
        """Invalid status is normalized to None."""
        mock_service = MagicMock()
        mock_service.list_feedbacks.return_value = []

        with patch("app.feedback.routes.DEFAULT_FEEDBACK_SERVICE", mock_service):
            with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
                from app.feedback.routes import list_feedbacks

                result = list_feedbacks(status="invalid")

        assert result["status"] == "todos"
        mock_service.list_feedbacks.assert_called_with(None)

    def test_list_feedbacks_empty(self):
        """List feedbacks returns empty list."""
        mock_service = MagicMock()
        mock_service.list_feedbacks.return_value = []

        with patch("app.feedback.routes.DEFAULT_FEEDBACK_SERVICE", mock_service):
            with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
                from app.feedback.routes import list_feedbacks

                result = list_feedbacks()

        assert result["items"] == []


class TestUpdateFeedback:
    """Tests for update_feedback function."""

    def test_update_feedback_success(self):
        """Update feedback status successfully."""
        mock_service = MagicMock()
        mock_entry = MagicMock()
        mock_entry.to_dict.return_value = {"id": "fb_1", "status": "resolved"}
        mock_service.update_feedback_status.return_value = mock_entry

        with patch("app.feedback.routes.DEFAULT_FEEDBACK_SERVICE", mock_service):
            with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
                from app.feedback.routes import update_feedback

                result = update_feedback("fb_1", {"status": "resolved"})

        assert result["item"]["status"] == "resolved"
        mock_service.update_feedback_status.assert_called_once_with("fb_1", "resolved")

    def test_update_feedback_invalid_status(self):
        """Update with invalid status raises ValueError."""
        with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
            from app.feedback.routes import update_feedback

            with pytest.raises(ValueError, match="status inválido"):
                update_feedback("fb_1", {"status": "invalid"})

    def test_update_feedback_missing_status(self):
        """Update without status raises ValueError."""
        with patch("app.feedback.routes.VALID_STATUSES", {"pending", "resolved"}):
            from app.feedback.routes import update_feedback

            with pytest.raises(ValueError, match="status inválido"):
                update_feedback("fb_1", {})


class TestRouterExports:
    """Tests for module exports."""

    def test_exports(self):
        """Module exports expected functions."""
        from app.feedback.routes import __all__

        assert "list_feedbacks" in __all__
        assert "update_feedback" in __all__
        assert "router" in __all__
