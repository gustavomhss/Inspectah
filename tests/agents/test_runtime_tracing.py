"""
Tests for app/agents/runtime_tracing.py

Covers:
- trace_flow_execution function
- trace_committee_decision function
- Integration with TraceRepository
- Default parameters
- Custom repository usage
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.agents.runtime_tracing import (
    trace_flow_execution,
    trace_committee_decision,
)
from app.truth.models import TraceLinkRefs


class TestTraceFlowExecution:
    """Test suite for trace_flow_execution."""

    @patch('app.agents.runtime_tracing.record_flow_trace')
    @patch('app.agents.runtime_tracing.TraceRepository')
    def test_trace_flow_execution_basic(self, mock_repo_class, mock_record):
        """Test basic flow execution tracing."""
        link_refs = TraceLinkRefs(
            truth_record_id="TR123",
            decision_record_id="DR456",
            claim_id="C789",
            domain="politics",
            risk_level="high",
            request_id="REQ001",
        )

        flow_plan = {
            "flow_id": "content_to_claim",
            "steps": ["extract", "validate", "store"],
        }

        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_record.return_value = "agent_trace_123"

        result = trace_flow_execution(link_refs, flow_plan)

        # Should call record_flow_trace with correct parameters
        mock_record.assert_called_once_with(
            link_refs,
            flow_plan,
            steps_summaries=None,
            repo=mock_repo_instance,
        )
        assert result == "agent_trace_123"

    @patch('app.agents.runtime_tracing.record_flow_trace')
    def test_trace_flow_execution_with_summaries(self, mock_record):
        """Test flow execution with step summaries."""
        link_refs = TraceLinkRefs(
            truth_record_id="TR123",
            claim_id="C789",
        )

        flow_plan = {"flow_id": "test_flow"}
        steps_summaries = ["Step 1 completed", "Step 2 completed"]

        mock_record.return_value = "trace_id"

        result = trace_flow_execution(
            link_refs,
            flow_plan,
            steps_summaries=steps_summaries,
        )

        # Check that steps_summaries were passed
        call_args = mock_record.call_args
        assert call_args[1]['steps_summaries'] == steps_summaries

    @patch('app.agents.runtime_tracing.record_flow_trace')
    def test_trace_flow_execution_custom_repo(self, mock_record):
        """Test flow execution with custom repository."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        flow_plan = {"flow_id": "custom_flow"}
        custom_repo = MagicMock()

        mock_record.return_value = "trace_custom"

        result = trace_flow_execution(
            link_refs,
            flow_plan,
            repo=custom_repo,
        )

        # Should use the provided repo
        call_args = mock_record.call_args
        assert call_args[1]['repo'] == custom_repo

    @patch('app.agents.runtime_tracing.record_flow_trace')
    @patch('app.agents.runtime_tracing.TraceRepository')
    def test_trace_flow_execution_default_repo(self, mock_repo_class, mock_record):
        """Test that default repository is created when not provided."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        flow_plan = {"flow_id": "default_flow"}

        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance

        trace_flow_execution(link_refs, flow_plan)

        # Should create a new TraceRepository
        mock_repo_class.assert_called_once()

    @patch('app.agents.runtime_tracing.record_flow_trace')
    def test_trace_flow_execution_complete_link_refs(self, mock_record):
        """Test with all TraceLinkRefs fields populated."""
        link_refs = TraceLinkRefs(
            truth_record_id="TR999",
            decision_record_id="DR888",
            claim_id="C777",
            domain="health",
            risk_level="medium",
            request_id="REQ999",
        )

        flow_plan = {"flow_id": "comprehensive_flow", "version": "1.0"}

        trace_flow_execution(link_refs, flow_plan)

        # Verify link_refs were passed correctly
        call_args = mock_record.call_args
        passed_refs = call_args[0][0]
        assert passed_refs.truth_record_id == "TR999"
        assert passed_refs.decision_record_id == "DR888"
        assert passed_refs.claim_id == "C777"
        assert passed_refs.domain == "health"


class TestTraceCommitteeDecision:
    """Test suite for trace_committee_decision."""

    @patch('app.agents.runtime_tracing.record_committee_trace')
    @patch('app.agents.runtime_tracing.TraceRepository')
    def test_trace_committee_decision_basic(self, mock_repo_class, mock_record):
        """Test basic committee decision tracing."""
        link_refs = TraceLinkRefs(
            truth_record_id="TR123",
            decision_record_id="DR456",
            claim_id="C789",
        )

        agent_trace_ids = ["agent_1", "agent_2", "agent_3"]
        summary = "Committee reached consensus"

        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_record.return_value = "committee_trace_123"

        result = trace_committee_decision(
            link_refs,
            agent_trace_ids,
            summary,
        )

        # Should call record_committee_trace with correct parameters
        mock_record.assert_called_once_with(
            link_refs=link_refs,
            agent_trace_ids=agent_trace_ids,
            summary=summary,
            committee_id="pilot_committee",
            committee_version="v1",
            repo=mock_repo_instance,
        )
        assert result == "committee_trace_123"

    @patch('app.agents.runtime_tracing.record_committee_trace')
    def test_trace_committee_decision_custom_committee(self, mock_record):
        """Test committee decision with custom committee ID and version."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        agent_trace_ids = ["agent_1"]
        summary = "Decision summary"

        mock_record.return_value = "trace_id"

        result = trace_committee_decision(
            link_refs,
            agent_trace_ids,
            summary,
            committee_id="production_committee",
            committee_version="v2",
        )

        # Check custom committee parameters
        call_args = mock_record.call_args
        assert call_args[1]['committee_id'] == "production_committee"
        assert call_args[1]['committee_version'] == "v2"

    @patch('app.agents.runtime_tracing.record_committee_trace')
    def test_trace_committee_decision_custom_repo(self, mock_record):
        """Test committee decision with custom repository."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        agent_trace_ids = ["agent_1", "agent_2"]
        summary = "Custom repo test"
        custom_repo = MagicMock()

        mock_record.return_value = "trace_custom"

        result = trace_committee_decision(
            link_refs,
            agent_trace_ids,
            summary,
            repo=custom_repo,
        )

        # Should use the provided repo
        call_args = mock_record.call_args
        assert call_args[1]['repo'] == custom_repo

    @patch('app.agents.runtime_tracing.record_committee_trace')
    @patch('app.agents.runtime_tracing.TraceRepository')
    def test_trace_committee_decision_default_repo(self, mock_repo_class, mock_record):
        """Test that default repository is created when not provided."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        agent_trace_ids = ["agent_1"]
        summary = "Default repo test"

        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance

        trace_committee_decision(link_refs, agent_trace_ids, summary)

        # Should create a new TraceRepository
        mock_repo_class.assert_called_once()

    @patch('app.agents.runtime_tracing.record_committee_trace')
    def test_trace_committee_decision_empty_agents(self, mock_record):
        """Test committee decision with empty agent list."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        agent_trace_ids = []
        summary = "No agents involved"

        mock_record.return_value = "trace_empty"

        result = trace_committee_decision(link_refs, agent_trace_ids, summary)

        # Should still work with empty list
        call_args = mock_record.call_args
        assert call_args[1]['agent_trace_ids'] == []

    @patch('app.agents.runtime_tracing.record_committee_trace')
    def test_trace_committee_decision_many_agents(self, mock_record):
        """Test committee decision with many agent traces."""
        link_refs = TraceLinkRefs(truth_record_id="TR123")
        agent_trace_ids = [f"agent_{i}" for i in range(20)]
        summary = "Large committee"

        mock_record.return_value = "trace_large"

        result = trace_committee_decision(link_refs, agent_trace_ids, summary)

        # Should handle large list
        call_args = mock_record.call_args
        assert len(call_args[1]['agent_trace_ids']) == 20

    @patch('app.agents.runtime_tracing.record_committee_trace')
    def test_trace_committee_decision_complete_refs(self, mock_record):
        """Test with all TraceLinkRefs fields populated."""
        link_refs = TraceLinkRefs(
            truth_record_id="TR555",
            decision_record_id="DR444",
            claim_id="C333",
            domain="economics",
            risk_level="low",
            request_id="REQ555",
        )

        agent_trace_ids = ["agent_a", "agent_b"]
        summary = "Complete test"

        trace_committee_decision(link_refs, agent_trace_ids, summary)

        # Verify all fields were passed
        call_args = mock_record.call_args
        passed_refs = call_args[1]['link_refs']
        assert passed_refs.truth_record_id == "TR555"
        assert passed_refs.decision_record_id == "DR444"
        assert passed_refs.claim_id == "C333"
        assert passed_refs.domain == "economics"
        assert passed_refs.risk_level == "low"
        assert passed_refs.request_id == "REQ555"


class TestIntegration:
    """Integration tests for runtime tracing helpers."""

    @patch('app.agents.runtime_tracing.record_flow_trace')
    @patch('app.agents.runtime_tracing.record_committee_trace')
    @patch('app.agents.runtime_tracing.TraceRepository')
    def test_flow_then_committee_tracing(
        self, mock_repo_class, mock_committee, mock_flow
    ):
        """Test sequential flow and committee tracing."""
        link_refs = TraceLinkRefs(
            truth_record_id="TR123",
            decision_record_id="DR456",
            claim_id="C789",
        )

        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance

        # First trace flow execution
        flow_plan = {"flow_id": "test_flow"}
        mock_flow.return_value = "flow_trace_123"

        flow_trace_id = trace_flow_execution(link_refs, flow_plan)

        # Then trace committee decision using the flow trace
        agent_trace_ids = [flow_trace_id, "another_agent_trace"]
        summary = "Committee decision based on flow"
        mock_committee.return_value = "committee_trace_456"

        committee_trace_id = trace_committee_decision(
            link_refs,
            agent_trace_ids,
            summary,
        )

        # Verify both were called
        assert flow_trace_id == "flow_trace_123"
        assert committee_trace_id == "committee_trace_456"
        mock_flow.assert_called_once()
        mock_committee.assert_called_once()

    @patch('app.agents.runtime_tracing.record_flow_trace')
    @patch('app.agents.runtime_tracing.TraceRepository')
    def test_shared_repository(self, mock_repo_class, mock_flow):
        """Test using same repository instance for multiple traces."""
        shared_repo = MagicMock()

        link_refs_1 = TraceLinkRefs(truth_record_id="TR1")
        link_refs_2 = TraceLinkRefs(truth_record_id="TR2")

        flow_plan_1 = {"flow_id": "flow_1"}
        flow_plan_2 = {"flow_id": "flow_2"}

        # Use same repo for both traces
        trace_flow_execution(link_refs_1, flow_plan_1, repo=shared_repo)
        trace_flow_execution(link_refs_2, flow_plan_2, repo=shared_repo)

        # Both should use the same repo instance
        assert mock_flow.call_count == 2
        for call in mock_flow.call_args_list:
            assert call[1]['repo'] == shared_repo

        # TraceRepository should not have been instantiated
        mock_repo_class.assert_not_called()
