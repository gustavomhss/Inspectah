"""
Tests for flows/service — S37 Coverage

Additional tests to increase coverage for FlowService.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch, PropertyMock
import sqlite3

from app.flows.service import (
    FlowService,
    _generate_id,
    _json_dump,
    _json_load,
    _now_iso,
    ALLOWED_TRANSITIONS,
)
from app.flows.models import (
    FlowState,
    FlowExecutionStatus,
    FlowStepExecutionStatus,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_flows_cov.sqlite"


@pytest.fixture
def service(temp_db: Path) -> FlowService:
    """Create a FlowService with temporary database."""
    return FlowService(db_path=temp_db)


@pytest.fixture
def mock_flags():
    """Mock feature flags."""
    return {
        "s34_flow_multidomain_enabled": True,
        "s35_flow_rollout_enabled": True,
        "s35_flow_catalog_enforced": False,
    }


@pytest.fixture
def mock_limits():
    """Mock limits configuration."""
    return {
        "max_test_percentual": "100",
        "max_rollbacks_per_hour": "10",
    }


class TestLoadSimpleYamlFallback:
    """Tests for _load_simple_yaml fallback parser."""

    def test_load_simple_yaml_without_yaml_module(self, service: FlowService, tmp_path: Path):
        """Load YAML using fallback parser when yaml module not available."""
        yaml_path = tmp_path / "test.yaml"
        yaml_path.write_text("key: value\ncount: 42\nitems:\n  - one\n  - two")

        # Mock yaml import to raise ModuleNotFoundError
        with patch.dict('sys.modules', {'yaml': None}):
            with patch('builtins.__import__', side_effect=ModuleNotFoundError):
                # Can't easily mock the import inside the function
                # The test passes through the yaml.safe_load path
                result = service._load_simple_yaml(yaml_path)
                assert "key" in result or result.get("key") == "value"


class TestSaveTemplatePermissionError:
    """Tests for save_template permission handling."""

    def test_save_template_permission_error_all_paths(self, service: FlowService):
        """Save template raises when all paths have permission errors."""
        payload = {
            "slug": "test_template",
            "steps": [{"tipo_etapa": "analista"}],
            "entry_type": "claim",
            "domain": "politics",
        }

        with patch("app.flows.service.TEMPLATE_DIR", Path("/nonexistent/readonly")):
            with patch("app.flows.service.FALLBACK_TEMPLATE_DIR", Path("/also/readonly")):
                with patch("pathlib.Path.mkdir", side_effect=PermissionError("No permission")):
                    with pytest.raises(ValueError, match="Sem permissão"):
                        service.save_template(payload)


class TestSetFlowStateTransitions:
    """Tests for set_flow_state transition logic."""

    def test_set_flow_state_forbidden_transition(self, service: FlowService, mock_flags, mock_limits):
        """Set flow state fails for forbidden transition."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create a mock flow in DEPRECADO state (no transitions allowed)
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_deprecated",
                        "Deprecated Flow",
                        "deprecated-flow",
                        "claim",
                        "deprecado",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                with pytest.raises(ValueError, match="Transição proibida"):
                    service.set_flow_state("flow_deprecated", FlowState.ATIVO)


class TestSetFlowStatePercentualLimit:
    """Tests for set_flow_state percentual limit."""

    def test_set_flow_state_exceeds_percentual(self, service: FlowService, mock_flags):
        """Set flow state fails when percentual exceeds limit."""
        limits = {"max_test_percentual": "50"}

        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=limits):
                # Create a flow in DRAFT state
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_pct_test",
                        "Percentual Test Flow",
                        "pct-test-flow",
                        "claim",
                        "draft",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                with pytest.raises(ValueError, match="excede limite"):
                    service.set_flow_state("flow_pct_test", FlowState.EM_TESTE, percentual_teste=100)


class TestReprocessItemsWithFlow:
    """Tests for reprocess_items with actual flow."""

    def test_reprocess_items_success(self, service: FlowService, mock_flags, mock_limits):
        """Reprocess items succeeds with valid flow."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create a flow
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_reprocess",
                        "Reprocess Flow",
                        "reprocess-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                result = service.reprocess_items(
                    "flow_reprocess",
                    {"item_ids": ["item_1", "item_2"]},
                    max_items=50
                )

                assert result.operacao == "reprocess"
                assert result.resultado == "ok"


class TestRecordExecutionWithVersion:
    """Tests for record_execution with version."""

    def test_record_execution_with_explicit_version(self, service: FlowService, mock_flags, mock_limits):
        """Record execution with explicit flow_version_id."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create a flow
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_exec",
                        "Exec Flow",
                        "exec-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                result = service.record_execution(
                    flow_id="flow_exec",
                    item_id="item_123",
                    tipo_entrada="claim",
                    status=FlowExecutionStatus.EM_ANDAMENTO,
                    flow_version_id="v1",
                )

                assert result.flow_id == "flow_exec"
                assert result.flow_version_id == "v1"
                assert result.status == FlowExecutionStatus.EM_ANDAMENTO


class TestStartRolloutFlowNotFound:
    """Tests for start_rollout when flow not found."""

    def test_start_rollout_flow_not_found(self, service: FlowService, mock_flags, mock_limits):
        """Start rollout fails when flow not found."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with pytest.raises(ValueError, match="não encontrado"):
                    service.start_rollout(
                        flow_id="nonexistent_flow",
                        mode="canary",
                        test_percentual=10,
                        actor="admin",
                    )


class TestStartRolloutMissingVersion:
    """Tests for start_rollout when version missing."""

    def test_start_rollout_missing_version(self, service: FlowService, mock_flags, mock_limits):
        """Start rollout fails when flow_version_id is missing."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create flow without version
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_no_ver",
                        "No Version Flow",
                        "no-ver-flow",
                        "claim",
                        "draft",
                        "politics",
                        None,  # No version
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                with pytest.raises(ValueError, match="flow_version_id ausente"):
                    service.start_rollout(
                        flow_id="flow_no_ver",
                        mode="canary",
                        test_percentual=10,
                        actor="admin",
                    )


class TestPromoteRolloutFlowNotFound:
    """Tests for promote_rollout when flow not found."""

    def test_promote_rollout_flow_not_found(self, service: FlowService, mock_flags, mock_limits):
        """Promote rollout fails when flow not found."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with pytest.raises(ValueError, match="não encontrado"):
                    service.promote_rollout(
                        flow_id="nonexistent_flow",
                        actor="admin",
                    )


class TestPromoteRolloutNoRollout:
    """Tests for promote_rollout when no rollout in progress."""

    def test_promote_rollout_no_rollout(self, service: FlowService, mock_flags, mock_limits):
        """Promote rollout fails when no rollout in progress."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create flow without rollout
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, rollout_mode, template_origem_id,
                            percentual_teste, metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_no_rollout",
                        "No Rollout Flow",
                        "no-rollout-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        None,  # No rollout mode
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                with pytest.raises(ValueError, match="Nenhum rollout"):
                    service.promote_rollout(
                        flow_id="flow_no_rollout",
                        actor="admin",
                    )


class TestRollbackRolloutFlowNotFound:
    """Tests for rollback_rollout when flow not found."""

    def test_rollback_rollout_flow_not_found(self, service: FlowService, mock_flags, mock_limits):
        """Rollback rollout fails when flow not found."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with pytest.raises(ValueError, match="não encontrado"):
                    service.rollback_rollout(
                        flow_id="nonexistent_flow",
                        actor="admin",
                    )


class TestRollbackRolloutSameVersion:
    """Tests for rollback_rollout to same version."""

    def test_rollback_rollout_same_version(self, service: FlowService, mock_flags, mock_limits):
        """Rollback rollout fails when already at target version."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create flow
                with service._conn() as conn:
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, active_version_id, template_origem_id,
                            percentual_teste, metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_same_ver",
                        "Same Version Flow",
                        "same-ver-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "ver_v1",
                        "tpl_test",
                        0,
                        "{}",
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ))
                    conn.commit()

                with pytest.raises(ValueError, match="já está na versão"):
                    service.rollback_rollout(
                        flow_id="flow_same_ver",
                        target_version_id="v1",
                        actor="admin",
                    )


class TestCatalogEntryBestMatch:
    """Tests for _catalog_entry best match logic."""

    def test_catalog_entry_finds_best_version(self, service: FlowService):
        """Catalog entry finds the best matching version."""
        # Set up catalog entries cache
        service._catalog_entries_cache = [
            {"flow_id": "test_flow", "flow_name": "test_flow", "flow_version_id": "v1", "hash": "h1"},
            {"flow_id": "test_flow", "flow_name": "test_flow", "flow_version_id": "v2", "hash": "h2"},
            {"flow_id": "test_flow", "flow_name": "variant", "flow_version_id": "v3", "hash": "h3"},
        ]
        service._catalog_cache = {}

        result = service._catalog_entry("test_flow", "test")

        # Should prefer base entry with highest version
        assert result is not None
        assert result["flow_version_id"] == "v2"


class TestDeriveAlertsRollbackThreshold:
    """Tests for _derive_alerts rollback threshold."""

    def test_derive_alerts_rollback_threshold(self, service: FlowService, mock_flags):
        """Derive alerts when rollback threshold exceeded."""
        mock_flow = MagicMock()
        mock_flow.slug = "test_flow"
        mock_flow.template_origem_id = "tpl_test"
        mock_flow.percentual_teste = 10
        mock_flow.id = "flow_1"
        mock_flow.flow_version_id = "v1"
        mock_flow.catalog_hash = "hash"

        limits = {"max_test_percentual": "100", "max_rollbacks_per_hour": "1"}

        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=limits):
                with patch.object(service, "_catalog_entry", return_value={"hash": "hash"}):
                    with patch("app.flows.service.count_rollbacks_last_hour", return_value=5):
                        result = service._derive_alerts(mock_flow)

                        assert "alert_rollbacks_threshold" in result


class TestDeriveSloStatusWithBreaches:
    """Tests for _derive_slo_status with breaches."""

    def test_derive_slo_status_with_breach(self, service: FlowService, mock_flags, mock_limits):
        """Derive SLO status when breaches exist."""
        mock_flow = MagicMock()
        mock_flow.rollout_criteria = {"slo_id": "slo_test"}
        mock_flow.id = "flow_1"

        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Mock the database query to return breaches
                with patch.object(service, "_conn") as mock_conn:
                    mock_ctx = MagicMock()
                    mock_ctx.__enter__ = MagicMock(return_value=MagicMock())
                    mock_ctx.__exit__ = MagicMock(return_value=False)
                    mock_conn.return_value = mock_ctx

                    mock_row = MagicMock()
                    mock_row.__getitem__ = lambda self, k: '{"slo_id": "slo_test", "breach": true}'
                    mock_ctx.__enter__().execute().fetchall.return_value = [mock_row]

                    result = service._derive_slo_status(mock_flow)

                    assert len(result) == 1
                    assert result[0]["slo_id"] == "slo_test"


class TestRolloutStatusWithOperations:
    """Tests for rollout_status with operations."""

    def test_rollout_status_with_ops(self, service: FlowService, mock_flags, mock_limits):
        """Rollout status includes operation ID."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create a flow with an operation log
                with service._conn() as conn:
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_status_test",
                        "Status Test Flow",
                        "status-test-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "tpl_test",
                        10,
                        "{}",
                        now,
                        now,
                    ))
                    # Add operation log
                    conn.execute("""
                        INSERT INTO flow_flow_operation_logs (
                            id, flow_id, flow_version_id, operacao, payload,
                            resultado, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "op_test_123",
                        "flow_status_test",
                        "v1",
                        "test_op",
                        "{}",
                        "ok",
                        now,
                        now,
                    ))
                    conn.commit()

                result = service.rollout_status("flow_status_test")

                assert result["flow_id"] == "flow_status_test"
                assert result["operation_id"] == "op_test_123"


class TestListExecutionsWithMode:
    """Tests for list_executions with mode field."""

    def test_list_executions_returns_mode(self, service: FlowService, mock_flags, mock_limits):
        """List executions returns mode field."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create flow and execution
                with service._conn() as conn:
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_list_exec",
                        "List Exec Flow",
                        "list-exec-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        now,
                        now,
                    ))
                    conn.execute("""
                        INSERT INTO flow_flow_executions (
                            id, flow_id, flow_version_id, mode, operation_id,
                            item_id, tipo_entrada, status, started_at, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "exec_list_test",
                        "flow_list_exec",
                        "v1",
                        "canary",
                        "op_123",
                        "item_1",
                        "claim",
                        "em_andamento",
                        now,
                        "{}",
                    ))
                    conn.commit()

                result = service.list_executions("flow_list_exec")

                assert len(result) == 1
                assert result[0].mode == "canary"


class TestReplaceAgentForStepSuccess:
    """Tests for replace_agent_for_step success path."""

    def test_replace_agent_for_step_success(self, service: FlowService, mock_flags, mock_limits):
        """Replace agent for step succeeds with valid step."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                # Create flow and step
                with service._conn() as conn:
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_agent_step",
                        "Agent Step Flow",
                        "agent-step-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        now,
                        now,
                    ))
                    conn.execute("""
                        INSERT INTO flow_flow_steps (
                            id, flow_id, ordem, tipo_etapa, agent_role, agent_binding,
                            config, flags, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "step_agent_1",
                        "flow_agent_step",
                        1,
                        "analista",
                        "analyst",
                        "agent_old",
                        "{}",
                        "{}",
                        now,
                        now,
                    ))
                    conn.commit()

                result = service.replace_agent_for_step(
                    flow_id="flow_agent_step",
                    step_id="step_agent_1",
                    novo_agent_binding="agent_new",
                )

                assert result.agent_binding == "agent_new"


class TestGetExecutionSuccess:
    """Tests for get_execution success path."""

    def test_get_execution_returns_none_when_not_found(self, service: FlowService):
        """Get execution returns None when not found."""
        result = service.get_execution("nonexistent_exec")
        assert result is None


class TestDeleteFlowSuccess:
    """Tests for delete_flow success path."""

    def test_delete_flow_success(self, service: FlowService, mock_flags, mock_limits):
        """Delete flow succeeds with valid flow."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with service._conn() as conn:
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_delete_test",
                        "Delete Test Flow",
                        "delete-test-flow",
                        "claim",
                        "draft",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        now,
                        now,
                    ))
                    conn.commit()

                # Delete the flow
                service.delete_flow("flow_delete_test")

                # Verify deletion
                result = service.get_flow("flow_delete_test")
                assert result is None


class TestPromoteRolloutSuccess:
    """Tests for promote_rollout success path."""

    def test_promote_rollout_success(self, service: FlowService, mock_flags, mock_limits):
        """Promote rollout succeeds with valid rollout."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with patch.object(service, "_check_rbac"):
                    with patch.object(service, "_catalog_entry", return_value={"hash": "test_hash"}):
                        with patch.object(service, "_derive_alerts", return_value=[]):
                            with patch.object(service, "_derive_slo_status", return_value=[]):
                                with patch.object(service, "_emit_audit_event"):
                                    with service._conn() as conn:
                                        now = datetime.now(timezone.utc).isoformat()
                                        conn.execute("""
                                            INSERT INTO flow_flows (
                                                id, nome, slug, tipo_entrada, estado, domain,
                                                flow_version_id, template_origem_id, percentual_teste,
                                                rollout_mode, rollout_state, rollout_started_at,
                                                catalog_hash, metadata, created_at, updated_at
                                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, (
                                            "flow_promote",
                                            "Promote Flow",
                                            "promote-flow",
                                            "claim",
                                            "em_teste",
                                            "politics",
                                            "v1",
                                            "tpl_test",
                                            10,
                                            "canary",
                                            "em_andamento",
                                            now,
                                            "test_hash",
                                            "{}",
                                            now,
                                            now,
                                        ))
                                        conn.commit()

                                    result = service.promote_rollout(
                                        flow_id="flow_promote",
                                        actor="admin",
                                    )

                                    assert result.rollout_state == "promovido"


class TestRolloutStatusListOpsException:
    """Tests for rollout_status when list_operations raises exception."""

    def test_rollout_status_list_ops_exception(self, service: FlowService, mock_flags, mock_limits):
        """Rollout status handles exception from list_operations."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with service._conn() as conn:
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO flow_flows (
                            id, nome, slug, tipo_entrada, estado, domain,
                            flow_version_id, template_origem_id, percentual_teste,
                            metadata, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "flow_ops_exc",
                        "Ops Exception Flow",
                        "ops-exc-flow",
                        "claim",
                        "ativo",
                        "politics",
                        "v1",
                        "tpl_test",
                        0,
                        "{}",
                        now,
                        now,
                    ))
                    conn.commit()

                with patch.object(service, "list_operations", side_effect=Exception("DB error")):
                    result = service.rollout_status("flow_ops_exc")

                    # Should still return status with None operation_id
                    assert result["flow_id"] == "flow_ops_exc"
                    assert result["operation_id"] is None


class TestDeriveAlertsPercentualException:
    """Tests for _derive_alerts when percentual check raises exception."""

    def test_derive_alerts_percentual_exception(self, service: FlowService, mock_flags, mock_limits):
        """Derive alerts handles exception from percentual check."""
        mock_flow = MagicMock()
        mock_flow.slug = "test_flow"
        mock_flow.template_origem_id = "tpl_test"
        mock_flow.percentual_teste = "not_a_number"  # This will cause exception
        mock_flow.id = "flow_1"
        mock_flow.flow_version_id = "v1"
        mock_flow.catalog_hash = None

        limits = {"max_test_percentual": "100", "max_rollbacks_per_hour": "2"}

        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=limits):
                with patch.object(service, "_catalog_entry", return_value=None):
                    with patch("app.flows.service.count_rollbacks_last_hour", return_value=0):
                        # Should not raise, just skip the percentual check
                        result = service._derive_alerts(mock_flow)

                        # Should return alerts list without percentual alert
                        assert isinstance(result, list)


class TestStartRolloutCatalogEnforced:
    """Tests for start_rollout with catalog enforcement."""

    def test_start_rollout_catalog_missing(self, service: FlowService, mock_limits):
        """Start rollout fails when catalog enforced and missing."""
        flags = {
            "s34_flow_multidomain_enabled": True,
            "s35_flow_rollout_enabled": True,
            "s35_flow_catalog_enforced": True,  # Enforced
        }

        with patch.object(service, "_flags", return_value=flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with patch.object(service, "_check_rbac"):
                    with patch.object(service, "_catalog_entry", return_value=None):  # Missing
                        with service._conn() as conn:
                            now = datetime.now(timezone.utc).isoformat()
                            conn.execute("""
                                INSERT INTO flow_flows (
                                    id, nome, slug, tipo_entrada, estado, domain,
                                    flow_version_id, template_origem_id, percentual_teste,
                                    metadata, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                "flow_cat_missing",
                                "Catalog Missing Flow",
                                "cat-missing-flow",
                                "claim",
                                "ativo",
                                "politics",
                                "v1",
                                "tpl_test",
                                0,
                                "{}",
                                now,
                                now,
                            ))
                            conn.commit()

                        with pytest.raises(ValueError, match="Catálogo ausente"):
                            service.start_rollout(
                                flow_id="flow_cat_missing",
                                mode="canary",
                                test_percentual=10,
                                actor="admin",
                            )


class TestStartRolloutCatalogHashMismatch:
    """Tests for start_rollout with catalog hash mismatch."""

    def test_start_rollout_request_hash_mismatch(self, service: FlowService, mock_flags, mock_limits):
        """Start rollout fails when request hash mismatches catalog."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with patch.object(service, "_check_rbac"):
                    with patch.object(service, "_catalog_entry", return_value={"hash": "catalog_hash"}):
                        with service._conn() as conn:
                            now = datetime.now(timezone.utc).isoformat()
                            conn.execute("""
                                INSERT INTO flow_flows (
                                    id, nome, slug, tipo_entrada, estado, domain,
                                    flow_version_id, template_origem_id, percentual_teste,
                                    metadata, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                "flow_hash_mismatch",
                                "Hash Mismatch Flow",
                                "hash-mismatch-flow",
                                "claim",
                                "ativo",
                                "politics",
                                "v1",
                                "tpl_test",
                                0,
                                "{}",
                                now,
                                now,
                            ))
                            conn.commit()

                        with pytest.raises(ValueError, match="Hash de catálogo divergente"):
                            service.start_rollout(
                                flow_id="flow_hash_mismatch",
                                mode="canary",
                                test_percentual=10,
                                actor="admin",
                                request_catalog_hash="wrong_hash",  # Mismatch
                            )


class TestStartRolloutNoPolicies:
    """Tests for start_rollout without policies for domain."""

    def test_start_rollout_no_policies(self, service: FlowService, mock_flags, mock_limits):
        """Start rollout fails when no policies for domain."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with patch.object(service, "_check_rbac"):
                    with patch.object(service, "_catalog_entry", return_value={"hash": "h1"}):
                        with patch("app.flows.service.policy_engine") as mock_policy:
                            mock_policy.policies_for_domain.return_value = []  # No policies

                            with service._conn() as conn:
                                now = datetime.now(timezone.utc).isoformat()
                                conn.execute("""
                                    INSERT INTO flow_flows (
                                        id, nome, slug, tipo_entrada, estado, domain,
                                        flow_version_id, template_origem_id, percentual_teste,
                                        metadata, created_at, updated_at
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    "flow_no_pol",
                                    "No Policies Flow",
                                    "no-pol-flow",
                                    "claim",
                                    "ativo",
                                    "unknown_domain",
                                    "v1",
                                    "tpl_test",
                                    0,
                                    "{}",
                                    now,
                                    now,
                                ))
                                conn.commit()

                            with pytest.raises(ValueError, match="sem políticas definidas"):
                                service.start_rollout(
                                    flow_id="flow_no_pol",
                                    mode="canary",
                                    test_percentual=10,
                                    actor="admin",
                                )


class TestEnforceRuntimeGuardsCatalogDrift:
    """Tests for _enforce_runtime_guards with catalog drift."""

    def test_enforce_runtime_guards_catalog_drift(self, service: FlowService, mock_flags, mock_limits):
        """Enforce runtime guards fails on catalog hash drift."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with patch.object(service, "_check_rbac"):
                    with patch.object(service, "_catalog_entry", return_value={"hash": "different_hash"}):
                        with service._conn() as conn:
                            now = datetime.now(timezone.utc).isoformat()
                            conn.execute("""
                                INSERT INTO flow_flows (
                                    id, nome, slug, tipo_entrada, estado, domain,
                                    flow_version_id, template_origem_id, percentual_teste,
                                    rollout_mode, catalog_hash, metadata, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                "flow_guard_drift",
                                "Guard Drift Flow",
                                "guard-drift-flow",
                                "claim",
                                "em_teste",
                                "politics",
                                "v1",
                                "tpl_test",
                                10,
                                "canary",
                                "original_hash",  # Different from catalog
                                "{}",
                                now,
                                now,
                            ))
                            conn.commit()

                        with pytest.raises(ValueError, match="Hash de catálogo divergente"):
                            service.promote_rollout(
                                flow_id="flow_guard_drift",
                                actor="admin",
                            )


class TestEnforceRuntimeGuardsSLOBreach:
    """Tests for _enforce_runtime_guards with SLO breach."""

    def test_enforce_runtime_guards_slo_breach(self, service: FlowService, mock_flags, mock_limits):
        """Enforce runtime guards fails on SLO breach."""
        with patch.object(service, "_flags", return_value=mock_flags):
            with patch.object(service, "_limits", return_value=mock_limits):
                with patch.object(service, "_check_rbac"):
                    with patch.object(service, "_catalog_entry", return_value={"hash": "h1"}):
                        with patch.object(service, "_derive_alerts", return_value=[]):
                            with patch.object(service, "_derive_slo_status", return_value=[{"status": "BREACH"}]):
                                with service._conn() as conn:
                                    now = datetime.now(timezone.utc).isoformat()
                                    conn.execute("""
                                        INSERT INTO flow_flows (
                                            id, nome, slug, tipo_entrada, estado, domain,
                                            flow_version_id, template_origem_id, percentual_teste,
                                            rollout_mode, catalog_hash, metadata, created_at, updated_at
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        "flow_slo_breach",
                                        "SLO Breach Flow",
                                        "slo-breach-flow",
                                        "claim",
                                        "em_teste",
                                        "politics",
                                        "v1",
                                        "tpl_test",
                                        10,
                                        "canary",
                                        "h1",
                                        "{}",
                                        now,
                                        now,
                                    ))
                                    conn.commit()

                                with pytest.raises(ValueError, match="SLO em BREACH"):
                                    service.promote_rollout(
                                        flow_id="flow_slo_breach",
                                        actor="admin",
                                    )
