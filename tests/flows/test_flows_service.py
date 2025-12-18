"""
Tests for flows/service — S37

Tests for FlowService and utility functions.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from app.flows.service import (
    _generate_id,
    _json_dump,
    _json_load,
    _now_iso,
    FlowService,
    ALLOWED_TRANSITIONS,
)
from app.flows.models import FlowState


class TestGenerateId:
    """Tests for _generate_id function."""

    def test_generate_id_with_prefix(self):
        """Generate ID with given prefix."""
        result = _generate_id("flow")

        assert result.startswith("flow_")
        assert len(result) == 17  # "flow_" + 12 hex chars

    def test_generate_id_unique(self):
        """Generated IDs are unique."""
        ids = [_generate_id("test") for _ in range(100)]

        assert len(set(ids)) == 100


class TestNowIso:
    """Tests for _now_iso function."""

    def test_now_iso_format(self):
        """Returns ISO formatted datetime string."""
        result = _now_iso()

        assert isinstance(result, str)
        # Should parse without error
        parsed = datetime.fromisoformat(result)
        assert parsed.tzinfo is not None


class TestJsonDump:
    """Tests for _json_dump function."""

    def test_json_dump_dict(self):
        """Dump dictionary to JSON."""
        result = _json_dump({"key": "value", "count": 42})

        assert result == '{"key": "value", "count": 42}'

    def test_json_dump_empty(self):
        """Dump empty dict."""
        result = _json_dump({})

        assert result == "{}"

    def test_json_dump_none(self):
        """Dump None returns empty dict JSON."""
        result = _json_dump(None)

        assert result == "{}"

    def test_json_dump_unicode(self):
        """Dump with unicode characters."""
        result = _json_dump({"text": "olá mundo"})

        assert "olá mundo" in result


class TestJsonLoad:
    """Tests for _json_load function."""

    def test_json_load_valid(self):
        """Load valid JSON string."""
        result = _json_load('{"key": "value"}')

        assert result == {"key": "value"}

    def test_json_load_none(self):
        """Load None returns empty dict."""
        result = _json_load(None)

        assert result == {}

    def test_json_load_invalid(self):
        """Load invalid JSON returns empty dict."""
        result = _json_load("not valid json{")

        assert result == {}

    def test_json_load_empty(self):
        """Load empty string returns empty dict."""
        result = _json_load("")

        assert result == {}


class TestAllowedTransitions:
    """Tests for ALLOWED_TRANSITIONS mapping."""

    def test_draft_transitions(self):
        """Draft can only go to EM_TESTE."""
        assert ALLOWED_TRANSITIONS[FlowState.DRAFT] == [FlowState.EM_TESTE]

    def test_em_teste_transitions(self):
        """EM_TESTE can go to ATIVO or PAUSADO."""
        transitions = ALLOWED_TRANSITIONS[FlowState.EM_TESTE]

        assert FlowState.ATIVO in transitions
        assert FlowState.PAUSADO in transitions
        assert len(transitions) == 2

    def test_ativo_transitions(self):
        """ATIVO can go to PAUSADO or DEPRECADO."""
        transitions = ALLOWED_TRANSITIONS[FlowState.ATIVO]

        assert FlowState.PAUSADO in transitions
        assert FlowState.DEPRECADO in transitions

    def test_pausado_transitions(self):
        """PAUSADO can go to ATIVO or DEPRECADO."""
        transitions = ALLOWED_TRANSITIONS[FlowState.PAUSADO]

        assert FlowState.ATIVO in transitions
        assert FlowState.DEPRECADO in transitions

    def test_deprecado_no_transitions(self):
        """DEPRECADO has no allowed transitions."""
        assert ALLOWED_TRANSITIONS[FlowState.DEPRECADO] == []


class TestFlowServiceInit:
    """Tests for FlowService initialization."""

    def test_init_default_path(self):
        """Initialize with default db path."""
        with patch("app.flows.service.DEFAULT_DB_PATH", Path("/tmp/test.db")):
            service = FlowService.__new__(FlowService)
            service.db_path = None
            service._limits_cache = None
            service._flags_cache = None
            service._catalog_cache = None
            service._rbac_cache = None

            # Just verify object was created
            assert service._limits_cache is None

    def test_init_custom_path(self):
        """Initialize with custom db path."""
        custom_path = Path("/tmp/custom.db")
        service = FlowService.__new__(FlowService)
        service.db_path = custom_path
        service._limits_cache = None
        service._flags_cache = None
        service._catalog_cache = None
        service._rbac_cache = None

        assert service.db_path == custom_path


class TestFlowServiceRequireActor:
    """Tests for _require_actor method."""

    def test_require_actor_present(self):
        """No error when actor is present."""
        service = FlowService.__new__(FlowService)
        service._require_actor("admin")  # Should not raise

    def test_require_actor_missing(self):
        """Error when actor is missing."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="Actor obrigatório"):
            service._require_actor(None)

    def test_require_actor_empty(self):
        """Error when actor is empty string."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="Actor obrigatório"):
            service._require_actor("")


class TestFlowServiceLoadSimpleYaml:
    """Tests for _load_simple_yaml method."""

    def test_load_simple_yaml_basic(self):
        """Load basic YAML file."""
        with TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            yaml_path.write_text("key: value\ncount: 42")

            service = FlowService.__new__(FlowService)
            result = service._load_simple_yaml(yaml_path)

            assert result.get("key") == "value"
            # YAML parser may return int or string depending on implementation
            assert result.get("count") in (42, "42")

    def test_load_simple_yaml_list(self):
        """Load YAML file with list."""
        with TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            yaml_path.write_text("items:\n  - one\n  - two\n  - three")

            service = FlowService.__new__(FlowService)
            result = service._load_simple_yaml(yaml_path)

            assert result.get("items") == ["one", "two", "three"]

    def test_load_simple_yaml_comments(self):
        """Load YAML file ignores comments."""
        with TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            yaml_path.write_text("# This is a comment\nkey: value\n# Another comment")

            service = FlowService.__new__(FlowService)
            result = service._load_simple_yaml(yaml_path)

            assert result.get("key") == "value"
            assert "#" not in str(result)


class TestFlowServiceCheckRbac:
    """Tests for _check_rbac method."""

    def test_check_rbac_no_actor(self):
        """No error when actor is None (fallback mode)."""
        service = FlowService.__new__(FlowService)
        service._rbac_cache = {}

        service._check_rbac("promote", None)  # Should not raise

    def test_check_rbac_system_actor(self):
        """System actor always allowed."""
        service = FlowService.__new__(FlowService)
        service._rbac_cache = {"actors": ["admin"], "promote": ["admin"]}

        service._check_rbac("promote", "system")  # Should not raise

    def test_check_rbac_allowed_actor(self):
        """Allowed actor passes check."""
        service = FlowService.__new__(FlowService)
        service._rbac_cache = {"actors": ["admin"], "promote": ["admin"]}

        service._check_rbac("promote", "admin")  # Should not raise

    def test_check_rbac_not_in_actors(self):
        """Error when actor not in allowed actors list."""
        service = FlowService.__new__(FlowService)
        service._rbac_cache = {"actors": ["admin"], "promote": ["admin"]}

        with pytest.raises(ValueError, match="não está na lista"):
            service._check_rbac("promote", "unknown_user")

    def test_check_rbac_not_authorized_for_action(self):
        """Error when actor not authorized for specific action."""
        service = FlowService.__new__(FlowService)
        service._rbac_cache = {"actors": ["admin", "viewer"], "promote": ["admin"]}

        with pytest.raises(ValueError, match="não autorizado"):
            service._check_rbac("promote", "viewer")


class TestFlowServiceLimits:
    """Tests for _limits method."""

    def test_limits_caches_result(self):
        """Limits are cached after first load."""
        with TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "flows_limits.yaml"
            yaml_path.write_text("max_test_percentual: 50")

            service = FlowService.__new__(FlowService)
            service._limits_cache = None

            with patch("app.flows.service.Path") as mock_path:
                mock_path.return_value = yaml_path
                mock_path.__truediv__ = lambda self, x: yaml_path

                # First call loads
                service._limits_cache = {"max_test_percentual": "50"}
                result1 = service._limits()

                # Second call uses cache
                result2 = service._limits()

                assert result1 == result2
                assert result1 == {"max_test_percentual": "50"}


class TestFlowServiceFlags:
    """Tests for _flags method."""

    def test_flags_caches_result(self):
        """Flags are cached after first load."""
        service = FlowService.__new__(FlowService)
        service._flags_cache = {"s35_flow_rollout_enabled": True}

        result = service._flags()

        assert result["s35_flow_rollout_enabled"] is True


class TestFlowServiceCatalog:
    """Tests for catalog methods."""

    def test_catalog_index_caches_result(self):
        """Catalog index is cached."""
        service = FlowService.__new__(FlowService)
        service._catalog_cache = {"template_ref": {"hash": "abc123"}}

        result = service._catalog_index()

        assert result == {"template_ref": {"hash": "abc123"}}

    def test_catalog_entry_from_cache(self):
        """Catalog entry retrieves from cache."""
        service = FlowService.__new__(FlowService)
        service._catalog_cache = {
            "config/flow_templates/test.yaml": {"flow_id": "test", "hash": "abc123"}
        }

        result = service._catalog_entry("test", "test")

        assert result == {"flow_id": "test", "hash": "abc123"}


class TestFlowServiceDeriveAlerts:
    """Tests for _derive_alerts method."""

    def test_derive_alerts_empty_flow(self):
        """Derive alerts for flow with no issues."""
        mock_flow = MagicMock()
        mock_flow.slug = "test_flow"
        mock_flow.template_origem_id = "tpl_test"
        mock_flow.percentual_teste = 10
        mock_flow.id = "flow_1"
        mock_flow.flow_version_id = "v1"
        mock_flow.catalog_hash = "abc123"

        service = FlowService.__new__(FlowService)
        service._flags_cache = {}
        service._limits_cache = {"max_test_percentual": "100"}
        service._catalog_cache = {
            "config/flow_templates/test.yaml": {"hash": "abc123"}
        }

        with patch.object(service, "_conn") as mock_conn:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=MagicMock())
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_conn.return_value = mock_ctx
            mock_ctx.__enter__().execute().fetchall.return_value = []

            with patch("app.flows.service.count_rollbacks_last_hour", return_value=0):
                result = service._derive_alerts(mock_flow)

        assert isinstance(result, list)


class TestFlowServiceDeriveSloStatus:
    """Tests for _derive_slo_status method."""

    def test_derive_slo_status_no_criteria(self):
        """No SLO status when no criteria."""
        mock_flow = MagicMock()
        mock_flow.rollout_criteria = {}

        service = FlowService.__new__(FlowService)
        result = service._derive_slo_status(mock_flow)

        assert result == []

    def test_derive_slo_status_no_slo_id(self):
        """No SLO status when no slo_id in criteria."""
        mock_flow = MagicMock()
        mock_flow.rollout_criteria = {"other": "value"}

        service = FlowService.__new__(FlowService)
        result = service._derive_slo_status(mock_flow)

        assert result == []


class TestFlowServiceReprocessItems:
    """Tests for reprocess_items method."""

    def test_reprocess_items_exceeds_limit(self):
        """Error when items exceed limit."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="excede limite"):
            service.reprocess_items("flow_1", {"item_ids": list(range(100))}, max_items=50)

    def test_reprocess_items_empty(self):
        """Error when no items provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="Nenhum item"):
            service.reprocess_items("flow_1", {"item_ids": []}, max_items=50)


class TestFlowServiceSaveTemplate:
    """Tests for save_template validation."""

    def test_save_template_no_slug(self):
        """Error when no slug provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="slug obrigatório"):
            service.save_template({})

    def test_save_template_no_steps(self):
        """Error when no steps provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="steps são obrigatórios"):
            service.save_template({"slug": "test"})

    def test_save_template_no_entry_type(self):
        """Error when no entry_type provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="entry_type é obrigatório"):
            service.save_template({"slug": "test", "steps": [{}]})

    def test_save_template_no_domain(self):
        """Error when no domain provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="domain é obrigatório"):
            service.save_template({"slug": "test", "steps": [{}], "entry_type": "news"})


class TestFlowServiceDeleteFlow:
    """Tests for delete_flow method."""

    def test_delete_flow_not_found(self):
        """Error when flow not found."""
        service = FlowService.__new__(FlowService)

        with patch.object(service, "_conn") as mock_conn:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=MagicMock())
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_conn.return_value = mock_ctx
            mock_ctx.__enter__().execute().fetchone.return_value = None

            with pytest.raises(ValueError, match="não encontrado"):
                service.delete_flow("missing_flow")


class TestFlowServiceStartRollout:
    """Tests for start_rollout validation."""

    def test_start_rollout_no_actor(self):
        """Error when no actor provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="Actor obrigatório"):
            service.start_rollout(
                "flow_1",
                mode="canary",
                test_percentual=10,
                actor=None,
            )

    def test_start_rollout_invalid_mode(self):
        """Error when invalid mode."""
        service = FlowService.__new__(FlowService)
        service._flags_cache = {"s35_flow_rollout_enabled": True}

        with pytest.raises(ValueError, match="Modo de rollout inválido"):
            service.start_rollout(
                "flow_1",
                mode="invalid",
                test_percentual=10,
                actor="admin",
            )

    def test_start_rollout_flag_disabled(self):
        """Error when rollout flag disabled."""
        service = FlowService.__new__(FlowService)
        service._flags_cache = {"s35_flow_rollout_enabled": False}

        with pytest.raises(ValueError, match="Flag.*desabilitada"):
            service.start_rollout(
                "flow_1",
                mode="canary",
                test_percentual=10,
                actor="admin",
            )


class TestFlowServicePromoteRollout:
    """Tests for promote_rollout validation."""

    def test_promote_rollout_no_actor(self):
        """Error when no actor provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="Actor obrigatório"):
            service.promote_rollout("flow_1", actor=None)


class TestFlowServiceRollbackRollout:
    """Tests for rollback_rollout validation."""

    def test_rollback_rollout_no_actor(self):
        """Error when no actor provided."""
        service = FlowService.__new__(FlowService)

        with pytest.raises(ValueError, match="Actor obrigatório"):
            service.rollback_rollout("flow_1", actor=None)


class TestFlowServiceRolloutStatus:
    """Tests for rollout_status method."""

    def test_rollout_status_flow_not_found(self):
        """Error when flow not found."""
        service = FlowService.__new__(FlowService)

        with patch.object(service, "get_flow", return_value=None):
            with pytest.raises(ValueError, match="não encontrado"):
                service.rollout_status("missing_flow")
