"""
Tests for Agent Flows Runtime Adapter — S37

Tests for runtime adapter functions.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.agents.flows.runtime_adapter import (
    DEFAULT_FALLBACK_STEPS,
    _build_plan,
    _normalize_step,
    get_agent_flow_for_domain,
    get_executable_flow_plan,
    record_flow_trace,
)
from app.agents.flows.schemas import AgentFlowConfigOut, AgentFlowStepOut
from app.agents.models import AgentRole
from app.truth.models import TraceLinkRefs


class TestDefaultFallbackSteps:
    """Tests for DEFAULT_FALLBACK_STEPS constant."""

    def test_has_three_steps(self):
        """Fallback has three steps."""
        assert len(DEFAULT_FALLBACK_STEPS) == 3

    def test_step_order(self):
        """Steps are in correct order."""
        positions = [s["position"] for s in DEFAULT_FALLBACK_STEPS]
        assert positions == [1, 2, 3]

    def test_step_roles(self):
        """Steps have expected roles."""
        roles = [s["agent_role"] for s in DEFAULT_FALLBACK_STEPS]
        assert AgentRole.INTERPRETER.value in roles
        assert AgentRole.CLASSIFIER.value in roles
        assert AgentRole.DECISION_MAKER.value in roles


class TestNormalizeStep:
    """Tests for _normalize_step function."""

    def test_normalize_dict(self):
        """Dict passes through."""
        step = {"position": 1, "agent_role": "interpreter"}
        result = _normalize_step(step)
        assert result == step

    def test_normalize_schema(self):
        """Schema is converted to dict."""
        now = datetime.now(timezone.utc)
        step = AgentFlowStepOut(
            id="step_1",
            flow_id="flow_1",
            position=1,
            agent_role="interpreter",
            params={"key": "value"},
            required=True,
            can_fail_soft=False,
            created_at=now,
            updated_at=now,
        )

        result = _normalize_step(step)

        assert isinstance(result, dict)
        assert result["position"] == 1
        assert result["agent_role"] == "interpreter"


class TestBuildPlan:
    """Tests for _build_plan function."""

    def test_build_plan_basic(self):
        """Build plan from flow."""
        now = datetime.now(timezone.utc)
        flow = AgentFlowConfigOut(
            id="flow_123",
            domain_key="politics",
            name="Test Flow",
            description="Test flow description",
            is_active=True,
            change_reason="test",
            created_at=now,
            updated_at=now,
            created_by="system",
            updated_by="system",
            steps=[
                AgentFlowStepOut(
                    id="s1",
                    flow_id="flow_123",
                    position=1,
                    agent_role="interpreter",
                    params={},
                    required=True,
                    can_fail_soft=False,
                    created_at=now,
                    updated_at=now,
                ),
            ],
        )

        plan = _build_plan(flow)

        assert plan["flow_id"] == "flow_123"
        assert plan["domain_key"] == "politics"
        assert plan["used_fallback"] is False
        assert len(plan["steps"]) == 1

    def test_build_plan_fallback_flag(self):
        """Build plan with fallback flag."""
        now = datetime.now(timezone.utc)
        flow = AgentFlowConfigOut(
            id="fallback",
            domain_key="test",
            name="Fallback",
            description="",
            is_active=True,
            change_reason="fallback",
            created_at=now,
            updated_at=now,
            created_by="system",
            updated_by="system",
            steps=[],
        )

        plan = _build_plan(flow, used_fallback=True)

        assert plan["used_fallback"] is True


class TestGetAgentFlowForDomain:
    """Tests for get_agent_flow_for_domain function."""

    def test_no_flow_returns_fallback(self):
        """No flow configured returns fallback."""
        mock_service = MagicMock()
        mock_service.get_flow_by_domain.return_value = None

        flow, fallback = get_agent_flow_for_domain("unknown_domain", service=mock_service)

        assert flow is None
        assert fallback is True

    def test_valid_flow_returns_flow(self):
        """Valid flow is returned."""
        now = datetime.now(timezone.utc)

        # Create a simple object instead of MagicMock with __dict__ override
        class MockStep:
            def __init__(self):
                self.id = "step_1"
                self.flow_id = "flow_1"
                self.position = 1
                self.agent_role = "interpreter"
                self.params = {}
                self.required = True
                self.can_fail_soft = False
                self.created_at = now
                self.updated_at = now

        class MockFlow:
            def __init__(self):
                self.id = "flow_1"
                self.domain_key = "politics"
                self.name = "Test"
                self.description = "Test flow"
                self.is_active = True
                self.change_reason = "test"
                self.created_at = now
                self.updated_at = now
                self.created_by = "system"
                self.updated_by = "system"
                self.steps = [MockStep()]

        mock_flow = MockFlow()
        mock_service = MagicMock()
        mock_service.get_flow_by_domain.return_value = mock_flow

        with patch("app.agents.flows.runtime_adapter.validate_agent_flow") as mock_validate:
            mock_validate.return_value = []  # No errors

            flow, fallback = get_agent_flow_for_domain("politics", service=mock_service)

        assert flow is not None
        assert fallback is False

    def test_invalid_flow_returns_fallback(self):
        """Invalid flow returns fallback."""
        now = datetime.now(timezone.utc)

        class MockFlow:
            def __init__(self):
                self.id = "flow_1"
                self.domain_key = "politics"
                self.name = "Test"
                self.description = ""
                self.is_active = True
                self.change_reason = ""
                self.created_at = now
                self.updated_at = now
                self.created_by = ""
                self.updated_by = ""
                self.steps = []

        mock_flow = MockFlow()
        mock_service = MagicMock()
        mock_service.get_flow_by_domain.return_value = mock_flow

        with patch("app.agents.flows.runtime_adapter.validate_agent_flow") as mock_validate:
            mock_validate.return_value = ["Validation error"]

            flow, fallback = get_agent_flow_for_domain("politics", service=mock_service)

        assert flow is None
        assert fallback is True


class TestGetExecutableFlowPlan:
    """Tests for get_executable_flow_plan function."""

    def test_returns_fallback_when_no_flow(self):
        """Returns fallback plan when no flow configured."""
        with patch("app.agents.flows.runtime_adapter.get_agent_flow_for_domain") as mock_get:
            mock_get.return_value = (None, True)

            plan = get_executable_flow_plan("unknown_domain")

        assert plan["used_fallback"] is True
        assert plan["flow_id"] == "fallback"
        assert len(plan["steps"]) == 3  # Default fallback steps

    def test_returns_flow_plan_when_valid(self):
        """Returns flow plan when valid flow exists."""
        now = datetime.now(timezone.utc)
        mock_flow = AgentFlowConfigOut(
            id="flow_real",
            domain_key="politics",
            name="Real Flow",
            description="",
            is_active=True,
            change_reason="",
            created_at=now,
            updated_at=now,
            created_by="system",
            updated_by="system",
            steps=[
                AgentFlowStepOut(
                    id="s1",
                    flow_id="flow_real",
                    position=1,
                    agent_role="interpreter",
                    params={},
                    required=True,
                    can_fail_soft=False,
                    created_at=now,
                    updated_at=now,
                ),
            ],
        )

        with patch("app.agents.flows.runtime_adapter.get_agent_flow_for_domain") as mock_get:
            mock_get.return_value = (mock_flow, False)

            plan = get_executable_flow_plan("politics")

        assert plan["used_fallback"] is False
        assert plan["flow_id"] == "flow_real"

    def test_fallback_plan_has_correct_structure(self):
        """Fallback plan has correct structure."""
        with patch("app.agents.flows.runtime_adapter.get_agent_flow_for_domain") as mock_get:
            mock_get.return_value = (None, True)

            plan = get_executable_flow_plan("test_domain")

        assert "flow_id" in plan
        assert "domain_key" in plan
        assert "used_fallback" in plan
        assert "steps" in plan
        assert plan["domain_key"] == "test_domain"


class TestRecordFlowTrace:
    """Tests for record_flow_trace function."""

    def test_record_trace_basic(self):
        """Record trace creates AgentTrace."""
        link_refs = TraceLinkRefs(
            truth_record_id="truth_123",
            decision_record_id="dec_456",
            claim_id="claim_789",
            domain="politics",
            risk_level="low",
            request_id="req_012",
        )

        flow_plan = {
            "flow_id": "flow_1",
            "steps": [
                {"position": 1, "agent_role": "interpreter"},
                {"position": 2, "agent_role": "classifier"},
            ],
        }

        mock_repo = MagicMock()
        mock_repo.save_agent_trace.return_value = MagicMock()

        result = record_flow_trace(link_refs, flow_plan, repo=mock_repo)

        mock_repo.save_agent_trace.assert_called_once()
        trace_arg = mock_repo.save_agent_trace.call_args[0][0]
        assert trace_arg.claim_id == "claim_789"
        assert trace_arg.domain == "politics"
        assert len(trace_arg.steps) == 2

    def test_record_trace_with_summaries(self):
        """Record trace with custom step summaries."""
        link_refs = TraceLinkRefs(
            truth_record_id="t1",
            decision_record_id="d1",
            claim_id="c1",
            domain="politics",
        )

        flow_plan = {
            "flow_id": "flow_1",
            "steps": [
                {"position": 1, "agent_role": "interpreter"},
            ],
        }

        mock_repo = MagicMock()
        mock_repo.save_agent_trace.return_value = MagicMock()

        record_flow_trace(
            link_refs,
            flow_plan,
            steps_summaries=["Custom summary for step 1"],
            repo=mock_repo,
        )

        trace_arg = mock_repo.save_agent_trace.call_args[0][0]
        assert trace_arg.steps[0].summary == "Custom summary for step 1"

    def test_record_trace_default_domain(self):
        """Record trace uses default domain."""
        link_refs = TraceLinkRefs(
            truth_record_id="t1",
            decision_record_id="d1",
            claim_id="c1",
            domain="",  # Empty domain to test default
        )

        flow_plan = {
            "flow_id": "flow_1",
            "steps": [],
        }

        mock_repo = MagicMock()
        mock_repo.save_agent_trace.return_value = MagicMock()

        record_flow_trace(link_refs, flow_plan, repo=mock_repo)

        trace_arg = mock_repo.save_agent_trace.call_args[0][0]
        assert trace_arg.domain == "pilot_politics"

    def test_record_trace_step_details(self):
        """Record trace captures step details."""
        link_refs = TraceLinkRefs(
            truth_record_id="t1",
            decision_record_id="d1",
            claim_id="c1",
            domain="politics",
        )

        flow_plan = {
            "flow_id": "flow_xyz",
            "steps": [
                {"position": 1, "agent_role": "interpreter"},
            ],
        }

        mock_repo = MagicMock()
        mock_repo.save_agent_trace.return_value = MagicMock()

        record_flow_trace(link_refs, flow_plan, repo=mock_repo)

        trace_arg = mock_repo.save_agent_trace.call_args[0][0]
        step = trace_arg.steps[0]
        assert step.order == 1
        assert step.actor_role == "interpreter"
        assert step.step_kind == "flow_step"
        assert "flow_xyz" in step.input_refs
