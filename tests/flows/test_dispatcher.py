"""
Tests for Flows Dispatcher — S37

Tests for flow event dispatcher.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from tempfile import NamedTemporaryFile

from app.flows.dispatcher import (
    _ensure_flow_active,
    _load_events,
    dispatch_events,
    dispatch_file,
)
from app.flows.models import FlowState


class TestEnsureFlowActive:
    """Tests for _ensure_flow_active function."""

    def test_flow_already_active(self):
        """Does nothing when flow already active."""
        mock_flow = MagicMock()
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.estado = FlowState.ATIVO

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_flow]

        _ensure_flow_active(mock_service)

        mock_service.create_flow_from_template.assert_not_called()

    def test_creates_flow_when_none_active(self):
        """Creates flow when none active."""
        mock_new_flow = MagicMock()
        mock_new_flow.id = "new_flow_123"

        mock_service = MagicMock()
        mock_service.list_flows.return_value = []
        mock_service.create_flow_from_template.return_value = mock_new_flow

        _ensure_flow_active(mock_service)

        mock_service.create_flow_from_template.assert_called_once_with(
            "fluxo_noticias_geral_v1",
            "Fluxo Noticias E2E",
            "fluxo_noticias_e2e",
            {},
        )
        assert mock_service.set_flow_state.call_count == 2

    def test_ignores_wrong_tipo_entrada(self):
        """Ignores flows with wrong tipo_entrada."""
        mock_flow = MagicMock()
        mock_flow.tipo_entrada = "outro_tipo"
        mock_flow.estado = FlowState.ATIVO

        mock_new_flow = MagicMock()
        mock_new_flow.id = "new_flow_123"

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_flow]
        mock_service.create_flow_from_template.return_value = mock_new_flow

        _ensure_flow_active(mock_service)

        mock_service.create_flow_from_template.assert_called_once()

    def test_ignores_inactive_flows(self):
        """Ignores flows that are not active."""
        mock_flow = MagicMock()
        mock_flow.tipo_entrada = "noticia_texto"
        mock_flow.estado = FlowState.EM_TESTE

        mock_new_flow = MagicMock()
        mock_new_flow.id = "new_flow_123"

        mock_service = MagicMock()
        mock_service.list_flows.return_value = [mock_flow]
        mock_service.create_flow_from_template.return_value = mock_new_flow

        _ensure_flow_active(mock_service)

        mock_service.create_flow_from_template.assert_called_once()


class TestLoadEvents:
    """Tests for _load_events function."""

    def test_load_events_from_file(self, tmp_path):
        """Load events from JSONL file."""
        events_file = tmp_path / "events.jsonl"
        events_file.write_text(
            '{"id": "1", "type": "noticia"}\n'
            '{"id": "2", "type": "noticia"}\n',
            encoding="utf-8",
        )

        events = _load_events(events_file)

        assert len(events) == 2
        assert events[0]["id"] == "1"
        assert events[1]["id"] == "2"

    def test_load_events_skips_empty_lines(self, tmp_path):
        """Skips empty lines."""
        events_file = tmp_path / "events.jsonl"
        events_file.write_text(
            '{"id": "1"}\n'
            "\n"
            '{"id": "2"}\n'
            "   \n",
            encoding="utf-8",
        )

        events = _load_events(events_file)

        assert len(events) == 2

    def test_load_events_empty_file(self, tmp_path):
        """Returns empty list for empty file."""
        events_file = tmp_path / "events.jsonl"
        events_file.write_text("", encoding="utf-8")

        events = _load_events(events_file)

        assert events == []


class TestDispatchEvents:
    """Tests for dispatch_events function."""

    def test_dispatch_events_returns_exec_ids(self):
        """Dispatch events returns execution IDs."""
        mock_engine = MagicMock()
        mock_engine.execute_event.side_effect = ["exec_1", "exec_2"]

        events = [{"id": "1"}, {"id": "2"}]

        with patch("app.flows.dispatcher.FlowService"):
            with patch("app.flows.dispatcher._ensure_flow_active"):
                with patch("app.flows.dispatcher.FlowExecutionEngine", return_value=mock_engine):
                    result = dispatch_events(events)

        assert result == ["exec_1", "exec_2"]
        assert mock_engine.execute_event.call_count == 2

    def test_dispatch_events_empty_list(self):
        """Dispatch empty list returns empty list."""
        mock_engine = MagicMock()

        with patch("app.flows.dispatcher.FlowService"):
            with patch("app.flows.dispatcher._ensure_flow_active"):
                with patch("app.flows.dispatcher.FlowExecutionEngine", return_value=mock_engine):
                    result = dispatch_events([])

        assert result == []
        mock_engine.execute_event.assert_not_called()


class TestDispatchFile:
    """Tests for dispatch_file function."""

    def test_dispatch_file(self, tmp_path):
        """Dispatch file loads and dispatches events."""
        events_file = tmp_path / "events.jsonl"
        events_file.write_text('{"id": "1"}\n{"id": "2"}\n', encoding="utf-8")

        mock_engine = MagicMock()
        mock_engine.execute_event.side_effect = ["exec_1", "exec_2"]

        with patch("app.flows.dispatcher.FlowService"):
            with patch("app.flows.dispatcher._ensure_flow_active"):
                with patch("app.flows.dispatcher.FlowExecutionEngine", return_value=mock_engine):
                    result = dispatch_file(str(events_file))

        assert result == ["exec_1", "exec_2"]
