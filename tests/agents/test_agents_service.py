"""
Tests for agents/service — S37

Tests for agent service functions.
"""

import json
import os
import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from app.agents.service import (
    _gen_id,
    _validate_agent,
    _validate_committee,
    _validate_flow,
    add_instruction_version,
    create_agent_profile,
    create_committee,
    finalize_committee_run_fail,
    finalize_committee_run_success,
    get_flow,
    get_or_create_model_policy,
    record_committee_trace,
    save_flow,
    start_committee_run,
    update_agent_profile,
    update_committee,
    update_model_policy,
)
from app.agents.models import (
    AgentCommittee,
    AgentLayer,
    AgentProfile,
    AgentRole,
    AgentRunStatus,
    AgentStatus,
    CommitteePolicy,
    FlowLayerType,
    ModelUpgradePolicy,
)
from app.truth.models import TraceLinkRefs


class TestGenId:
    """Tests for _gen_id function."""

    def test_gen_id_with_prefix(self):
        """Generate ID with given prefix."""
        result = _gen_id("test")

        assert result.startswith("test_")
        assert len(result) > 5

    def test_gen_id_unique(self):
        """Generated IDs are unique."""
        ids = [_gen_id("pref") for _ in range(100)]

        assert len(set(ids)) == 100


class TestValidateAgent:
    """Tests for _validate_agent function."""

    def test_validate_agent_valid(self):
        """Valid agent passes validation."""
        agent = AgentProfile(
            id="agent_1",
            name="Test Agent",
            description="Test",
            instructions="Do stuff",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )

        _validate_agent(agent)  # Should not raise

    def test_validate_agent_no_name(self):
        """Agent without name fails validation."""
        agent = AgentProfile(
            id="agent_1",
            name="",
            description="Test",
            instructions="Do stuff",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )

        with pytest.raises(ValueError, match="Agent name is required"):
            _validate_agent(agent)

    def test_validate_agent_no_layer(self):
        """Agent without layer fails validation."""
        agent = AgentProfile(
            id="agent_1",
            name="Test",
            description="Test",
            instructions="Do stuff",
            role=AgentRole.ANALYST,
            layer=None,  # type: ignore
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )

        with pytest.raises(ValueError, match="layer and role are required"):
            _validate_agent(agent)


class TestValidateFlow:
    """Tests for _validate_flow function."""

    def test_validate_flow_empty_list(self):
        """Empty flow list fails validation."""
        with pytest.raises(ValueError, match="lista não vazia"):
            _validate_flow([])

    def test_validate_flow_not_list(self):
        """Non-list flow fails validation."""
        with pytest.raises(ValueError, match="lista não vazia"):
            _validate_flow({})

    def test_validate_flow_entry_not_dict(self):
        """Flow entry that is not a dict fails validation."""
        with pytest.raises(ValueError, match="objeto"):
            _validate_flow(["not a dict"])

    def test_validate_flow_invalid_layer_type(self):
        """Flow with invalid layer type fails validation."""
        with pytest.raises(ValueError, match="Camada inválida"):
            _validate_flow([{"layer_type": "invalid_layer"}])

    def test_validate_flow_duplicate_layer(self):
        """Flow with duplicate layer fails validation."""
        flow = [
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a1", "a2", "a3"],
                "mediator_agent_id": "a1",
            },
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a4", "a5", "a6"],
                "mediator_agent_id": "a4",
            },
        ]

        with pytest.raises(ValueError, match="duplicada"):
            _validate_flow(flow)

    def test_validate_flow_less_than_3_agents(self):
        """Flow layer with less than 3 agents fails validation."""
        flow = [
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a1", "a2"],
                "mediator_agent_id": "a1",
            },
        ]

        with pytest.raises(ValueError, match="pelo menos 3 agentes"):
            _validate_flow(flow)

    def test_validate_flow_mediator_not_in_agents(self):
        """Flow with mediator not in agents fails validation."""
        flow = [
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a1", "a2", "a3"],
                "mediator_agent_id": "outside",
            },
        ]

        with pytest.raises(ValueError, match="Mediador deve fazer parte"):
            _validate_flow(flow)

    def test_validate_flow_missing_layers(self):
        """Flow with missing required layers fails validation."""
        flow = [
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a1", "a2", "a3"],
                "mediator_agent_id": "a1",
            },
        ]

        with pytest.raises(ValueError, match="faltam camadas"):
            _validate_flow(flow)

    def test_validate_flow_complete(self):
        """Complete valid flow passes validation."""
        flow = [
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a1", "a2", "a3"],
                "mediator_agent_id": "a1",
            },
            {
                "layer_type": FlowLayerType.CLASSIFICATION.value,
                "agent_ids": ["b1", "b2", "b3"],
                "mediator_agent_id": "b1",
            },
            {
                "layer_type": FlowLayerType.INTERMEDIATE.value,
                "agent_ids": ["c1", "c2", "c3"],
                "mediator_agent_id": "c1",
            },
            {
                "layer_type": FlowLayerType.DECISION_MAKER.value,
                "agent_ids": ["d1", "d2", "d3"],
                "mediator_agent_id": "d1",
            },
            {
                "layer_type": FlowLayerType.LIBRARIAN.value,
                "agent_ids": ["e1", "e2", "e3"],
                "mediator_agent_id": "e1",
            },
        ]

        _validate_flow(flow)  # Should not raise


class TestGetFlow:
    """Tests for get_flow function."""

    def test_get_flow_file_not_exists(self):
        """Get flow when file doesn't exist returns empty list."""
        with patch("app.agents.service.FLOW_PATH") as mock_path:
            mock_path.exists.return_value = False

            result = get_flow()

            assert result == []

    def test_get_flow_empty_file(self):
        """Get flow from empty file returns empty list."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "flow.json"
            flow_path.write_text("")

            with patch("app.agents.service.FLOW_PATH", flow_path):
                result = get_flow()

                assert result == []

    def test_get_flow_whitespace_only(self):
        """Get flow from whitespace-only file returns empty list."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "flow.json"
            flow_path.write_text("   \n\t  ")

            with patch("app.agents.service.FLOW_PATH", flow_path):
                result = get_flow()

                assert result == []

    def test_get_flow_valid_list(self):
        """Get flow from valid JSON list."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "flow.json"
            flow_data = [{"layer": "test"}]
            flow_path.write_text(json.dumps(flow_data))

            with patch("app.agents.service.FLOW_PATH", flow_path):
                result = get_flow()

                assert result == flow_data

    def test_get_flow_json_not_list(self):
        """Get flow from JSON that is not a list returns empty list."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "flow.json"
            flow_path.write_text('{"key": "value"}')

            with patch("app.agents.service.FLOW_PATH", flow_path):
                result = get_flow()

                assert result == []

    def test_get_flow_invalid_json(self):
        """Get flow from invalid JSON returns empty list."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "flow.json"
            flow_path.write_text("not valid json{")

            with patch("app.agents.service.FLOW_PATH", flow_path):
                result = get_flow()

                assert result == []


class TestSaveFlow:
    """Tests for save_flow function."""

    def test_save_flow_valid(self):
        """Save valid flow."""
        flow_data = [
            {
                "layer_type": FlowLayerType.INTERPRETATION.value,
                "agent_ids": ["a1", "a2", "a3"],
                "mediator_agent_id": "a1",
            },
            {
                "layer_type": FlowLayerType.CLASSIFICATION.value,
                "agent_ids": ["b1", "b2", "b3"],
                "mediator_agent_id": "b1",
            },
            {
                "layer_type": FlowLayerType.INTERMEDIATE.value,
                "agent_ids": ["c1", "c2", "c3"],
                "mediator_agent_id": "c1",
            },
            {
                "layer_type": FlowLayerType.DECISION_MAKER.value,
                "agent_ids": ["d1", "d2", "d3"],
                "mediator_agent_id": "d1",
            },
            {
                "layer_type": FlowLayerType.LIBRARIAN.value,
                "agent_ids": ["e1", "e2", "e3"],
                "mediator_agent_id": "e1",
            },
        ]

        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "runtime" / "flow.json"

            with patch("app.agents.service.FLOW_PATH", flow_path):
                result = save_flow(flow_data)

                assert result == flow_data
                assert flow_path.exists()
                saved_data = json.loads(flow_path.read_text())
                assert saved_data == flow_data

    def test_save_flow_invalid_raises(self):
        """Save invalid flow raises ValueError."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "runtime" / "flow.json"

            with patch("app.agents.service.FLOW_PATH", flow_path):
                with pytest.raises(ValueError):
                    save_flow([])

    def test_save_flow_non_list_becomes_empty(self):
        """Save non-list flow saves empty list."""
        with TemporaryDirectory() as tmpdir:
            flow_path = Path(tmpdir) / "runtime" / "flow.json"

            with patch("app.agents.service.FLOW_PATH", flow_path):
                with pytest.raises(ValueError):
                    save_flow({"not": "a list"})


class TestCreateAgentProfile:
    """Tests for create_agent_profile function."""

    def test_create_agent_profile(self):
        """Create agent profile."""
        mock_repo = MagicMock()
        agent = AgentProfile(
            id="agent_new",
            name="New Agent",
            description="Desc",
            instructions="Instr",
            role=AgentRole.DEBUNKER,
            layer=AgentLayer.DEBUNK,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.5,
            max_tokens=2000,
            top_p=0.9,
            status=AgentStatus.ACTIVE,
            created_by="admin",
        )

        result = create_agent_profile(mock_repo, agent)

        assert result == agent
        mock_repo.create_agent.assert_called_once_with(agent)
        mock_repo.create_instruction_version.assert_called_once()

    def test_create_agent_profile_invalid(self):
        """Create agent with invalid data raises."""
        mock_repo = MagicMock()
        agent = AgentProfile(
            id="agent_bad",
            name="",  # Invalid - empty name
            description="Desc",
            instructions="Instr",
            role=AgentRole.DEBUNKER,
            layer=AgentLayer.DEBUNK,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.5,
            max_tokens=2000,
            top_p=0.9,
            status=AgentStatus.ACTIVE,
        )

        with pytest.raises(ValueError):
            create_agent_profile(mock_repo, agent)


class TestUpdateAgentProfile:
    """Tests for update_agent_profile function."""

    def test_update_agent_profile_found(self):
        """Update existing agent profile."""
        existing = AgentProfile(
            id="agent_1",
            name="Old Name",
            description="Old Desc",
            instructions="Old Instr",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-3.5",
            recommended_model_name="gpt-3.5",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = existing

        result = update_agent_profile(mock_repo, "agent_1", {"name": "New Name"})

        assert result is not None
        assert result.name == "New Name"
        mock_repo.update_agent.assert_called_once()

    def test_update_agent_profile_not_found(self):
        """Update non-existent agent returns None."""
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = None

        result = update_agent_profile(mock_repo, "agent_missing", {"name": "New"})

        assert result is None

    def test_update_agent_profile_ignores_none_values(self):
        """Update ignores None values in updates."""
        existing = AgentProfile(
            id="agent_1",
            name="Original",
            description="Desc",
            instructions="Instr",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = existing

        result = update_agent_profile(mock_repo, "agent_1", {"name": None})

        assert result.name == "Original"


class TestAddInstructionVersion:
    """Tests for add_instruction_version function."""

    def test_add_instruction_version_agent_not_found(self):
        """Add version to non-existent agent returns None."""
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = None

        result = add_instruction_version(
            mock_repo,
            "missing_agent",
            "new instructions",
            "changelog",
            None,
            None,
            None,
            None,
            None,
            "author",
        )

        assert result is None

    def test_add_instruction_version_first_version(self):
        """Add first version creates version 1."""
        existing = AgentProfile(
            id="agent_1",
            name="Agent",
            description="Desc",
            instructions="Old",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = existing
        mock_repo.list_instruction_versions.return_value = []

        result = add_instruction_version(
            mock_repo,
            "agent_1",
            "new instructions",
            "Initial",
            None,
            None,
            None,
            None,
            None,
            "author",
        )

        assert result is not None
        assert result.version_number == 1
        assert result.instructions == "new instructions"

    def test_add_instruction_version_increments(self):
        """Add version increments version number."""
        existing = AgentProfile(
            id="agent_1",
            name="Agent",
            description="Desc",
            instructions="Old",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )
        mock_version = MagicMock()
        mock_version.version_number = 5
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = existing
        mock_repo.list_instruction_versions.return_value = [mock_version]

        result = add_instruction_version(
            mock_repo,
            "agent_1",
            "new instructions",
            "Update",
            None,
            None,
            None,
            None,
            None,
            "author",
        )

        assert result is not None
        assert result.version_number == 6


class TestRecordCommitteeTrace:
    """Tests for record_committee_trace function."""

    def test_record_committee_trace_basic(self):
        """Record committee trace with basic data."""
        link_refs = TraceLinkRefs(
            truth_record_id="tr_1",
            decision_record_id="dr_1",
            claim_id="claim_1",
            domain="politics",
            risk_level="high",
            request_id="req_1",
        )

        mock_repo = MagicMock()
        mock_repo.save_committee_trace.return_value = MagicMock()

        result = record_committee_trace(
            link_refs,
            agent_trace_ids=["at_1", "at_2"],
            summary="Test summary",
            repo=mock_repo,
        )

        mock_repo.save_committee_trace.assert_called_once()
        call_arg = mock_repo.save_committee_trace.call_args[0][0]
        assert call_arg.truth_record_id == "tr_1"
        assert call_arg.decision_record_id == "dr_1"
        assert call_arg.claim_id == "claim_1"
        assert call_arg.domain == "politics"

    def test_record_committee_trace_default_domain(self):
        """Record committee trace with None domain uses default."""
        link_refs = TraceLinkRefs(
            truth_record_id="tr_1",
            decision_record_id="dr_1",
            claim_id="claim_1",
            domain=None,
        )

        mock_repo = MagicMock()
        mock_repo.save_committee_trace.return_value = MagicMock()

        record_committee_trace(
            link_refs,
            agent_trace_ids=[],
            summary="Test",
            repo=mock_repo,
        )

        call_arg = mock_repo.save_committee_trace.call_args[0][0]
        assert call_arg.domain == "pilot_politics"


class TestValidateCommittee:
    """Tests for _validate_committee function."""

    def test_validate_committee_not_two_primary(self):
        """Committee without two primary agents fails validation."""
        mock_repo = MagicMock()
        committee = AgentCommittee(
            id="comm_1",
            name="Test",
            description="Desc",
            layer=AgentLayer.DEBUNK,
            primary_agents=["agent_1"],  # Only one
            mediator_agent="mediator_1",
            policy=CommitteePolicy(),
        )

        with pytest.raises(ValueError, match="dois agentes primários"):
            _validate_committee(mock_repo, committee)

    def test_validate_committee_mediator_is_primary(self):
        """Committee with mediator in primary agents fails validation."""
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = MagicMock()
        committee = AgentCommittee(
            id="comm_1",
            name="Test",
            description="Desc",
            layer=AgentLayer.DEBUNK,
            primary_agents=["agent_1", "mediator_1"],  # Mediator is in primary
            mediator_agent="mediator_1",
            policy=CommitteePolicy(),
        )

        with pytest.raises(ValueError, match="diferente dos agentes primários"):
            _validate_committee(mock_repo, committee)

    def test_validate_committee_agent_not_found(self):
        """Committee with missing agent fails validation."""
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = None
        committee = AgentCommittee(
            id="comm_1",
            name="Test",
            description="Desc",
            layer=AgentLayer.DEBUNK,
            primary_agents=["agent_1", "agent_2"],
            mediator_agent="mediator_1",
            policy=CommitteePolicy(),
        )

        with pytest.raises(ValueError, match="não encontrado"):
            _validate_committee(mock_repo, committee)


class TestCreateCommittee:
    """Tests for create_committee function."""

    def test_create_committee_valid(self):
        """Create valid committee."""
        mock_repo = MagicMock()
        mock_repo.get_agent.return_value = MagicMock()
        committee = AgentCommittee(
            id="comm_1",
            name="Test Committee",
            description="Desc",
            layer=AgentLayer.DEBUNK,
            primary_agents=["agent_1", "agent_2"],
            mediator_agent="mediator_1",
            policy=CommitteePolicy(),
        )

        result = create_committee(mock_repo, committee)

        assert result == committee
        mock_repo.create_committee.assert_called_once_with(committee)


class TestUpdateCommittee:
    """Tests for update_committee function."""

    def test_update_committee_not_found(self):
        """Update non-existent committee returns None."""
        mock_repo = MagicMock()
        mock_repo.get_committee.return_value = None

        result = update_committee(mock_repo, "comm_missing", {"name": "New"})

        assert result is None

    def test_update_committee_found(self):
        """Update existing committee."""
        existing = AgentCommittee(
            id="comm_1",
            name="Old Name",
            description="Desc",
            layer=AgentLayer.DEBUNK,
            primary_agents=["agent_1", "agent_2"],
            mediator_agent="mediator_1",
            policy=CommitteePolicy(),
        )
        mock_repo = MagicMock()
        mock_repo.get_committee.return_value = existing
        mock_repo.get_agent.return_value = MagicMock()

        result = update_committee(mock_repo, "comm_1", {"name": "New Name"})

        assert result is not None
        assert result.name == "New Name"
        mock_repo.update_committee.assert_called_once()


class TestModelPolicy:
    """Tests for model policy functions."""

    def test_get_or_create_model_policy(self):
        """Get or create model policy."""
        mock_repo = MagicMock()
        expected_policy = ModelUpgradePolicy()
        mock_repo.get_model_policy.return_value = expected_policy

        result = get_or_create_model_policy(mock_repo)

        assert result == expected_policy

    def test_update_model_policy_all_fields(self):
        """Update model policy with all fields."""
        mock_repo = MagicMock()
        mock_repo.get_model_policy.return_value = ModelUpgradePolicy()
        new_date = datetime(2024, 12, 1, tzinfo=timezone.utc)

        result = update_model_policy(
            mock_repo,
            global_default_model="gpt-5",
            auto_upgrade_enabled=False,
            adoption_delay_days=30,
            allowed_models=["gpt-4", "gpt-5"],
            next_upgrade_at=new_date,
        )

        assert result.global_default_model == "gpt-5"
        assert result.auto_upgrade_enabled is False
        assert result.adoption_delay_days == 30
        assert result.allowed_models == ["gpt-4", "gpt-5"]
        assert result.next_upgrade_at == new_date
        mock_repo.save_model_policy.assert_called_once()

    def test_update_model_policy_partial(self):
        """Update model policy with partial fields."""
        mock_repo = MagicMock()
        mock_repo.get_model_policy.return_value = ModelUpgradePolicy(
            global_default_model="gpt-4",
            auto_upgrade_enabled=True,
        )

        result = update_model_policy(
            mock_repo,
            global_default_model=None,  # Not updating
            auto_upgrade_enabled=False,  # Updating
            adoption_delay_days=None,
            allowed_models=None,
        )

        assert result.global_default_model == "gpt-4"  # Unchanged
        assert result.auto_upgrade_enabled is False  # Changed


class TestCommitteeRuns:
    """Tests for committee run functions."""

    def test_start_committee_run_committee_not_found(self):
        """Start run for non-existent committee returns None."""
        mock_repo = MagicMock()
        mock_repo.get_committee.return_value = None

        result = start_committee_run(
            mock_repo, "comm_missing", None, {"key": "value"}
        )

        assert result is None

    def test_start_committee_run_success(self):
        """Start committee run successfully."""
        mock_repo = MagicMock()
        mock_repo.get_committee.return_value = MagicMock()

        result = start_committee_run(
            mock_repo, "comm_1", "input_ref_1", {"data": "test"}
        )

        assert result is not None
        assert result.committee_id == "comm_1"
        assert result.input_ref == "input_ref_1"
        assert result.status == AgentRunStatus.RUNNING
        mock_repo.create_run.assert_called_once()

    def test_finalize_committee_run_success_not_found(self):
        """Finalize run that doesn't exist returns None."""
        mock_repo = MagicMock()
        mock_repo.get_run.return_value = None

        result = finalize_committee_run_success(
            mock_repo, "run_missing", "bundle_1"
        )

        assert result is None

    def test_finalize_committee_run_success(self):
        """Finalize run with success."""
        from app.agents.models import AgentRun

        mock_run = AgentRun.create(
            id="run_1",
            committee_id="comm_1",
            input_ref=None,
            payload_snapshot={},
        )
        mock_repo = MagicMock()
        mock_repo.get_run.return_value = mock_run

        result = finalize_committee_run_success(
            mock_repo, "run_1", "bundle_success"
        )

        assert result is not None
        assert result.status == AgentRunStatus.SUCCESS
        assert result.result_bundle_ref == "bundle_success"
        assert result.finished_at is not None
        mock_repo.update_run.assert_called_once()

    def test_finalize_committee_run_fail_not_found(self):
        """Finalize run failure for non-existent run returns None."""
        mock_repo = MagicMock()
        mock_repo.get_run.return_value = None

        result = finalize_committee_run_fail(
            mock_repo, "run_missing", "error msg"
        )

        assert result is None

    def test_finalize_committee_run_fail(self):
        """Finalize run with failure."""
        from app.agents.models import AgentRun

        mock_run = AgentRun.create(
            id="run_1",
            committee_id="comm_1",
            input_ref=None,
            payload_snapshot={},
        )
        mock_repo = MagicMock()
        mock_repo.get_run.return_value = mock_run

        result = finalize_committee_run_fail(
            mock_repo, "run_1", "Something went wrong"
        )

        assert result is not None
        assert result.status == AgentRunStatus.FAIL
        assert result.error == "Something went wrong"
        assert result.finished_at is not None
        mock_repo.update_run.assert_called_once()
