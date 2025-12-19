"""
Tests for ContestationService — S41

Tests for the main contestation service orchestration.
"""

from __future__ import annotations

import pytest

from app.contestation import (
    ContestationService,
    ContestationStats,
    DisputeCase,
    DisputeStatus,
    AppealType,
    EvidenceType,
    VoteRecord,
    AcordaoOutcome,
    get_contestation_service,
    reset_contestation_service,
    reset_acordao_service,
)


class TestContestationService:
    """Tests for ContestationService."""

    def setup_method(self) -> None:
        """Reset services before each test."""
        reset_contestation_service()
        reset_acordao_service()
        self.service = ContestationService()

    def test_create_dispute(self) -> None:
        """Test creating a dispute."""
        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            petitioner_name="John Doe",
            domain="saude",
            risk_level="high",
        )

        assert case.id.startswith("case_")
        assert case.claim_id == "claim_123"
        assert case.model.petitioner_name == "John Doe"
        assert case.status == DisputeStatus.DRAFT

    def test_create_dispute_with_grounds(self) -> None:
        """Test creating a dispute with initial grounds."""
        grounds = [
            {
                "ground_type": "factual",
                "description": "Facts were wrong",
                "weight": 0.8,
            },
            {
                "ground_type": "procedural",
                "description": "Process error",
                "weight": 0.6,
            },
        ]

        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            grounds=grounds,
        )

        assert len(case.model.grounds) == 2
        assert case.model.grounds[0].ground_type == AppealType.FACTUAL
        assert case.model.grounds[1].ground_type == AppealType.PROCEDURAL

    def test_get_dispute(self) -> None:
        """Test getting a dispute by ID."""
        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        retrieved = self.service.get_dispute(case.id)

        assert retrieved is not None
        assert retrieved.id == case.id

    def test_get_dispute_not_found(self) -> None:
        """Test getting non-existent dispute returns None."""
        result = self.service.get_dispute("nonexistent")
        assert result is None

    def test_file_dispute(self) -> None:
        """Test filing a dispute."""
        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        self.service.add_ground(
            case.id,
            ground_type=AppealType.FACTUAL,
            description="Test ground",
        )

        result = self.service.file_dispute(case.id, "actor_001")

        assert result.success
        assert self.service.get_dispute(case.id).status == DisputeStatus.FILED

    def test_file_dispute_not_found(self) -> None:
        """Test filing non-existent dispute raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.file_dispute("nonexistent", "actor_001")

    def test_start_triage(self) -> None:
        """Test starting triage."""
        case = self._create_filed_case()

        result = self.service.start_triage(case.id, "triage_agent")

        assert result.success
        assert self.service.get_dispute(case.id).status == DisputeStatus.UNDER_TRIAGE

    def test_start_instruction(self) -> None:
        """Test starting instruction phase."""
        case = self._create_filed_case()
        self.service.start_triage(case.id, "triage_agent")

        result = self.service.start_instruction(case.id, "instructor")

        assert result.success
        assert self.service.get_dispute(case.id).status == DisputeStatus.INSTRUCTION

    def test_add_ground(self) -> None:
        """Test adding a ground via service."""
        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        ground = self.service.add_ground(
            case.id,
            ground_type=AppealType.ETHICAL,
            description="Ethical concern",
            weight=0.9,
        )

        assert ground.id.startswith("gnd_")
        assert ground.ground_type == AppealType.ETHICAL
        case = self.service.get_dispute(case.id)
        assert len(case.model.grounds) == 1

    def test_add_evidence(self) -> None:
        """Test adding evidence via service."""
        case = self._create_filed_case()

        evidence = self.service.add_evidence(
            case.id,
            evidence_type=EvidenceType.DOCUMENT,
            description="Supporting document",
            url="https://example.com/doc.pdf",
        )

        assert evidence.id.startswith("evd_")
        case = self.service.get_dispute(case.id)
        assert len(case.model.evidence) == 1

    def test_mark_ready_for_decision(self) -> None:
        """Test marking case ready for decision."""
        case = self._create_filed_case()
        self.service.start_triage(case.id, "triage_agent")

        result = self.service.mark_ready_for_decision(case.id, "reviewer")

        assert result.success
        assert self.service.get_dispute(case.id).status == DisputeStatus.READY_FOR_DECISION

    def test_decide_dispute(self) -> None:
        """Test deciding a dispute."""
        case = self._create_ready_case()
        votes = [
            VoteRecord(voter_id="a1", voter_role="arbiter", vote="uphold", confidence=0.9),
            VoteRecord(voter_id="a2", voter_role="arbiter", vote="uphold", confidence=0.85),
        ]

        acordao = self.service.decide_dispute(
            case.id,
            votes=votes,
            actor_id="committee_lead",
        )

        assert acordao.id.startswith("acrd_")
        assert acordao.outcome == AcordaoOutcome.UPHELD

        case = self.service.get_dispute(case.id)
        assert case.status == DisputeStatus.DECIDED
        assert case.model.acordao_id == acordao.id

    def test_decide_dispute_not_ready(self) -> None:
        """Test deciding dispute that's not ready raises error."""
        case = self._create_filed_case()
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]

        with pytest.raises(ValueError, match="not ready for decision"):
            self.service.decide_dispute(case.id, votes=votes, actor_id="lead")

    def test_reject_dispute(self) -> None:
        """Test rejecting a dispute."""
        case = self._create_filed_case()

        result = self.service.reject_dispute(
            case.id,
            actor_id="triage_agent",
            reason="Invalid grounds",
        )

        assert result.success
        assert self.service.get_dispute(case.id).status == DisputeStatus.REJECTED

    def test_close_dispute(self) -> None:
        """Test closing a dispute."""
        case = self._create_ready_case()
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        self.service.decide_dispute(case.id, votes=votes, actor_id="lead")

        result = self.service.close_dispute(case.id, actor_id="admin")

        assert result.success
        assert self.service.get_dispute(case.id).status == DisputeStatus.CLOSED

    def test_list_disputes(self) -> None:
        """Test listing disputes."""
        for i in range(3):
            self.service.create_dispute(
                claim_id=f"claim_{i}",
                original_decision_id=f"dec_{i}",
                petitioner_id="user_789",
            )

        results = self.service.list_disputes()

        assert len(results) == 3

    def test_list_disputes_with_filters(self) -> None:
        """Test listing disputes with filters."""
        case1 = self.service.create_dispute(
            claim_id="claim_1",
            original_decision_id="dec_1",
            petitioner_id="user_1",
            domain="saude",
        )
        case2 = self.service.create_dispute(
            claim_id="claim_2",
            original_decision_id="dec_2",
            petitioner_id="user_2",
            domain="governo",
        )

        results = self.service.list_disputes(domain="saude")

        assert len(results) == 1
        assert results[0].id == case1.id

    def test_get_statistics(self) -> None:
        """Test getting statistics."""
        # Create cases in different states
        case1 = self.service.create_dispute(
            claim_id="claim_1",
            original_decision_id="dec_1",
            petitioner_id="user_789",
        )
        self.service.add_ground(case1.id, AppealType.FACTUAL, "Test")
        self.service.file_dispute(case1.id, "actor")

        case2 = self.service.create_dispute(
            claim_id="claim_2",
            original_decision_id="dec_2",
            petitioner_id="user_789",
        )

        stats = self.service.get_statistics()

        assert stats.total_cases == 2
        assert stats.filed_cases == 1
        assert stats.draft_cases == 1

    def test_get_statistics_all_statuses(self) -> None:
        """Test statistics covers all statuses."""
        # Create case in under_triage status
        case_triage = self.service.create_dispute(
            claim_id="claim_triage",
            original_decision_id="dec_1",
            petitioner_id="user_1",
        )
        self.service.add_ground(case_triage.id, AppealType.FACTUAL, "Test")
        self.service.file_dispute(case_triage.id, "actor")
        self.service.start_triage(case_triage.id, "triager")

        # Create case in instruction status
        case_instruction = self.service.create_dispute(
            claim_id="claim_instruction",
            original_decision_id="dec_2",
            petitioner_id="user_2",
        )
        self.service.add_ground(case_instruction.id, AppealType.FACTUAL, "Test")
        self.service.file_dispute(case_instruction.id, "actor")
        self.service.start_triage(case_instruction.id, "triager")
        self.service.start_instruction(case_instruction.id, "instructor")

        # Create case in ready_for_decision status
        case_ready = self._create_ready_case()

        # Create decided case
        case_decided = self._create_ready_case()
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        self.service.decide_dispute(case_decided.id, votes=votes, actor_id="lead")

        # Create closed case
        case_closed = self._create_ready_case()
        votes = [VoteRecord(voter_id="a1", vote="overturn", confidence=0.85)]
        self.service.decide_dispute(case_closed.id, votes=votes, actor_id="lead")
        self.service.close_dispute(case_closed.id, actor_id="admin")

        # Create rejected case
        case_rejected = self.service.create_dispute(
            claim_id="claim_rejected",
            original_decision_id="dec_rej",
            petitioner_id="user_rej",
        )
        self.service.add_ground(case_rejected.id, AppealType.FACTUAL, "Test")
        self.service.file_dispute(case_rejected.id, "actor")
        self.service.reject_dispute(case_rejected.id, "triage", "Invalid")

        stats = self.service.get_statistics()

        assert stats.under_triage_cases == 1
        assert stats.instruction_cases == 1
        assert stats.ready_for_decision_cases == 1
        assert stats.decided_cases == 1
        assert stats.closed_cases == 1
        assert stats.rejected_cases == 1

    def test_get_statistics_acordao_outcomes(self) -> None:
        """Test statistics includes acordao outcome counts."""
        # Create upheld case
        case_upheld = self._create_ready_case()
        votes_upheld = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        self.service.decide_dispute(case_upheld.id, votes=votes_upheld, actor_id="lead")

        # Create overturned case
        case_overturned = self._create_ready_case()
        votes_overturn = [VoteRecord(voter_id="a1", vote="overturn", confidence=0.9)]
        self.service.decide_dispute(case_overturned.id, votes=votes_overturn, actor_id="lead")

        # Create modified case
        case_modified = self._create_ready_case()
        votes_modify = [VoteRecord(voter_id="a1", vote="modify", confidence=0.9)]
        self.service.decide_dispute(case_modified.id, votes=votes_modify, actor_id="lead")

        stats = self.service.get_statistics()

        assert stats.upheld_count == 1
        assert stats.overturned_count == 1
        assert stats.modified_count == 1

    def test_get_statistics_resolution_time(self) -> None:
        """Test statistics includes average resolution time."""
        # Create and decide a case
        case = self._create_ready_case()
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        self.service.decide_dispute(case.id, votes=votes, actor_id="lead")

        stats = self.service.get_statistics()

        # Resolution time should be calculated (even if 0 days for same-day decision)
        assert stats.average_resolution_days >= 0

    def test_clear_method(self) -> None:
        """Test clearing all cases."""
        # Create some cases
        self.service.create_dispute(
            claim_id="claim_1",
            original_decision_id="dec_1",
            petitioner_id="user_1",
        )
        self.service.create_dispute(
            claim_id="claim_2",
            original_decision_id="dec_2",
            petitioner_id="user_2",
        )

        assert len(self.service.list_disputes()) == 2

        self.service.clear()

        assert len(self.service.list_disputes()) == 0

    def test_create_dispute_with_metadata(self) -> None:
        """Test creating dispute with metadata."""
        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            metadata={"source": "api", "priority": "high"},
        )
        assert case.model.metadata == {"source": "api", "priority": "high"}

    def test_start_triage_not_found(self) -> None:
        """Test starting triage on non-existent case raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.start_triage("nonexistent", "actor")

    def test_start_instruction_not_found(self) -> None:
        """Test starting instruction on non-existent case raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.start_instruction("nonexistent", "actor")

    def test_add_ground_not_found(self) -> None:
        """Test adding ground to non-existent case raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.add_ground("nonexistent", AppealType.FACTUAL, "desc")

    def test_add_evidence_not_found(self) -> None:
        """Test adding evidence to non-existent case raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.add_evidence("nonexistent", EvidenceType.DOCUMENT, "desc")

    def test_mark_ready_not_found(self) -> None:
        """Test marking ready on non-existent case raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.mark_ready_for_decision("nonexistent", "actor")

    def test_decide_dispute_not_found(self) -> None:
        """Test deciding non-existent dispute raises error."""
        votes = [VoteRecord(voter_id="a1", vote="uphold", confidence=0.9)]
        with pytest.raises(ValueError, match="not found"):
            self.service.decide_dispute("nonexistent", votes=votes, actor_id="lead")

    def test_reject_dispute_not_found(self) -> None:
        """Test rejecting non-existent dispute raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.reject_dispute("nonexistent", "actor", "reason")

    def test_close_dispute_not_found(self) -> None:
        """Test closing non-existent dispute raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.service.close_dispute("nonexistent", "actor")

    # Helper methods
    def _create_filed_case(self) -> DisputeCase:
        case = self.service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        self.service.add_ground(case.id, AppealType.FACTUAL, "Test ground")
        self.service.file_dispute(case.id, "actor_001")
        return self.service.get_dispute(case.id)

    def _create_ready_case(self) -> DisputeCase:
        case = self._create_filed_case()
        self.service.start_triage(case.id, "triage_agent")
        self.service.mark_ready_for_decision(case.id, "reviewer")
        return self.service.get_dispute(case.id)


class TestContestationStats:
    """Tests for ContestationStats."""

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        stats = ContestationStats(
            total_cases=10,
            filed_cases=5,
            decided_cases=3,
            upheld_count=2,
            overturned_count=1,
        )

        result = stats.to_dict()

        assert result["total_cases"] == 10
        assert result["filed_cases"] == 5
        assert result["upheld_count"] == 2


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_contestation_service(self) -> None:
        """Test getting singleton service."""
        reset_contestation_service()

        service1 = get_contestation_service()
        service2 = get_contestation_service()

        assert service1 is service2

    def test_reset_contestation_service(self) -> None:
        """Test resetting singleton."""
        service1 = get_contestation_service()
        reset_contestation_service()
        service2 = get_contestation_service()

        assert service1 is not service2
