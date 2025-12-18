"""
Tests for agents/reporting — S37

Tests for agent reporting functions.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from dataclasses import field

from app.agents.reporting import AgentReport, log_agent_report, log_committee_decision


class TestAgentReport:
    """Tests for AgentReport dataclass."""

    def test_create_agent_report(self):
        """Create an agent report."""
        report = AgentReport(
            agent_id="agent_1",
            committee_id="comm_1",
            role="analyst",
            status="completed",
            bundle_ref="bundle_123",
            notes="Test notes",
        )

        assert report.agent_id == "agent_1"
        assert report.committee_id == "comm_1"
        assert report.role == "analyst"
        assert report.status == "completed"

    def test_create_agent_report_minimal(self):
        """Create agent report with minimal fields."""
        report = AgentReport(
            agent_id="agent_2",
            committee_id=None,
            role="reviewer",
            status="pending",
            bundle_ref=None,
            notes=None,
        )

        assert report.agent_id == "agent_2"
        assert report.committee_id is None
        assert report.notes is None


class TestLogAgentReport:
    """Tests for log_agent_report function."""

    def test_log_agent_report_basic(self):
        """Log a basic agent report."""
        report = AgentReport(
            agent_id="agent_1",
            committee_id="comm_1",
            role="analyst",
            status="completed",
            bundle_ref="bundle_123",
            notes="Test",
        )

        with patch("app.agents.reporting.logger") as mock_logger:
            log_agent_report(report)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "agent.report"
            assert "event" in call_args[1]["extra"]

    def test_log_agent_report_with_payload(self):
        """Log agent report with payload."""
        report = AgentReport(
            agent_id="agent_1",
            committee_id="comm_1",
            role="analyst",
            status="completed",
            bundle_ref="bundle_123",
            notes="Test",
            payload={"key": "value", "count": 42},
        )

        with patch("app.agents.reporting.logger") as mock_logger:
            log_agent_report(report)

            mock_logger.info.assert_called_once()

    def test_log_agent_report_none_payload(self):
        """Log agent report with None payload."""
        report = AgentReport(
            agent_id="agent_1",
            committee_id=None,
            role="analyst",
            status="pending",
            bundle_ref=None,
            notes=None,
            payload=None,
        )

        with patch("app.agents.reporting.logger") as mock_logger:
            log_agent_report(report)

            mock_logger.info.assert_called_once()


class TestLogCommitteeDecision:
    """Tests for log_committee_decision function."""

    def test_log_committee_decision_basic(self):
        """Log basic committee decision."""
        with patch("app.agents.reporting.logger") as mock_logger:
            log_committee_decision(
                committee_id="comm_1",
                run_id="run_123",
                outcome="approved",
            )

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "committee.decision"
            extra = call_args[1]["extra"]
            assert extra["committee_id"] == "comm_1"
            assert extra["run_id"] == "run_123"
            assert extra["outcome"] == "approved"

    def test_log_committee_decision_with_disagreement(self):
        """Log committee decision with disagreement score."""
        with patch("app.agents.reporting.logger") as mock_logger:
            log_committee_decision(
                committee_id="comm_2",
                run_id="run_456",
                outcome="rejected",
                disagreement_score=0.75,
            )

            mock_logger.info.assert_called_once()
            extra = mock_logger.info.call_args[1]["extra"]
            assert extra["disagreement_score"] == 0.75

    def test_log_committee_decision_none_disagreement(self):
        """Log committee decision with None disagreement."""
        with patch("app.agents.reporting.logger") as mock_logger:
            log_committee_decision(
                committee_id="comm_3",
                run_id="run_789",
                outcome="pending",
                disagreement_score=None,
            )

            mock_logger.info.assert_called_once()
            extra = mock_logger.info.call_args[1]["extra"]
            assert extra["disagreement_score"] is None

    def test_log_committee_decision_includes_timestamp(self):
        """Log committee decision includes timestamp."""
        with patch("app.agents.reporting.logger") as mock_logger:
            log_committee_decision(
                committee_id="comm_1",
                run_id="run_1",
                outcome="approved",
            )

            extra = mock_logger.info.call_args[1]["extra"]
            assert "ts" in extra
            assert isinstance(extra["ts"], str)
