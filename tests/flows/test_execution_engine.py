"""
Tests for Flows Execution Engine — S37

Tests for flow execution engine.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.flows.execution_engine import FlowExecutionEngine
from app.flows.models import FlowExecutionStatus, FlowStepExecutionStatus


class TestFlowExecutionEngine:
    """Tests for FlowExecutionEngine class."""

    def test_init_default_service(self):
        """Initialize with default service."""
        with patch("app.flows.execution_engine.FlowService") as mock_cls:
            mock_service = MagicMock()
            mock_cls.return_value = mock_service

            engine = FlowExecutionEngine()

            mock_cls.assert_called_once()
            assert engine.service == mock_service

    def test_init_custom_service(self):
        """Initialize with custom service."""
        mock_service = MagicMock()

        engine = FlowExecutionEngine(service=mock_service)

        assert engine.service == mock_service

    def test_execute_event_basic(self):
        """Execute event creates execution record."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.flow_version_id = "v1"

        mock_decision = MagicMock()
        mock_decision.flow = mock_flow

        mock_exec = MagicMock()
        mock_exec.id = "exec_456"
        mock_exec.status = FlowExecutionStatus.EM_ANDAMENTO

        mock_service = MagicMock()
        mock_service.record_execution.return_value = mock_exec
        mock_service.list_steps.return_value = []

        engine = FlowExecutionEngine(service=mock_service)
        evento = {"tipo_entrada": "noticia_texto", "id": "item_789"}

        with patch("app.flows.execution_engine.select_flow_for_event", return_value=mock_decision):
            with patch("app.flows.execution_engine.instrumentation") as mock_instr:
                result = engine.execute_event(evento)

        assert result == "exec_456"
        mock_service.record_execution.assert_called_once()
        mock_instr.record_flow_execution_started.assert_called_once_with(mock_exec)

    def test_execute_event_with_steps(self):
        """Execute event processes all steps."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.flow_version_id = "v1"

        mock_decision = MagicMock()
        mock_decision.flow = mock_flow

        mock_exec = MagicMock()
        mock_exec.id = "exec_456"
        mock_exec.status = FlowExecutionStatus.EM_ANDAMENTO

        mock_step = MagicMock()
        mock_step.id = "step_1"
        mock_step.tipo_etapa.value = "INTERPRETACAO"
        mock_step.agent_role = "interpreter"

        mock_step_exec = MagicMock()

        mock_service = MagicMock()
        mock_service.record_execution.return_value = mock_exec
        mock_service.list_steps.return_value = [mock_step]
        mock_service.record_step_execution.return_value = mock_step_exec

        engine = FlowExecutionEngine(service=mock_service)
        evento = {"tipo_entrada": "noticia_texto", "item_id": "item_789"}

        with patch("app.flows.execution_engine.select_flow_for_event", return_value=mock_decision):
            with patch("app.flows.execution_engine.instrumentation") as mock_instr:
                result = engine.execute_event(evento)

        assert result == "exec_456"
        mock_service.record_step_execution.assert_called_once()
        mock_instr.record_flow_step_execution.assert_called_once_with(mock_step_exec)

    def test_execute_event_uses_item_id(self):
        """Execute event uses item_id from evento."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.flow_version_id = "v1"

        mock_decision = MagicMock()
        mock_decision.flow = mock_flow

        mock_exec = MagicMock()
        mock_exec.id = "exec_456"
        mock_exec.status = FlowExecutionStatus.EM_ANDAMENTO

        mock_service = MagicMock()
        mock_service.record_execution.return_value = mock_exec
        mock_service.list_steps.return_value = []

        engine = FlowExecutionEngine(service=mock_service)
        evento = {"tipo_entrada": "noticia_texto", "item_id": "specific_item"}

        with patch("app.flows.execution_engine.select_flow_for_event", return_value=mock_decision):
            with patch("app.flows.execution_engine.instrumentation"):
                engine.execute_event(evento)

        call_args = mock_service.record_execution.call_args
        assert call_args[0][1] == "specific_item"

    def test_execute_event_uses_id_fallback(self):
        """Execute event falls back to id when no item_id."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.flow_version_id = "v1"

        mock_decision = MagicMock()
        mock_decision.flow = mock_flow

        mock_exec = MagicMock()
        mock_exec.id = "exec_456"
        mock_exec.status = FlowExecutionStatus.EM_ANDAMENTO

        mock_service = MagicMock()
        mock_service.record_execution.return_value = mock_exec
        mock_service.list_steps.return_value = []

        engine = FlowExecutionEngine(service=mock_service)
        evento = {"tipo_entrada": "noticia_texto", "id": "fallback_id"}

        with patch("app.flows.execution_engine.select_flow_for_event", return_value=mock_decision):
            with patch("app.flows.execution_engine.instrumentation"):
                engine.execute_event(evento)

        call_args = mock_service.record_execution.call_args
        assert call_args[0][1] == "fallback_id"

    def test_execute_event_uses_unknown_item(self):
        """Execute event uses unknown_item when no id."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.flow_version_id = "v1"

        mock_decision = MagicMock()
        mock_decision.flow = mock_flow

        mock_exec = MagicMock()
        mock_exec.id = "exec_456"
        mock_exec.status = FlowExecutionStatus.EM_ANDAMENTO

        mock_service = MagicMock()
        mock_service.record_execution.return_value = mock_exec
        mock_service.list_steps.return_value = []

        engine = FlowExecutionEngine(service=mock_service)
        evento = {"tipo_entrada": "noticia_texto"}

        with patch("app.flows.execution_engine.select_flow_for_event", return_value=mock_decision):
            with patch("app.flows.execution_engine.instrumentation"):
                engine.execute_event(evento)

        call_args = mock_service.record_execution.call_args
        assert call_args[0][1] == "unknown_item"

    def test_execute_event_completes_successfully(self):
        """Execute event sets CONCLUIDO on success."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_123"
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.flow_version_id = "v1"

        mock_decision = MagicMock()
        mock_decision.flow = mock_flow

        mock_exec = MagicMock()
        mock_exec.id = "exec_456"
        mock_exec.status = FlowExecutionStatus.EM_ANDAMENTO

        mock_service = MagicMock()
        mock_service.record_execution.return_value = mock_exec
        mock_service.list_steps.return_value = []

        engine = FlowExecutionEngine(service=mock_service)
        evento = {"tipo_entrada": "noticia_texto"}

        with patch("app.flows.execution_engine.select_flow_for_event", return_value=mock_decision):
            with patch("app.flows.execution_engine.instrumentation") as mock_instr:
                engine.execute_event(evento)

        mock_service.update_execution_status.assert_called_once()
        call_args = mock_service.update_execution_status.call_args
        assert call_args[0][1] == FlowExecutionStatus.CONCLUIDO
        mock_instr.record_flow_execution_finished.assert_called_once()
