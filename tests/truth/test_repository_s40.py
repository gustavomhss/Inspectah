"""
Tests for Sprint 40 repository enhancements: DecisionBlockRepository.

Task: S40-BE-006
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.truth.repository import (
    DecisionBlockRepository,
    get_decision_block_repository,
    record_decision_block,
)


class MockDecisionBlock:
    """Mock DecisionBlock for testing."""

    def __init__(
        self,
        id: str = "block-001",
        decision_id: str = "decision-001",
        claim_id: str = "claim-001",
        domain: str = "saude",
        gate: str = "G23",
        initial_state: str = "pending",
        final_state: str = "verified",
        decision_type: str = "auto_approve",
        policy_name: str = "saude_g23",
        policy_version: str = "v1.0",
        committee_summary: dict = None,
        invariants_checked: dict = None,
        evidence_refs: list = None,
        latency_ms: int = 150,
        references=None,
        state_transition=None,
        experience_ref=None,
    ):
        self.id = id
        self.decision_id = decision_id
        self.claim_id = claim_id
        self.domain = domain
        self.gate = gate
        self.initial_state = initial_state
        self.final_state = final_state
        self.decision_type = decision_type
        self.policy_name = policy_name
        self.policy_version = policy_version
        self.committee_summary = committee_summary or {}
        self.invariants_checked = invariants_checked or {"evidence_exists": True}
        self.evidence_refs = evidence_refs or ["ev-001"]
        self.created_at = datetime.now(timezone.utc)
        self.latency_ms = latency_ms
        self.references = references
        self.state_transition = state_transition
        self.experience_ref = experience_ref or []


class MockReferences:
    """Mock References for testing."""

    def to_dict(self):
        return {
            "guias": [{"guia": "MQV", "documento": "01_Guia_3X"}],
            "pilares": [{"pilar": "P5", "documento": "P5-4"}],
            "e40_5": {"status": "PASS", "invariants_checked": ["INV-1"], "violations": []},
        }


class MockStateTransition:
    """Mock StateTransition for testing."""

    def __init__(self):
        self.from_state = "pending"
        self.to_state = "verified"
        self.reason = "auto_approved"
        self.timestamp = datetime.now(timezone.utc)


class TestDecisionBlockRepository:
    """Tests for DecisionBlockRepository."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            yield Path(f.name)

    @pytest.fixture
    def repo(self, temp_db):
        """Create a repository with temporary database."""
        return DecisionBlockRepository(db_path=temp_db)

    def test_create_repository(self, repo):
        """Test creating a repository."""
        assert repo is not None
        assert repo.db_path.exists()

    def test_record_basic_block(self, repo):
        """Test recording a basic DecisionBlock."""
        block = MockDecisionBlock()

        result = repo.record(block)

        assert result.id == block.id
        assert repo.count() == 1

    def test_record_block_with_references(self, repo):
        """Test recording a block with references."""
        block = MockDecisionBlock(references=MockReferences())

        result = repo.record(block)

        stored = repo.get(block.id)
        assert stored is not None
        assert stored["references"] is not None
        assert stored["references"]["guias"][0]["guia"] == "MQV"

    def test_record_block_with_state_transition(self, repo):
        """Test recording a block with state transition."""
        block = MockDecisionBlock(state_transition=MockStateTransition())

        result = repo.record(block)

        stored = repo.get(block.id)
        assert stored is not None
        assert stored["state_transition"] is not None
        assert stored["state_transition"]["from_state"] == "pending"
        assert stored["state_transition"]["to_state"] == "verified"

    def test_record_block_with_experience_refs(self, repo):
        """Test recording a block with experience refs."""
        block = MockDecisionBlock(experience_ref=["exp-001", "exp-002"])

        result = repo.record(block)

        stored = repo.get(block.id)
        assert stored is not None
        assert stored["experience_refs"] == ["exp-001", "exp-002"]

    def test_immutability_prevents_duplicate(self, repo):
        """Test that duplicate blocks are rejected."""
        block = MockDecisionBlock()

        repo.record(block)

        with pytest.raises(ValueError, match="already exists"):
            repo.record(block)

    def test_get_block(self, repo):
        """Test getting a block by ID."""
        block = MockDecisionBlock()
        repo.record(block)

        result = repo.get(block.id)

        assert result is not None
        assert result["id"] == block.id
        assert result["claim_id"] == block.claim_id
        assert result["domain"] == block.domain
        assert result["gate"] == block.gate
        assert result["final_state"] == block.final_state

    def test_get_nonexistent_block(self, repo):
        """Test getting a nonexistent block."""
        result = repo.get("nonexistent")

        assert result is None

    def test_get_by_claim(self, repo):
        """Test getting blocks by claim ID."""
        block1 = MockDecisionBlock(id="b1", claim_id="claim-1")
        block2 = MockDecisionBlock(id="b2", claim_id="claim-1")
        block3 = MockDecisionBlock(id="b3", claim_id="claim-2")

        repo.record(block1)
        repo.record(block2)
        repo.record(block3)

        results = repo.get_by_claim("claim-1")

        assert len(results) == 2
        assert all(r["claim_id"] == "claim-1" for r in results)

    def test_get_by_decision(self, repo):
        """Test getting block by decision ID."""
        block = MockDecisionBlock(decision_id="decision-123")
        repo.record(block)

        result = repo.get_by_decision("decision-123")

        assert result is not None
        assert result["decision_id"] == "decision-123"

    def test_list_recent(self, repo):
        """Test listing recent blocks."""
        for i in range(5):
            block = MockDecisionBlock(id=f"block-{i}", decision_id=f"decision-{i}")
            repo.record(block)

        results = repo.list_recent(limit=3)

        assert len(results) == 3

    def test_list_recent_by_domain(self, repo):
        """Test listing recent blocks by domain."""
        block1 = MockDecisionBlock(id="b1", domain="saude")
        block2 = MockDecisionBlock(id="b2", domain="politica")
        block3 = MockDecisionBlock(id="b3", domain="saude")

        repo.record(block1)
        repo.record(block2)
        repo.record(block3)

        results = repo.list_recent(domain="saude")

        assert len(results) == 2
        assert all(r["domain"] == "saude" for r in results)

    def test_count(self, repo):
        """Test counting blocks."""
        assert repo.count() == 0

        for i in range(3):
            block = MockDecisionBlock(id=f"block-{i}", decision_id=f"decision-{i}")
            repo.record(block)

        assert repo.count() == 3

    def test_count_by_domain(self, repo):
        """Test counting blocks by domain."""
        block1 = MockDecisionBlock(id="b1", domain="saude")
        block2 = MockDecisionBlock(id="b2", domain="politica")
        block3 = MockDecisionBlock(id="b3", domain="saude")

        repo.record(block1)
        repo.record(block2)
        repo.record(block3)

        assert repo.count(domain="saude") == 2
        assert repo.count(domain="politica") == 1


class TestRecordDecisionBlockFunction:
    """Tests for record_decision_block convenience function."""

    @pytest.fixture
    def temp_db(self, monkeypatch):
        """Set up temporary database path."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            monkeypatch.setenv("INSPECTAH_DECISION_BLOCK_DB_PATH", f.name)
            yield Path(f.name)

    def test_record_via_function(self, temp_db, monkeypatch):
        """Test recording via convenience function."""
        # Reset singleton
        import app.truth.repository as repo_module

        repo_module._decision_block_repository = None

        block = MockDecisionBlock()

        result = record_decision_block(block)

        assert result.id == block.id


class TestGetDecisionBlockRepository:
    """Tests for get_decision_block_repository function."""

    @pytest.fixture
    def temp_db(self, monkeypatch):
        """Set up temporary database path."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            monkeypatch.setenv("INSPECTAH_DECISION_BLOCK_DB_PATH", f.name)
            yield Path(f.name)

    def test_singleton_pattern(self, temp_db, monkeypatch):
        """Test that get_decision_block_repository returns singleton."""
        import app.truth.repository as repo_module

        repo_module._decision_block_repository = None

        repo1 = get_decision_block_repository()
        repo2 = get_decision_block_repository()

        assert repo1 is repo2
