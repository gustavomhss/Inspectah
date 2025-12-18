"""
Tests for Flows Routing Policy — S37

Tests for flow routing and selection.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.flows.routing_policy import RoutingDecision, select_flow_for_event
from app.flows.models import FlowState


class TestRoutingDecision:
    """Tests for RoutingDecision class."""

    def test_create(self):
        """Create routing decision."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"

        decision = RoutingDecision(flow=mock_flow, motivo="test_reason")

        assert decision.flow == mock_flow
        assert decision.motivo == "test_reason"

    def test_attributes(self):
        """Decision has flow and motivo attributes."""
        mock_flow = MagicMock()
        decision = RoutingDecision(mock_flow, "fluxo_ativo")

        assert hasattr(decision, "flow")
        assert hasattr(decision, "motivo")


class TestSelectFlowForEvent:
    """Tests for select_flow_for_event function."""

    def test_select_active_flow(self):
        """Select active flow when available."""
        mock_flow = MagicMock()
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.estado = FlowState.ATIVO
        mock_flow.percentual_teste = 0

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_flow]

        evento = {"tipo_entrada": "noticia_texto"}

        decision = select_flow_for_event(evento, service=mock_service)

        assert decision.flow == mock_flow
        assert decision.motivo == "fluxo_ativo"

    def test_select_test_flow_when_no_active(self):
        """Select test flow when no active flow."""
        mock_flow = MagicMock()
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.estado = FlowState.EM_TESTE
        mock_flow.percentual_teste = 50

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_flow]

        evento = {"tipo_entrada": "noticia_texto"}

        decision = select_flow_for_event(evento, service=mock_service)

        assert decision.flow == mock_flow
        assert decision.motivo == "fallback_em_teste_sem_ativo"

    def test_select_test_flow_by_percentage(self):
        """Select test flow based on percentage."""
        mock_active = MagicMock()
        mock_active.tipo_entrada = "noticia_texto"
        mock_active.estado = FlowState.ATIVO

        mock_test = MagicMock()
        mock_test.tipo_entrada = "noticia_texto"
        mock_test.estado = FlowState.EM_TESTE
        mock_test.percentual_teste = 100  # 100% to test flow

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_active, mock_test]

        evento = {"tipo_entrada": "noticia_texto"}

        with patch("app.flows.routing_policy.random.randint", return_value=50):
            decision = select_flow_for_event(evento, service=mock_service)

        assert decision.flow == mock_test
        assert decision.motivo == "fluxo_em_teste_percentual"

    def test_select_active_when_percentage_not_hit(self):
        """Select active flow when random doesn't hit test percentage."""
        mock_active = MagicMock()
        mock_active.tipo_entrada = "noticia_texto"
        mock_active.estado = FlowState.ATIVO

        mock_test = MagicMock()
        mock_test.tipo_entrada = "noticia_texto"
        mock_test.estado = FlowState.EM_TESTE
        mock_test.percentual_teste = 10  # Only 10%

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_active, mock_test]

        evento = {"tipo_entrada": "noticia_texto"}

        # Random returns 50, which is > 10%, so active is selected
        with patch("app.flows.routing_policy.random.randint", return_value=50):
            decision = select_flow_for_event(evento, service=mock_service)

        assert decision.flow == mock_active
        assert decision.motivo == "fluxo_ativo"

    def test_raises_when_no_flow(self):
        """Raises ValueError when no flow for tipo_entrada."""
        mock_service = MagicMock()
        mock_service.list_flows.return_value = []

        evento = {"tipo_entrada": "noticia_texto"}

        with pytest.raises(ValueError, match="Nenhum fluxo ativo"):
            select_flow_for_event(evento, service=mock_service)

    def test_filters_by_tipo_entrada(self):
        """Only considers flows matching tipo_entrada."""
        mock_flow_wrong = MagicMock()
        mock_flow_wrong.tipo_entrada = "outro_tipo"
        mock_flow_wrong.estado = FlowState.ATIVO

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_flow_wrong]

        evento = {"tipo_entrada": "noticia_texto"}

        with pytest.raises(ValueError, match="Nenhum fluxo ativo"):
            select_flow_for_event(evento, service=mock_service)

    def test_filters_test_with_zero_percent(self):
        """Test flows with 0% are not selected."""
        mock_test = MagicMock()
        mock_test.tipo_entrada = "noticia_texto"
        mock_test.estado = FlowState.EM_TESTE
        mock_test.percentual_teste = 0  # 0% means not in routing

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_test]

        evento = {"tipo_entrada": "noticia_texto"}

        with pytest.raises(ValueError, match="Nenhum fluxo ativo"):
            select_flow_for_event(evento, service=mock_service)
