"""
Tests for Flows Rollout — S37

Tests for flow rollout convenience functions.
"""

import pytest
from unittest.mock import MagicMock

from app.flows.rollout import start_rollout, promote_rollout, rollback_rollout


class TestStartRollout:
    """Tests for start_rollout function."""

    def test_start_rollout_basic(self):
        """Start rollout calls service."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"

        mock_service = MagicMock()
        mock_service.start_rollout.return_value = mock_flow

        result = start_rollout(
            service=mock_service,
            flow_id="flow_123",
            mode="canary",
            test_percentual=10,
        )

        assert result == mock_flow
        mock_service.start_rollout.assert_called_once_with(
            "flow_123",
            mode="canary",
            test_percentual=10,
            criteria={},
            actor=None,
        )

    def test_start_rollout_with_criteria(self):
        """Start rollout with criteria."""
        mock_flow = MagicMock()
        mock_service = MagicMock()
        mock_service.start_rollout.return_value = mock_flow

        criteria = {"region": "br", "min_success_rate": 0.95}

        result = start_rollout(
            service=mock_service,
            flow_id="flow_123",
            mode="gradual",
            test_percentual=25,
            criteria=criteria,
        )

        assert result == mock_flow
        mock_service.start_rollout.assert_called_once_with(
            "flow_123",
            mode="gradual",
            test_percentual=25,
            criteria=criteria,
            actor=None,
        )

    def test_start_rollout_with_actor(self):
        """Start rollout with actor."""
        mock_flow = MagicMock()
        mock_service = MagicMock()
        mock_service.start_rollout.return_value = mock_flow

        result = start_rollout(
            service=mock_service,
            flow_id="flow_123",
            mode="canary",
            test_percentual=5,
            actor="admin_user",
        )

        mock_service.start_rollout.assert_called_once_with(
            "flow_123",
            mode="canary",
            test_percentual=5,
            criteria={},
            actor="admin_user",
        )


class TestPromoteRollout:
    """Tests for promote_rollout function."""

    def test_promote_rollout_basic(self):
        """Promote rollout calls service."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"

        mock_service = MagicMock()
        mock_service.promote_rollout.return_value = mock_flow

        result = promote_rollout(service=mock_service, flow_id="flow_123")

        assert result == mock_flow
        mock_service.promote_rollout.assert_called_once_with("flow_123", actor=None)

    def test_promote_rollout_with_actor(self):
        """Promote rollout with actor."""
        mock_flow = MagicMock()
        mock_service = MagicMock()
        mock_service.promote_rollout.return_value = mock_flow

        result = promote_rollout(
            service=mock_service,
            flow_id="flow_123",
            actor="reviewer_user",
        )

        mock_service.promote_rollout.assert_called_once_with("flow_123", actor="reviewer_user")


class TestRollbackRollout:
    """Tests for rollback_rollout function."""

    def test_rollback_rollout_basic(self):
        """Rollback rollout calls service."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"

        mock_service = MagicMock()
        mock_service.rollback_rollout.return_value = mock_flow

        result = rollback_rollout(service=mock_service, flow_id="flow_123")

        assert result == mock_flow
        mock_service.rollback_rollout.assert_called_once_with(
            "flow_123",
            target_version_id=None,
            actor=None,
        )

    def test_rollback_rollout_with_target_version(self):
        """Rollback rollout to specific version."""
        mock_flow = MagicMock()
        mock_service = MagicMock()
        mock_service.rollback_rollout.return_value = mock_flow

        result = rollback_rollout(
            service=mock_service,
            flow_id="flow_123",
            target_version_id="version_456",
        )

        mock_service.rollback_rollout.assert_called_once_with(
            "flow_123",
            target_version_id="version_456",
            actor=None,
        )

    def test_rollback_rollout_with_actor(self):
        """Rollback rollout with actor."""
        mock_flow = MagicMock()
        mock_service = MagicMock()
        mock_service.rollback_rollout.return_value = mock_flow

        result = rollback_rollout(
            service=mock_service,
            flow_id="flow_123",
            actor="ops_user",
        )

        mock_service.rollback_rollout.assert_called_once_with(
            "flow_123",
            target_version_id=None,
            actor="ops_user",
        )

    def test_rollback_rollout_full(self):
        """Rollback rollout with all parameters."""
        mock_flow = MagicMock()
        mock_service = MagicMock()
        mock_service.rollback_rollout.return_value = mock_flow

        result = rollback_rollout(
            service=mock_service,
            flow_id="flow_123",
            target_version_id="version_789",
            actor="incident_responder",
        )

        mock_service.rollback_rollout.assert_called_once_with(
            "flow_123",
            target_version_id="version_789",
            actor="incident_responder",
        )
