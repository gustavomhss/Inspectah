"""
Tests for flows/instrumentation — S37

Tests for flow execution metrics and logging.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from app.flows.instrumentation import (
    _duration_seconds,
    record_flow_execution_started,
    record_flow_execution_finished,
    record_flow_step_execution,
    record_policy_violation,
    record_rollback,
    record_slo_breach,
    record_rollout_request,
    record_rollout_success,
    record_rollout_rollback,
    record_catalog_drift,
    record_catalog_mismatch,
)
from app.flows.models import FlowExecution, FlowStepExecution, FlowExecutionStatus, FlowStepExecutionStatus


class TestDurationSeconds:
    """Tests for _duration_seconds function."""

    def test_duration_seconds_with_both_times(self):
        """Calculate duration with start and end times."""
        started = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        finished = datetime(2024, 1, 1, 12, 0, 30, tzinfo=timezone.utc)

        result = _duration_seconds(started, finished)

        assert result == 30.0

    def test_duration_seconds_with_none_finished(self):
        """Return None when finished_at is None."""
        started = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = _duration_seconds(started, None)

        assert result is None

    def test_duration_seconds_fractional(self):
        """Calculate fractional seconds."""
        started = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
        finished = datetime(2024, 1, 1, 12, 0, 1, 500000, tzinfo=timezone.utc)

        result = _duration_seconds(started, finished)

        assert result == 1.5


class TestRecordFlowExecutionStarted:
    """Tests for record_flow_execution_started."""

    def test_record_flow_execution_started_logs(self):
        """Log flow execution start."""
        execution = FlowExecution(
            id="exec_1",
            flow_id="flow_1",
            flow_version_id="v1",
            mode="test",
            operation_id="op_1",
            item_id="item_1",
            tipo_entrada="news",
            status=FlowExecutionStatus.EM_ANDAMENTO,
            started_at=datetime.now(timezone.utc),
        )

        with patch("app.flows.instrumentation.logger") as mock_logger:
            record_flow_execution_started(execution)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "flow_execution_started"
            assert call_args[1]["extra"]["flow_id"] == "flow_1"


class TestRecordFlowExecutionFinished:
    """Tests for record_flow_execution_finished."""

    def test_record_flow_execution_finished_success(self):
        """Record successful flow execution."""
        started = datetime.now(timezone.utc)
        finished = started + timedelta(seconds=5)
        execution = FlowExecution(
            id="exec_1",
            flow_id="flow_1",
            flow_version_id="v1",
            mode="test",
            operation_id="op_1",
            item_id="item_1",
            tipo_entrada="news",
            status=FlowExecutionStatus.CONCLUIDO,
            started_at=started,
            finished_at=finished,
        )

        with patch("app.flows.instrumentation._exec_total") as mock_total:
            with patch("app.flows.instrumentation._exec_success") as mock_success:
                with patch("app.flows.instrumentation._exec_latency") as mock_latency:
                    mock_total.labels.return_value = MagicMock()
                    mock_success.labels.return_value = MagicMock()
                    mock_latency.labels.return_value = MagicMock()

                    record_flow_execution_finished(execution)

                    mock_total.labels.assert_called()
                    mock_success.labels.assert_called()
                    mock_latency.labels.return_value.observe.assert_called_with(5.0)

    def test_record_flow_execution_finished_failure(self):
        """Record failed flow execution."""
        execution = FlowExecution(
            id="exec_1",
            flow_id="flow_1",
            flow_version_id="v1",
            mode="test",
            operation_id="op_1",
            item_id="item_1",
            tipo_entrada="news",
            status=FlowExecutionStatus.FALHOU,
            started_at=datetime.now(timezone.utc),
            erro_resumo="Test error",
        )

        with patch("app.flows.instrumentation._exec_total") as mock_total:
            with patch("app.flows.instrumentation._exec_failure") as mock_failure:
                mock_total.labels.return_value = MagicMock()
                mock_failure.labels.return_value = MagicMock()

                record_flow_execution_finished(execution)

                mock_failure.labels.assert_called()

    def test_record_flow_execution_finished_no_finished_at(self):
        """Record execution without finished_at."""
        execution = FlowExecution(
            id="exec_1",
            flow_id="flow_1",
            flow_version_id=None,
            mode=None,
            operation_id="op_1",
            item_id="item_1",
            tipo_entrada="news",
            status=FlowExecutionStatus.FALHOU,
            started_at=datetime.now(timezone.utc),
            finished_at=None,
        )

        with patch("app.flows.instrumentation._exec_total") as mock_total:
            with patch("app.flows.instrumentation._exec_failure") as mock_failure:
                with patch("app.flows.instrumentation._exec_latency") as mock_latency:
                    mock_total.labels.return_value = MagicMock()
                    mock_failure.labels.return_value = MagicMock()

                    record_flow_execution_finished(execution)

                    mock_latency.labels.return_value.observe.assert_not_called()


class TestRecordFlowStepExecution:
    """Tests for record_flow_step_execution."""

    def test_record_flow_step_execution(self):
        """Record step execution logs."""
        step = FlowStepExecution(
            id="step_1",
            flow_execution_id="exec_1",
            step_id="step_a",
            status=FlowStepExecutionStatus.OK,
            output_resumo="Output",
            erro_resumo=None,
            started_at=datetime.now(timezone.utc),
        )

        with patch("app.flows.instrumentation.logger") as mock_logger:
            record_flow_step_execution(step)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "flow_step_execution"


class TestRecordPolicyViolation:
    """Tests for record_policy_violation."""

    def test_record_policy_violation(self):
        """Record policy violation."""
        with patch("app.flows.instrumentation._policy_violations") as mock_pv:
            with patch("app.flows.instrumentation._policy_violations_rollout") as mock_pvr:
                mock_pv.labels.return_value = MagicMock()
                mock_pvr.labels.return_value = MagicMock()

                record_policy_violation("flow_1", "v1", "test")

                mock_pv.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1")
                mock_pvr.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1", mode="test")

    def test_record_policy_violation_none_values(self):
        """Record policy violation with None values."""
        with patch("app.flows.instrumentation._policy_violations") as mock_pv:
            with patch("app.flows.instrumentation._policy_violations_rollout") as mock_pvr:
                mock_pv.labels.return_value = MagicMock()
                mock_pvr.labels.return_value = MagicMock()

                record_policy_violation("flow_1", None, None)

                mock_pv.labels.assert_called_with(flow_id="flow_1", flow_version_id="unknown")
                mock_pvr.labels.assert_called_with(flow_id="flow_1", flow_version_id="unknown", mode="unknown")


class TestRecordRollback:
    """Tests for record_rollback."""

    def test_record_rollback(self):
        """Record rollback."""
        with patch("app.flows.instrumentation._rollbacks") as mock_rb:
            with patch("app.flows.instrumentation.logger") as mock_logger:
                mock_rb.labels.return_value = MagicMock()

                record_rollback("flow_1", "v1", "op_1")

                mock_rb.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1")
                mock_logger.info.assert_called()


class TestRecordSLOBreach:
    """Tests for record_slo_breach."""

    def test_record_slo_breach(self):
        """Record SLO breach."""
        with patch("app.flows.instrumentation._slo_breaches") as mock_slo:
            with patch("app.flows.instrumentation.logger") as mock_logger:
                mock_slo.labels.return_value = MagicMock()

                record_slo_breach("flow_1", "v1", "slo_latency")

                mock_slo.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1", slo_id="slo_latency")
                mock_logger.warning.assert_called()


class TestRecordRolloutRequest:
    """Tests for record_rollout_request."""

    def test_record_rollout_request(self):
        """Record rollout request."""
        with patch("app.flows.instrumentation._rollout_requests") as mock_rr:
            with patch("app.flows.instrumentation.logger") as mock_logger:
                mock_rr.labels.return_value = MagicMock()

                record_rollout_request("flow_1", "v1", "canary")

                mock_rr.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1", mode="canary")
                mock_logger.info.assert_called()


class TestRecordRolloutSuccess:
    """Tests for record_rollout_success."""

    def test_record_rollout_success_with_duration(self):
        """Record rollout success with duration."""
        with patch("app.flows.instrumentation._rollout_success") as mock_rs:
            with patch("app.flows.instrumentation._rollout_duration") as mock_rd:
                with patch("app.flows.instrumentation.logger") as mock_logger:
                    mock_rs.labels.return_value = MagicMock()
                    mock_rd.labels.return_value = MagicMock()

                    record_rollout_success("flow_1", "v1", "canary", 10.5)

                    mock_rs.labels.assert_called()
                    mock_rd.labels.return_value.observe.assert_called_with(10.5)
                    mock_logger.info.assert_called()

    def test_record_rollout_success_without_duration(self):
        """Record rollout success without duration."""
        with patch("app.flows.instrumentation._rollout_success") as mock_rs:
            with patch("app.flows.instrumentation._rollout_duration") as mock_rd:
                mock_rs.labels.return_value = MagicMock()
                mock_rd.labels.return_value = MagicMock()

                record_rollout_success("flow_1", "v1", "canary", None)

                mock_rd.labels.return_value.observe.assert_not_called()


class TestRecordRolloutRollback:
    """Tests for record_rollout_rollback."""

    def test_record_rollout_rollback(self):
        """Record rollout rollback."""
        with patch("app.flows.instrumentation._rollout_rollbacks") as mock_rrb:
            with patch("app.flows.instrumentation.logger") as mock_logger:
                mock_rrb.labels.return_value = MagicMock()

                record_rollout_rollback("flow_1", "v1", "canary")

                mock_rrb.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1", mode="canary")
                mock_logger.info.assert_called()

    def test_record_rollout_rollback_none_values(self):
        """Record rollout rollback with None values."""
        with patch("app.flows.instrumentation._rollout_rollbacks") as mock_rrb:
            mock_rrb.labels.return_value = MagicMock()

            record_rollout_rollback("flow_1", None, None)

            mock_rrb.labels.assert_called_with(flow_id="flow_1", flow_version_id="unknown", mode="unknown")


class TestRecordCatalogDrift:
    """Tests for record_catalog_drift."""

    def test_record_catalog_drift(self):
        """Record catalog drift."""
        with patch("app.flows.instrumentation._rollout_catalog_drift") as mock_cd:
            with patch("app.flows.instrumentation.logger") as mock_logger:
                mock_cd.labels.return_value = MagicMock()

                record_catalog_drift("flow_1", "v1")

                mock_cd.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1")
                mock_logger.warning.assert_called()


class TestRecordCatalogMismatch:
    """Tests for record_catalog_mismatch."""

    def test_record_catalog_mismatch(self):
        """Record catalog mismatch."""
        with patch("app.flows.instrumentation._rollout_catalog_mismatch") as mock_cm:
            with patch("app.flows.instrumentation.logger") as mock_logger:
                mock_cm.labels.return_value = MagicMock()

                record_catalog_mismatch("flow_1", "v1", "canary")

                mock_cm.labels.assert_called_with(flow_id="flow_1", flow_version_id="v1", mode="canary")
                mock_logger.warning.assert_called()

    def test_record_catalog_mismatch_none_values(self):
        """Record catalog mismatch with None values."""
        with patch("app.flows.instrumentation._rollout_catalog_mismatch") as mock_cm:
            mock_cm.labels.return_value = MagicMock()

            record_catalog_mismatch("flow_1", None, None)

            mock_cm.labels.assert_called_with(flow_id="flow_1", flow_version_id="unknown", mode="unknown")
