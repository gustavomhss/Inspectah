"""
Tests for agents/repository — S37

Integration tests for AgentsRepository.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from app.agents.repository import AgentsRepository
from app.agents.models import (
    AgentCommittee,
    AgentInstructionVersion,
    AgentKBRef,
    AgentLayer,
    AgentProfile,
    AgentRole,
    AgentRun,
    AgentRunStatus,
    AgentStatus,
    CommitteePolicy,
    ModelUpgradePolicy,
)


@pytest.fixture
def repo(tmp_path: Path) -> AgentsRepository:
    """Create repository with temporary database."""
    db_path = tmp_path / "test_agents.sqlite"
    return AgentsRepository(db_path=db_path)


@pytest.fixture
def sample_agent() -> AgentProfile:
    """Create a sample agent profile."""
    return AgentProfile(
        id="agent_test_1",
        name="Test Agent",
        description="A test agent",
        instructions="Test instructions",
        role=AgentRole.ANALYST,
        layer=AgentLayer.INTERPRETATION,
        model_name="gpt-4",
        recommended_model_name="gpt-4",
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
        status=AgentStatus.ACTIVE,
        kb_refs=[
            AgentKBRef(id="kb_1", kind="doc", label="Test Doc", path_or_uri="/docs/test.md")
        ],
        created_by="tester",
    )


@pytest.fixture
def sample_committee() -> AgentCommittee:
    """Create a sample committee."""
    return AgentCommittee(
        id="comm_test_1",
        name="Test Committee",
        description="A test committee",
        layer=AgentLayer.DEBUNK,
        primary_agents=["agent_1", "agent_2"],
        mediator_agent="agent_mediator",
        policy=CommitteePolicy(required_agreement_ratio=0.8),
        status=AgentStatus.ACTIVE,
    )


class TestAgentsRepositoryInit:
    """Tests for repository initialization."""

    def test_init_creates_db(self, tmp_path: Path):
        """Repository creates database on init."""
        db_path = tmp_path / "test.sqlite"
        repo = AgentsRepository(db_path=db_path)

        assert db_path.exists()


class TestAgentsRepositoryAgents:
    """Tests for agent CRUD operations."""

    def test_create_agent(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """Create agent."""
        result = repo.create_agent(sample_agent)

        assert result.id == sample_agent.id
        assert result.name == sample_agent.name

    def test_get_agent(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """Get agent by ID."""
        repo.create_agent(sample_agent)

        result = repo.get_agent(sample_agent.id)

        assert result is not None
        assert result.id == sample_agent.id

    def test_get_agent_not_found(self, repo: AgentsRepository):
        """Get non-existent agent returns None."""
        result = repo.get_agent("missing_agent")

        assert result is None

    def test_update_agent(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """Update agent."""
        repo.create_agent(sample_agent)
        sample_agent.name = "Updated Name"
        sample_agent.updated_at = datetime.now(timezone.utc)

        result = repo.update_agent(sample_agent)

        assert result.name == "Updated Name"

    def test_list_agents_empty(self, repo: AgentsRepository):
        """List agents when none exist."""
        result = repo.list_agents()

        assert result == []

    def test_list_agents(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """List agents."""
        repo.create_agent(sample_agent)

        result = repo.list_agents()

        assert len(result) == 1
        assert result[0].id == sample_agent.id

    def test_list_agents_by_layer(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """List agents filtered by layer."""
        repo.create_agent(sample_agent)

        result = repo.list_agents(layer=AgentLayer.INTERPRETATION)

        assert len(result) == 1

        result_empty = repo.list_agents(layer=AgentLayer.DEBUNK)

        assert len(result_empty) == 0

    def test_list_agents_by_role(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """List agents filtered by role."""
        repo.create_agent(sample_agent)

        result = repo.list_agents(role=AgentRole.ANALYST)

        assert len(result) == 1

    def test_list_agents_by_status(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """List agents filtered by status."""
        repo.create_agent(sample_agent)

        result = repo.list_agents(status=AgentStatus.ACTIVE)

        assert len(result) == 1


class TestAgentsRepositoryVersions:
    """Tests for instruction version operations."""

    def test_create_instruction_version(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """Create instruction version."""
        repo.create_agent(sample_agent)
        version = AgentInstructionVersion(
            id="ver_1",
            agent_id=sample_agent.id,
            version_number=1,
            instructions="New instructions",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            kb_snapshot=[],
            changelog="Initial version",
            created_by="tester",
        )

        result = repo.create_instruction_version(version)

        assert result.id == "ver_1"
        assert result.version_number == 1

    def test_list_instruction_versions(self, repo: AgentsRepository, sample_agent: AgentProfile):
        """List instruction versions."""
        repo.create_agent(sample_agent)
        version = AgentInstructionVersion(
            id="ver_1",
            agent_id=sample_agent.id,
            version_number=1,
            instructions="New instructions",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            kb_snapshot=[],
            changelog="Initial version",
            created_by="tester",
        )
        repo.create_instruction_version(version)

        result = repo.list_instruction_versions(sample_agent.id)

        assert len(result) == 1
        assert result[0].version_number == 1


class TestAgentsRepositoryCommittees:
    """Tests for committee CRUD operations."""

    def test_create_committee(self, repo: AgentsRepository, sample_committee: AgentCommittee):
        """Create committee."""
        result = repo.create_committee(sample_committee)

        assert result.id == sample_committee.id
        assert result.name == sample_committee.name

    def test_get_committee(self, repo: AgentsRepository, sample_committee: AgentCommittee):
        """Get committee by ID."""
        repo.create_committee(sample_committee)

        result = repo.get_committee(sample_committee.id)

        assert result is not None
        assert result.id == sample_committee.id

    def test_get_committee_not_found(self, repo: AgentsRepository):
        """Get non-existent committee returns None."""
        result = repo.get_committee("missing_committee")

        assert result is None

    def test_update_committee(self, repo: AgentsRepository, sample_committee: AgentCommittee):
        """Update committee."""
        repo.create_committee(sample_committee)
        sample_committee.name = "Updated Committee"
        sample_committee.updated_at = datetime.now(timezone.utc)

        result = repo.update_committee(sample_committee)

        assert result.name == "Updated Committee"

    def test_list_committees(self, repo: AgentsRepository, sample_committee: AgentCommittee):
        """List committees."""
        repo.create_committee(sample_committee)

        result = repo.list_committees()

        assert len(result) == 1

    def test_list_committees_by_layer(self, repo: AgentsRepository, sample_committee: AgentCommittee):
        """List committees filtered by layer."""
        repo.create_committee(sample_committee)

        result = repo.list_committees(layer=AgentLayer.DEBUNK)

        assert len(result) == 1


class TestAgentsRepositoryModelPolicy:
    """Tests for model policy operations."""

    def test_get_model_policy_creates_default(self, repo: AgentsRepository):
        """Get model policy creates default if none exists."""
        result = repo.get_model_policy()

        assert isinstance(result, ModelUpgradePolicy)
        assert result.global_default_model == "gpt-plus-latest"

    def test_save_model_policy(self, repo: AgentsRepository):
        """Save model policy."""
        policy = ModelUpgradePolicy(
            global_default_model="gpt-5",
            auto_upgrade_enabled=False,
            adoption_delay_days=30,
            allowed_models=["gpt-4", "gpt-5"],
        )

        result = repo.save_model_policy(policy)

        assert result.global_default_model == "gpt-5"

        # Verify persisted
        loaded = repo.get_model_policy()
        assert loaded.global_default_model == "gpt-5"


class TestAgentsRepositoryRuns:
    """Tests for run operations."""

    def test_create_run(self, repo: AgentsRepository):
        """Create run."""
        run = AgentRun.create(
            id="run_1",
            committee_id="comm_1",
            input_ref="input_ref_1",
            payload_snapshot={"key": "value"},
        )

        result = repo.create_run(run)

        assert result.id == "run_1"
        assert result.status == AgentRunStatus.RUNNING

    def test_get_run(self, repo: AgentsRepository):
        """Get run by ID."""
        run = AgentRun.create(
            id="run_2",
            committee_id="comm_1",
            input_ref=None,
            payload_snapshot={},
        )
        repo.create_run(run)

        result = repo.get_run("run_2")

        assert result is not None
        assert result.id == "run_2"

    def test_get_run_not_found(self, repo: AgentsRepository):
        """Get non-existent run returns None."""
        result = repo.get_run("missing_run")

        assert result is None

    def test_update_run(self, repo: AgentsRepository):
        """Update run."""
        run = AgentRun.create(
            id="run_3",
            committee_id="comm_1",
            input_ref=None,
            payload_snapshot={},
        )
        repo.create_run(run)

        run.status = AgentRunStatus.SUCCESS
        run.result_bundle_ref = "bundle_1"
        run.finished_at = datetime.now(timezone.utc)

        result = repo.update_run(run)

        assert result.status == AgentRunStatus.SUCCESS

    def test_list_runs_by_committee(self, repo: AgentsRepository):
        """List runs by committee."""
        run = AgentRun.create(
            id="run_4",
            committee_id="comm_test",
            input_ref=None,
            payload_snapshot={},
        )
        repo.create_run(run)

        result = repo.list_runs_by_committee("comm_test")

        assert len(result) == 1
        assert result[0].committee_id == "comm_test"
