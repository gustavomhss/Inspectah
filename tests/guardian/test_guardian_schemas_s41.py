"""
Tests for Guardian Schemas.

Tests for app/guardian/schemas.py Pydantic models.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.guardian.schemas import (
    CommitteeDetails,
    OrchestrateRequest,
    OrchestrateResponse,
    ThresholdConfigSchema,
    VoteResponse,
)


class TestThresholdConfigSchema:
    """Tests for ThresholdConfigSchema."""

    def test_create_minimal(self):
        """Create with minimal required fields."""
        config = ThresholdConfigSchema(
            risk_level="HIGH",
            min_agents=5,
            consensus_threshold=0.8,
        )

        assert config.risk_level == "HIGH"
        assert config.min_agents == 5
        assert config.consensus_threshold == 0.8
        assert config.veto_threshold is None

    def test_create_with_veto(self):
        """Create with veto threshold."""
        config = ThresholdConfigSchema(
            risk_level="MEDIUM",
            min_agents=3,
            consensus_threshold=0.7,
            veto_threshold=0.3,
        )

        assert config.veto_threshold == 0.3

    def test_from_dict(self):
        """Create from dictionary."""
        data = {
            "risk_level": "LOW",
            "min_agents": 2,
            "consensus_threshold": 0.6,
        }
        config = ThresholdConfigSchema(**data)
        assert config.risk_level == "LOW"
        assert config.min_agents == 2

    def test_validate_min_agents_positive(self):
        """min_agents must be >= 1."""
        with pytest.raises(ValidationError) as exc:
            ThresholdConfigSchema(
                risk_level="HIGH",
                min_agents=0,
                consensus_threshold=0.8,
            )
        assert "min_agents" in str(exc.value)

    def test_validate_consensus_threshold_bounds(self):
        """consensus_threshold must be between 0 and 1."""
        # Test lower bound
        with pytest.raises(ValidationError) as exc:
            ThresholdConfigSchema(
                risk_level="HIGH",
                min_agents=5,
                consensus_threshold=-0.1,
            )
        assert "consensus_threshold" in str(exc.value)

        # Test upper bound
        with pytest.raises(ValidationError) as exc:
            ThresholdConfigSchema(
                risk_level="HIGH",
                min_agents=5,
                consensus_threshold=1.5,
            )
        assert "consensus_threshold" in str(exc.value)

    def test_validate_veto_threshold_bounds(self):
        """veto_threshold must be between 0 and 1."""
        with pytest.raises(ValidationError) as exc:
            ThresholdConfigSchema(
                risk_level="HIGH",
                min_agents=5,
                consensus_threshold=0.8,
                veto_threshold=1.5,
            )
        assert "veto_threshold" in str(exc.value)

    def test_json_schema_example(self):
        """Schema has example in json_schema_extra."""
        schema = ThresholdConfigSchema.model_config.get("json_schema_extra")
        assert schema is not None
        assert "example" in schema
        assert "risk_level" in schema["example"]

    def test_from_attributes(self):
        """Schema can be created from_attributes."""
        assert ThresholdConfigSchema.model_config.get("from_attributes") is True


class TestVoteResponse:
    """Tests for VoteResponse."""

    def test_create_minimal(self):
        """Create with minimal required fields."""
        vote = VoteResponse(
            agent_id="fact_checker_01",
            vote="APPROVE",
            confidence=0.85,
            reasoning="Evidence is strong",
            processing_time_ms=1250,
        )

        assert vote.agent_id == "fact_checker_01"
        assert vote.vote == "APPROVE"
        assert vote.confidence == 0.85
        assert vote.reasoning == "Evidence is strong"
        assert vote.processing_time_ms == 1250
        assert vote.metadata is None

    def test_create_with_metadata(self):
        """Create with metadata."""
        vote = VoteResponse(
            agent_id="agent_01",
            vote="REJECT",
            confidence=0.9,
            reasoning="Insufficient evidence",
            processing_time_ms=800,
            metadata={"source_count": 2, "evidence_quality": "low"},
        )

        assert vote.metadata is not None
        assert vote.metadata["source_count"] == 2
        assert vote.metadata["evidence_quality"] == "low"

    def test_from_dict(self):
        """Create from dictionary."""
        data = {
            "agent_id": "agent_123",
            "vote": "ABSTAIN",
            "confidence": 0.5,
            "reasoning": "Not enough information",
            "processing_time_ms": 500,
        }
        vote = VoteResponse(**data)
        assert vote.vote == "ABSTAIN"
        assert vote.confidence == 0.5

    def test_validate_confidence_bounds(self):
        """confidence must be between 0 and 1."""
        # Test lower bound
        with pytest.raises(ValidationError) as exc:
            VoteResponse(
                agent_id="agent_01",
                vote="APPROVE",
                confidence=-0.1,
                reasoning="Test",
                processing_time_ms=100,
            )
        assert "confidence" in str(exc.value)

        # Test upper bound
        with pytest.raises(ValidationError) as exc:
            VoteResponse(
                agent_id="agent_01",
                vote="APPROVE",
                confidence=1.5,
                reasoning="Test",
                processing_time_ms=100,
            )
        assert "confidence" in str(exc.value)

    def test_validate_processing_time_non_negative(self):
        """processing_time_ms must be >= 0."""
        with pytest.raises(ValidationError) as exc:
            VoteResponse(
                agent_id="agent_01",
                vote="APPROVE",
                confidence=0.8,
                reasoning="Test",
                processing_time_ms=-100,
            )
        assert "processing_time_ms" in str(exc.value)

    def test_confidence_at_boundaries(self):
        """Test confidence at exact boundaries."""
        # Test 0.0
        vote = VoteResponse(
            agent_id="agent_01",
            vote="ABSTAIN",
            confidence=0.0,
            reasoning="No confidence",
            processing_time_ms=100,
        )
        assert vote.confidence == 0.0

        # Test 1.0
        vote = VoteResponse(
            agent_id="agent_02",
            vote="APPROVE",
            confidence=1.0,
            reasoning="Full confidence",
            processing_time_ms=100,
        )
        assert vote.confidence == 1.0

    def test_json_schema_example(self):
        """Schema has example in json_schema_extra."""
        schema = VoteResponse.model_config.get("json_schema_extra")
        assert schema is not None
        assert "example" in schema
        assert "agent_id" in schema["example"]


class TestCommitteeDetails:
    """Tests for CommitteeDetails."""

    def test_create_minimal(self):
        """Create with minimal required fields."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="committee_123",
            agent_ids=["agent_01", "agent_02", "agent_03"],
            total_agents=3,
            votes_approve=2,
            votes_reject=1,
            votes_abstain=0,
            formed_at=now,
        )

        assert committee.committee_id == "committee_123"
        assert len(committee.agent_ids) == 3
        assert committee.total_agents == 3
        assert committee.votes_approve == 2
        assert committee.votes_reject == 1
        assert committee.votes_abstain == 0
        assert committee.formed_at == now
        assert committee.dissolved_at is None

    def test_create_with_dissolved(self):
        """Create with dissolved timestamp."""
        now = datetime.now(timezone.utc)
        later = datetime(2025, 12, 19, 12, 0, 0, tzinfo=timezone.utc)
        committee = CommitteeDetails(
            committee_id="committee_456",
            agent_ids=["agent_01"],
            total_agents=1,
            votes_approve=1,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
            dissolved_at=later,
        )

        assert committee.dissolved_at == later

    def test_from_dict(self):
        """Create from dictionary."""
        now = datetime.now(timezone.utc)
        data = {
            "committee_id": "comm_xyz",
            "agent_ids": ["a1", "a2"],
            "total_agents": 2,
            "votes_approve": 1,
            "votes_reject": 1,
            "votes_abstain": 0,
            "formed_at": now,
        }
        committee = CommitteeDetails(**data)
        assert committee.committee_id == "comm_xyz"
        assert committee.total_agents == 2

    def test_validate_total_agents_positive(self):
        """total_agents must be >= 1."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc:
            CommitteeDetails(
                committee_id="comm_123",
                agent_ids=[],
                total_agents=0,
                votes_approve=0,
                votes_reject=0,
                votes_abstain=0,
                formed_at=now,
            )
        assert "total_agents" in str(exc.value)

    def test_validate_vote_counts_non_negative(self):
        """Vote counts must be >= 0."""
        now = datetime.now(timezone.utc)

        # Test negative votes_approve
        with pytest.raises(ValidationError) as exc:
            CommitteeDetails(
                committee_id="comm_123",
                agent_ids=["a1"],
                total_agents=1,
                votes_approve=-1,
                votes_reject=0,
                votes_abstain=0,
                formed_at=now,
            )
        assert "votes_approve" in str(exc.value)

        # Test negative votes_reject
        with pytest.raises(ValidationError) as exc:
            CommitteeDetails(
                committee_id="comm_123",
                agent_ids=["a1"],
                total_agents=1,
                votes_approve=0,
                votes_reject=-1,
                votes_abstain=0,
                formed_at=now,
            )
        assert "votes_reject" in str(exc.value)

        # Test negative votes_abstain
        with pytest.raises(ValidationError) as exc:
            CommitteeDetails(
                committee_id="comm_123",
                agent_ids=["a1"],
                total_agents=1,
                votes_approve=0,
                votes_reject=0,
                votes_abstain=-1,
                formed_at=now,
            )
        assert "votes_abstain" in str(exc.value)

    def test_empty_agent_ids_list(self):
        """Agent IDs list can be empty (edge case)."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=[],
            total_agents=1,
            votes_approve=0,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
        )
        assert len(committee.agent_ids) == 0


class TestOrchestrateRequest:
    """Tests for OrchestrateRequest."""

    def test_create_minimal(self):
        """Create with minimal required fields."""
        request = OrchestrateRequest(
            claim_id="claim_123",
            domain="politics",
            risk_level="HIGH",
            context={"source": "test"},
        )

        assert request.claim_id == "claim_123"
        assert request.domain == "politics"
        assert request.risk_level == "HIGH"
        assert request.context == {"source": "test"}
        assert request.priority is None
        assert request.timeout_ms is None

    def test_create_with_priority(self):
        """Create with priority."""
        request = OrchestrateRequest(
            claim_id="claim_456",
            domain="health",
            risk_level="MEDIUM",
            context={},
            priority=8,
        )

        assert request.priority == 8

    def test_create_with_timeout(self):
        """Create with timeout."""
        request = OrchestrateRequest(
            claim_id="claim_789",
            domain="science",
            risk_level="LOW",
            context={},
            timeout_ms=5000,
        )

        assert request.timeout_ms == 5000

    def test_from_dict(self):
        """Create from dictionary."""
        data = {
            "claim_id": "c1",
            "domain": "test",
            "risk_level": "HIGH",
            "context": {"key": "value"},
        }
        request = OrchestrateRequest(**data)
        assert request.claim_id == "c1"
        assert request.context["key"] == "value"

    def test_validate_priority_bounds(self):
        """priority must be between 0 and 10."""
        # Test lower bound
        with pytest.raises(ValidationError) as exc:
            OrchestrateRequest(
                claim_id="claim_123",
                domain="politics",
                risk_level="HIGH",
                context={},
                priority=-1,
            )
        assert "priority" in str(exc.value)

        # Test upper bound
        with pytest.raises(ValidationError) as exc:
            OrchestrateRequest(
                claim_id="claim_123",
                domain="politics",
                risk_level="HIGH",
                context={},
                priority=11,
            )
        assert "priority" in str(exc.value)

    def test_validate_timeout_minimum(self):
        """timeout_ms must be >= 1000."""
        with pytest.raises(ValidationError) as exc:
            OrchestrateRequest(
                claim_id="claim_123",
                domain="politics",
                risk_level="HIGH",
                context={},
                timeout_ms=500,
            )
        assert "timeout_ms" in str(exc.value)

    def test_priority_at_boundaries(self):
        """Test priority at exact boundaries."""
        # Test 0
        request = OrchestrateRequest(
            claim_id="c1",
            domain="test",
            risk_level="LOW",
            context={},
            priority=0,
        )
        assert request.priority == 0

        # Test 10
        request = OrchestrateRequest(
            claim_id="c2",
            domain="test",
            risk_level="HIGH",
            context={},
            priority=10,
        )
        assert request.priority == 10

    def test_complex_context(self):
        """Context can contain complex nested structures."""
        request = OrchestrateRequest(
            claim_id="claim_123",
            domain="politics",
            risk_level="HIGH",
            context={
                "source_url": "https://example.com",
                "claim_text": "Test claim",
                "nested": {
                    "key1": "value1",
                    "key2": [1, 2, 3],
                },
            },
        )

        assert request.context["nested"]["key2"] == [1, 2, 3]


class TestOrchestrateResponse:
    """Tests for OrchestrateResponse."""

    def test_create_minimal(self):
        """Create with minimal required fields."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=["agent_01"],
            total_agents=1,
            votes_approve=1,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
        )
        threshold = ThresholdConfigSchema(
            risk_level="HIGH",
            min_agents=1,
            consensus_threshold=0.8,
        )
        vote = VoteResponse(
            agent_id="agent_01",
            vote="APPROVE",
            confidence=0.9,
            reasoning="Good evidence",
            processing_time_ms=100,
        )

        response = OrchestrateResponse(
            decision_id="decision_123",
            claim_id="claim_456",
            outcome="APPROVED",
            committee=committee,
            votes=[vote],
            threshold_used=threshold,
            processing_time_ms=1500,
            completed_at=now,
        )

        assert response.decision_id == "decision_123"
        assert response.claim_id == "claim_456"
        assert response.outcome == "APPROVED"
        assert response.processing_time_ms == 1500
        assert response.completed_at == now
        assert response.confidence_score is None
        assert response.metadata is None

    def test_create_with_confidence_and_metadata(self):
        """Create with confidence score and metadata."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=["agent_01"],
            total_agents=1,
            votes_approve=1,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
        )
        threshold = ThresholdConfigSchema(
            risk_level="MEDIUM",
            min_agents=1,
            consensus_threshold=0.7,
        )
        vote = VoteResponse(
            agent_id="agent_01",
            vote="APPROVE",
            confidence=0.85,
            reasoning="Test",
            processing_time_ms=100,
        )

        response = OrchestrateResponse(
            decision_id="decision_789",
            claim_id="claim_abc",
            outcome="APPROVED",
            committee=committee,
            votes=[vote],
            threshold_used=threshold,
            processing_time_ms=2000,
            completed_at=now,
            confidence_score=0.88,
            metadata={"retries": 0, "warnings": []},
        )

        assert response.confidence_score == 0.88
        assert response.metadata is not None
        assert response.metadata["retries"] == 0

    def test_from_dict(self):
        """Create from dictionary."""
        now = datetime.now(timezone.utc)
        data = {
            "decision_id": "dec_123",
            "claim_id": "claim_456",
            "outcome": "REJECTED",
            "committee": {
                "committee_id": "comm_123",
                "agent_ids": ["a1"],
                "total_agents": 1,
                "votes_approve": 0,
                "votes_reject": 1,
                "votes_abstain": 0,
                "formed_at": now,
            },
            "votes": [
                {
                    "agent_id": "a1",
                    "vote": "REJECT",
                    "confidence": 0.95,
                    "reasoning": "No evidence",
                    "processing_time_ms": 200,
                }
            ],
            "threshold_used": {
                "risk_level": "HIGH",
                "min_agents": 1,
                "consensus_threshold": 0.8,
            },
            "processing_time_ms": 1000,
            "completed_at": now,
        }
        response = OrchestrateResponse(**data)
        assert response.outcome == "REJECTED"
        assert len(response.votes) == 1

    def test_validate_processing_time_non_negative(self):
        """processing_time_ms must be >= 0."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=["agent_01"],
            total_agents=1,
            votes_approve=1,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
        )
        threshold = ThresholdConfigSchema(
            risk_level="HIGH",
            min_agents=1,
            consensus_threshold=0.8,
        )

        with pytest.raises(ValidationError) as exc:
            OrchestrateResponse(
                decision_id="decision_123",
                claim_id="claim_456",
                outcome="APPROVED",
                committee=committee,
                votes=[],
                threshold_used=threshold,
                processing_time_ms=-100,
                completed_at=now,
            )
        assert "processing_time_ms" in str(exc.value)

    def test_validate_confidence_score_bounds(self):
        """confidence_score must be between 0 and 1."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=["agent_01"],
            total_agents=1,
            votes_approve=1,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
        )
        threshold = ThresholdConfigSchema(
            risk_level="HIGH",
            min_agents=1,
            consensus_threshold=0.8,
        )

        # Test upper bound
        with pytest.raises(ValidationError) as exc:
            OrchestrateResponse(
                decision_id="decision_123",
                claim_id="claim_456",
                outcome="APPROVED",
                committee=committee,
                votes=[],
                threshold_used=threshold,
                processing_time_ms=100,
                completed_at=now,
                confidence_score=1.5,
            )
        assert "confidence_score" in str(exc.value)

    def test_multiple_votes(self):
        """Response can contain multiple votes."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=["agent_01", "agent_02", "agent_03"],
            total_agents=3,
            votes_approve=2,
            votes_reject=1,
            votes_abstain=0,
            formed_at=now,
        )
        threshold = ThresholdConfigSchema(
            risk_level="HIGH",
            min_agents=3,
            consensus_threshold=0.8,
        )
        votes = [
            VoteResponse(
                agent_id="agent_01",
                vote="APPROVE",
                confidence=0.9,
                reasoning="Strong evidence",
                processing_time_ms=100,
            ),
            VoteResponse(
                agent_id="agent_02",
                vote="APPROVE",
                confidence=0.85,
                reasoning="Sufficient evidence",
                processing_time_ms=120,
            ),
            VoteResponse(
                agent_id="agent_03",
                vote="REJECT",
                confidence=0.75,
                reasoning="Conflicting sources",
                processing_time_ms=150,
            ),
        ]

        response = OrchestrateResponse(
            decision_id="decision_123",
            claim_id="claim_456",
            outcome="APPROVED",
            committee=committee,
            votes=votes,
            threshold_used=threshold,
            processing_time_ms=2500,
            completed_at=now,
        )

        assert len(response.votes) == 3
        assert response.votes[0].agent_id == "agent_01"
        assert response.votes[1].confidence == 0.85
        assert response.votes[2].vote == "REJECT"

    def test_empty_votes_list(self):
        """Response can have empty votes list."""
        now = datetime.now(timezone.utc)
        committee = CommitteeDetails(
            committee_id="comm_123",
            agent_ids=[],
            total_agents=1,
            votes_approve=0,
            votes_reject=0,
            votes_abstain=0,
            formed_at=now,
        )
        threshold = ThresholdConfigSchema(
            risk_level="LOW",
            min_agents=1,
            consensus_threshold=0.5,
        )

        response = OrchestrateResponse(
            decision_id="decision_123",
            claim_id="claim_456",
            outcome="INCONCLUSIVE",
            committee=committee,
            votes=[],
            threshold_used=threshold,
            processing_time_ms=500,
            completed_at=now,
        )

        assert len(response.votes) == 0
