"""
Tests for api/flow_console_routes — S37

Tests for flow console routes helper functions.
"""

import pytest
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.api.flow_console_routes import _service, _to_flow_read
from app.flows.service import FlowService


@dataclass
class MockFlow:
    """Mock flow for testing."""
    id: str
    nome: str
    slug: str
    tipo_entrada: str
    estado: str
    template_origem_id: Optional[str]
    percentual_teste: int
    domain: str
    flow_version_id: str
    active_version_id: Optional[str]
    test_version_id: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    rollout_mode: Optional[str] = None
    rollout_state: Optional[str] = None
    catalog_hash: Optional[str] = None
    catalog_signature: Optional[str] = None
    rollout_started_at: Optional[datetime] = None
    rollout_criteria: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockStep:
    """Mock step for testing."""
    id: str
    flow_id: str
    ordem: int
    tipo_etapa: str
    agent_role: str
    agent_binding: str
    config: Dict[str, Any]
    flags: Dict[str, Any]  # flags is a dict, not list
    created_at: datetime
    updated_at: datetime


class TestServiceFactory:
    """Tests for _service factory function."""

    def test_service_returns_flow_service(self):
        """Factory returns FlowService instance."""
        result = _service()
        assert isinstance(result, FlowService)


class TestToFlowRead:
    """Tests for _to_flow_read helper function."""

    def test_to_flow_read_minimal(self):
        """Convert flow to FlowRead with no steps."""
        flow = MockFlow(
            id="flow_1",
            nome="Test Flow",
            slug="test-flow",
            tipo_entrada="claim",
            estado="draft",
            template_origem_id="tpl_1",
            percentual_teste=0,
            domain="generic",
            flow_version_id="v1",
            active_version_id=None,
            test_version_id=None,
            metadata={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        result = _to_flow_read(flow)

        assert result.id == "flow_1"
        assert result.nome == "Test Flow"
        assert result.slug == "test-flow"
        assert result.steps == []

    def test_to_flow_read_with_steps(self):
        """Convert flow to FlowRead with steps."""
        now = datetime.now(timezone.utc)
        flow = MockFlow(
            id="flow_2",
            nome="Flow with Steps",
            slug="flow-steps",
            tipo_entrada="news",
            estado="ativo",
            template_origem_id="tpl_2",
            percentual_teste=10,
            domain="politics",
            flow_version_id="v2",
            active_version_id="v2",
            test_version_id=None,
            metadata={"key": "value"},
            created_at=now,
            updated_at=now,
        )

        step = MockStep(
            id="step_1",
            flow_id="flow_2",
            ordem=1,
            tipo_etapa="analista",
            agent_role="analyst",
            agent_binding="agent_1",
            config={},
            flags={},
            created_at=now,
            updated_at=now,
        )

        result = _to_flow_read(flow, steps=[step])

        assert result.id == "flow_2"
        assert len(result.steps) == 1
        assert result.steps[0].id == "step_1"

    def test_to_flow_read_with_rollout_attributes(self):
        """Convert flow with rollout attributes."""
        now = datetime.now(timezone.utc)
        flow = MockFlow(
            id="flow_3",
            nome="Rollout Flow",
            slug="rollout-flow",
            tipo_entrada="claim",
            estado="em_teste",
            template_origem_id="tpl_3",
            percentual_teste=20,
            domain="health",
            flow_version_id="v3",
            active_version_id="v2",
            test_version_id="v3",
            rollout_mode="canary",
            rollout_state="testing",
            catalog_hash="abc123",
            catalog_signature="sig_123",
            rollout_started_at=now,
            rollout_criteria={"min_success_rate": 0.95},
            metadata={},
            created_at=now,
            updated_at=now,
        )

        result = _to_flow_read(flow)

        assert result.rollout_mode == "canary"
        assert result.rollout_state == "testing"
        assert result.catalog_hash == "abc123"

    def test_to_flow_read_none_steps(self):
        """Convert flow with None steps defaults to empty list."""
        flow = MockFlow(
            id="flow_4",
            nome="No Steps",
            slug="no-steps",
            tipo_entrada="claim",
            estado="draft",
            template_origem_id=None,
            percentual_teste=0,
            domain="generic",
            flow_version_id="v1",
            active_version_id=None,
            test_version_id=None,
            metadata={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        result = _to_flow_read(flow, steps=None)

        assert result.steps == []
