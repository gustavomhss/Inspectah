"""
Tests for AcordaoService — S41

Tests for the acordao creation and management.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from app.contestation import (
    AcordaoModel,
    AcordaoOutcome,
    AcordaoRequest,
    AcordaoService,
    ConsensusMetrics,
    VoteRecord,
    get_acordao_service,
    reset_acordao_service,
)


class TestAcordaoModel:
    """Tests for AcordaoModel."""

    def test_create_acordao_model(self) -> None:
        """Test creating an acordao model."""
        acordao = AcordaoModel(
            dispute_case_id="case_123",
            outcome=AcordaoOutcome.UPHELD,
            original_decision_id="dec_456",
        )
        assert acordao.id.startswith("acrd_")
        assert acordao.outcome == AcordaoOutcome.UPHELD
        assert not acordao.finalized

    def test_add_vote(self) -> None:
        """Test adding votes to acordao."""
        acordao = AcordaoModel()
        vote = VoteRecord(
            voter_id="arbiter_001",
            voter_role="arbiter",
            vote="uphold",
            confidence=0.9,
        )
        acordao.add_vote(vote)
        assert len(acordao.votes) == 1

    def test_calculate_consensus_unanimous(self) -> None:
        """Test consensus calculation with unanimous votes."""
        acordao = AcordaoModel()
        for i in range(3):
            acordao.add_vote(VoteRecord(
                voter_id=f"arbiter_{i}",
                vote="uphold",
                confidence=0.9,
            ))

        consensus = acordao.calculate_consensus()
        assert consensus == 1.0

    def test_calculate_consensus_split(self) -> None:
        """Test consensus calculation with split votes."""
        acordao = AcordaoModel()
        acordao.add_vote(VoteRecord(voter_id="a1", vote="uphold", confidence=0.9))
        acordao.add_vote(VoteRecord(voter_id="a2", vote="uphold", confidence=0.8))
        acordao.add_vote(VoteRecord(voter_id="a3", vote="overturn", confidence=0.7))

        consensus = acordao.calculate_consensus()
        assert consensus == pytest.approx(2/3, abs=0.01)

    def test_calculate_consensus_empty(self) -> None:
        """Test consensus with no votes."""
        acordao = AcordaoModel()
        assert acordao.calculate_consensus() == 0.0

    def test_finalize(self) -> None:
        """Test finalizing an acordao."""
        acordao = AcordaoModel()
        acordao.add_vote(VoteRecord(voter_id="a1", vote="uphold", confidence=0.9))

        acordao.finalize()

        assert acordao.finalized

    def test_finalize_twice_fails(self) -> None:
        """Test that finalizing twice fails."""
        acordao = AcordaoModel()
        acordao.add_vote(VoteRecord(voter_id="a1", vote="uphold", confidence=0.9))
        acordao.finalize()

        with pytest.raises(ValueError, match="already finalized"):
            acordao.finalize()

    def test_finalize_without_votes_fails(self) -> None:
        """Test that finalizing without votes fails."""
        acordao = AcordaoModel()

        with pytest.raises(ValueError, match="without votes"):
            acordao.finalize()

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        acordao = AcordaoModel(
            dispute_case_id="case_123",
            outcome=AcordaoOutcome.OVERTURNED,
        )
        acordao.add_vote(VoteRecord(voter_id="a1", vote="overturn", confidence=0.85))

        result = acordao.to_dict()

        assert result["dispute_case_id"] == "case_123"
        assert result["outcome"] == "overturned"
        assert len(result["votes"]) == 1


class TestAcordaoService:
    """Tests for AcordaoService."""

    def setup_method(self) -> None:
        """Reset service before each test."""
        reset_acordao_service()
        self.service = AcordaoService()

    def test_create_acordao_basic(self) -> None:
        """Test creating a basic acordao."""
        votes = [
            VoteRecord(voter_id="a1", voter_role="arbiter", vote="uphold", confidence=0.9),
            VoteRecord(voter_id="a2", voter_role="arbiter", vote="uphold", confidence=0.8),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        assert acordao.id.startswith("acrd_")
        assert acordao.outcome == AcordaoOutcome.UPHELD
        assert acordao.dispute_case_id == "case_123"
        assert len(acordao.votes) == 2

    def test_create_acordao_overturn(self) -> None:
        """Test creating an acordao that overturns."""
        votes = [
            VoteRecord(voter_id="a1", vote="overturn", confidence=0.9),
            VoteRecord(voter_id="a2", vote="overturn", confidence=0.85),
            VoteRecord(voter_id="a3", vote="uphold", confidence=0.6),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        assert acordao.outcome == AcordaoOutcome.OVERTURNED

    def test_create_acordao_insufficient_votes(self) -> None:
        """Test that insufficient votes raises error."""
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=[],
            issued_by="committee_001",
        )

        with pytest.raises(ValueError, match="Insufficient votes"):
            self.service.create_acordao(request)

    def test_delta_crenca_calculation(self) -> None:
        """Test delta-crença calculation."""
        # All overturn = high delta
        votes_overturn = [
            VoteRecord(voter_id="a1", vote="overturn", confidence=1.0),
            VoteRecord(voter_id="a2", vote="overturn", confidence=1.0),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes_overturn,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)
        assert acordao.delta_crenca > 0.5

        # All uphold = low delta
        self.service.clear()
        votes_uphold = [
            VoteRecord(voter_id="a1", vote="uphold", confidence=1.0),
            VoteRecord(voter_id="a2", vote="uphold", confidence=1.0),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_124",
            original_decision_id="dec_457",
            votes=votes_uphold,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)
        assert acordao.delta_crenca == 0.0

    def test_lambda_factor_calculation(self) -> None:
        """Test lambda-factor calculation."""
        votes = [
            VoteRecord(voter_id="a1", vote="uphold", confidence=0.95),
            VoteRecord(voter_id="a2", vote="uphold", confidence=0.90),
            VoteRecord(voter_id="a3", vote="uphold", confidence=0.85),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        # High confidence + high consensus + more votes = high lambda
        assert acordao.lambda_factor > 0.5

    def test_reasoning_generated(self) -> None:
        """Test that reasoning is generated."""
        votes = [
            VoteRecord(voter_id="a1", vote="uphold", confidence=0.9),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        assert acordao.reasoning
        assert "mantida" in acordao.reasoning.lower() or "voto" in acordao.reasoning.lower()

    def test_custom_reasoning(self) -> None:
        """Test using custom reasoning."""
        votes = [
            VoteRecord(voter_id="a1", vote="uphold", confidence=0.9),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
            custom_reasoning="Custom decision rationale",
        )

        acordao = self.service.create_acordao(request)

        assert acordao.reasoning == "Custom decision rationale"

    def test_dissenting_opinions_extracted(self) -> None:
        """Test that dissenting opinions are extracted."""
        votes = [
            VoteRecord(voter_id="a1", vote="uphold", confidence=0.9, reasoning="Agree"),
            VoteRecord(voter_id="a2", vote="uphold", confidence=0.8, reasoning="Also agree"),
            VoteRecord(voter_id="a3", vote="overturn", confidence=0.7, reasoning="I disagree"),
        ]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        assert len(acordao.dissenting_opinions) == 1
        assert "I disagree" in acordao.dissenting_opinions[0]

    def test_get_acordao(self) -> None:
        """Test getting an acordao by ID."""
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        retrieved = self.service.get_acordao(acordao.id)

        assert retrieved is not None
        assert retrieved.id == acordao.id

    def test_get_acordao_not_found(self) -> None:
        """Test getting non-existent acordao returns None."""
        result = self.service.get_acordao("nonexistent")
        assert result is None

    def test_finalize_acordao(self) -> None:
        """Test finalizing an acordao."""
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        request = AcordaoRequest(
            dispute_case_id="case_123",
            original_decision_id="dec_456",
            votes=votes,
            issued_by="committee_001",
        )

        acordao = self.service.create_acordao(request)

        result = self.service.finalize_acordao(acordao.id)

        assert result.finalized

    def test_list_acordaos(self) -> None:
        """Test listing acordaos."""
        # Create multiple acordaos
        for i in range(3):
            votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
            request = AcordaoRequest(
                dispute_case_id=f"case_{i}",
                original_decision_id=f"dec_{i}",
                votes=votes,
                issued_by="committee_001",
            )
            self.service.create_acordao(request)

        results = self.service.list_acordaos()

        assert len(results) == 3

    def test_list_acordaos_with_filter(self) -> None:
        """Test listing acordaos with filter."""
        for i in range(3):
            votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
            request = AcordaoRequest(
                dispute_case_id=f"case_{i}",
                original_decision_id=f"dec_{i}",
                votes=votes,
                issued_by="committee_001",
            )
            self.service.create_acordao(request)

        results = self.service.list_acordaos(dispute_case_id="case_1")

        assert len(results) == 1
        assert results[0].dispute_case_id == "case_1"


class TestConsensusMetrics:
    """Tests for ConsensusMetrics."""

    def test_consensus_metrics_to_dict(self) -> None:
        """Test serialization of consensus metrics."""
        metrics = ConsensusMetrics(
            total_votes=3,
            uphold_votes=2,
            overturn_votes=1,
            consensus_level=0.67,
            average_confidence=0.8,
            has_majority=True,
            majority_outcome=AcordaoOutcome.UPHELD,
        )

        result = metrics.to_dict()

        assert result["total_votes"] == 3
        assert result["consensus_level"] == 0.67
        assert result["majority_outcome"] == "upheld"


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_acordao_service(self) -> None:
        """Test getting singleton service."""
        reset_acordao_service()

        service1 = get_acordao_service()
        service2 = get_acordao_service()

        assert service1 is service2

    def test_reset_acordao_service(self) -> None:
        """Test resetting singleton."""
        service1 = get_acordao_service()
        reset_acordao_service()
        service2 = get_acordao_service()

        assert service1 is not service2
