"""
Tests for DisputeCase FSM — S41

Tests for the dispute case finite state machine.
"""

from __future__ import annotations

import pytest

from app.contestation import (
    DisputeCase,
    DisputeCaseModel,
    DisputeGround,
    DisputeStatus,
    AppealType,
    EvidenceType,
    TransitionResult,
    VALID_TRANSITIONS,
)


class TestDisputeCaseCreation:
    """Tests for creating dispute cases."""

    def test_create_basic_case(self) -> None:
        """Test creating a basic dispute case."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        assert case.id.startswith("case_")
        assert case.claim_id == "claim_123"
        assert case.model.original_decision_id == "dec_456"
        assert case.model.petitioner_id == "user_789"
        assert case.status == DisputeStatus.DRAFT

    def test_create_case_with_all_fields(self) -> None:
        """Test creating a case with all optional fields."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            petitioner_name="John Doe",
            domain="saude",
            risk_level="high",
            priority=5,
        )
        assert case.model.petitioner_name == "John Doe"
        assert case.model.domain == "saude"
        assert case.model.risk_level == "high"
        assert case.model.priority == 5

    def test_create_from_model(self) -> None:
        """Test creating DisputeCase from existing model."""
        model = DisputeCaseModel(
            claim_id="existing_claim",
            original_decision_id="existing_dec",
            petitioner_id="existing_user",
            status=DisputeStatus.FILED,
        )
        case = DisputeCase(model)
        assert case.status == DisputeStatus.FILED
        assert case.claim_id == "existing_claim"


class TestDisputeCaseTransitions:
    """Tests for state transitions."""

    def test_valid_transitions_defined(self) -> None:
        """Test that valid transitions are defined for all states."""
        for status in DisputeStatus:
            assert status in VALID_TRANSITIONS

    def test_file_from_draft(self) -> None:
        """Test filing a case from DRAFT status."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")

        result = case.file("actor_001")

        assert result.success
        assert case.status == DisputeStatus.FILED
        assert case.model.filed_at is not None

    def test_file_without_grounds_fails(self) -> None:
        """Test that filing without grounds fails."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        result = case.file("actor_001")

        assert not result.success
        assert "grounds" in result.reason.lower()

    def test_start_triage(self) -> None:
        """Test starting triage."""
        case = self._create_filed_case()

        result = case.start_triage("triage_agent")

        assert result.success
        assert case.status == DisputeStatus.UNDER_TRIAGE

    def test_start_instruction(self) -> None:
        """Test starting instruction phase."""
        case = self._create_triaged_case()

        result = case.start_instruction("instructor_001")

        assert result.success
        assert case.status == DisputeStatus.INSTRUCTION

    def test_mark_ready_for_decision(self) -> None:
        """Test marking case ready for decision."""
        case = self._create_instruction_case()
        case.add_evidence(EvidenceType.DOCUMENT, "Test evidence")

        result = case.mark_ready_for_decision("reviewer_001")

        assert result.success
        assert case.status == DisputeStatus.READY_FOR_DECISION

    def test_decide_case(self) -> None:
        """Test deciding a case."""
        case = self._create_ready_case()

        result = case.decide("arbiter_001", "acordao_123")

        assert result.success
        assert case.status == DisputeStatus.DECIDED
        assert case.model.acordao_id == "acordao_123"
        assert case.model.decided_at is not None

    def test_decide_without_acordao_fails(self) -> None:
        """Test that deciding without acordao fails."""
        case = self._create_ready_case()
        case.model.acordao_id = None  # Ensure no acordao

        # Try to transition without setting acordao_id
        result = case.transition(DisputeStatus.DECIDED, "arbiter_001")

        assert not result.success
        assert "acordao" in result.reason.lower()

    def test_close_case(self) -> None:
        """Test closing a case."""
        case = self._create_decided_case()

        result = case.close("admin_001")

        assert result.success
        assert case.status == DisputeStatus.CLOSED
        assert case.model.closed_at is not None

    def test_reject_case(self) -> None:
        """Test rejecting a case."""
        case = self._create_filed_case()

        result = case.reject("triage_agent", "Invalid grounds")

        assert result.success
        assert case.status == DisputeStatus.REJECTED

    def test_invalid_transition_fails(self) -> None:
        """Test that invalid transitions fail."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        # Try to skip directly to DECIDED from DRAFT
        result = case.transition(DisputeStatus.DECIDED, "actor_001")

        assert not result.success
        assert "invalid transition" in result.reason.lower()

    def test_can_transition_to(self) -> None:
        """Test checking if transition is valid."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        assert case.can_transition_to(DisputeStatus.FILED)
        assert case.can_transition_to(DisputeStatus.REJECTED)
        assert not case.can_transition_to(DisputeStatus.DECIDED)

    def test_get_valid_transitions(self) -> None:
        """Test getting valid transitions."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        valid = case.get_valid_transitions()

        assert DisputeStatus.FILED in valid
        assert DisputeStatus.REJECTED in valid
        assert len(valid) == 2

    # Helper methods
    def _create_filed_case(self) -> DisputeCase:
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")
        case.file("actor_001")
        return case

    def _create_triaged_case(self) -> DisputeCase:
        case = self._create_filed_case()
        case.start_triage("triage_agent")
        return case

    def _create_instruction_case(self) -> DisputeCase:
        case = self._create_triaged_case()
        case.start_instruction("instructor_001")
        return case

    def _create_ready_case(self) -> DisputeCase:
        case = self._create_triaged_case()
        case.mark_ready_for_decision("reviewer_001")
        return case

    def _create_decided_case(self) -> DisputeCase:
        case = self._create_ready_case()
        case.decide("arbiter_001", "acordao_123")
        return case


class TestDisputeCaseGrounds:
    """Tests for managing grounds."""

    def test_add_ground(self) -> None:
        """Test adding a ground."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        ground = case.add_ground(
            ground_type=AppealType.FACTUAL,
            description="The facts were misrepresented",
            weight=0.8,
        )

        assert ground.id.startswith("gnd_")
        assert ground.ground_type == AppealType.FACTUAL
        assert ground.weight == 0.8
        assert len(case.model.grounds) == 1

    def test_add_ground_with_evidence(self) -> None:
        """Test adding a ground with supporting evidence."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        ground = case.add_ground(
            ground_type=AppealType.ETHICAL,
            description="Ethical concerns",
            supporting_evidence=["evd_001", "evd_002"],
        )

        assert len(ground.supporting_evidence) == 2

    def test_add_ground_after_filing_fails(self) -> None:
        """Test that adding grounds after filing fails."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Initial ground")
        case.file("actor_001")

        with pytest.raises(ValueError, match="Cannot add grounds"):
            case.add_ground(AppealType.PROCEDURAL, "Late ground")

    def test_weight_clamped(self) -> None:
        """Test that weight is clamped to [0.0, 1.0]."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        ground = case.add_ground(AppealType.FACTUAL, "Test", weight=1.5)
        assert ground.weight == 1.0

        ground2 = case.add_ground(AppealType.FACTUAL, "Test", weight=-0.5)
        assert ground2.weight == 0.0


class TestDisputeCaseEvidence:
    """Tests for managing evidence."""

    def test_add_evidence(self) -> None:
        """Test adding evidence."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        evidence = case.add_evidence(
            evidence_type=EvidenceType.DOCUMENT,
            description="Supporting document",
            url="https://example.com/doc.pdf",
            submitted_by="user_789",
        )

        assert evidence.id.startswith("evd_")
        assert evidence.evidence_type == EvidenceType.DOCUMENT
        assert len(case.model.evidence) == 1

    def test_add_evidence_to_filed_case(self) -> None:
        """Test adding evidence to filed case works."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")
        case.file("actor_001")

        # Should succeed
        evidence = case.add_evidence(EvidenceType.SOURCE, "New source")
        assert evidence is not None

    def test_add_evidence_to_closed_case_fails(self) -> None:
        """Test that adding evidence to closed case fails."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")
        case.file("actor_001")
        case.reject("triage_agent", "Invalid")
        case.close("admin_001")

        with pytest.raises(ValueError, match="Cannot add evidence"):
            case.add_evidence(EvidenceType.DOCUMENT, "Late evidence")


class TestDisputeCaseProperties:
    """Tests for case properties."""

    def test_is_terminal(self) -> None:
        """Test is_terminal property."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        assert not case.is_terminal

        case.add_ground(AppealType.FACTUAL, "Test")
        case.file("actor_001")
        case.reject("agent", "Invalid")
        assert case.is_terminal

    def test_is_active(self) -> None:
        """Test is_active property."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        assert not case.is_active

        case.add_ground(AppealType.FACTUAL, "Test")
        case.file("actor_001")
        assert case.is_active

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")

        result = case.to_dict()

        assert "id" in result
        assert "claim_id" in result
        assert "status" in result
        assert "grounds" in result
        assert "transitions" in result
        assert "valid_transitions" in result


class TestDisputeCaseCallbacks:
    """Tests for transition callbacks."""

    def test_on_transition_callback(self) -> None:
        """Test transition callback is called."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")

        callback_called = []

        def on_filed(record):
            callback_called.append(record)

        case.on_transition("filed", on_filed)
        case.file("actor_001")

        assert len(callback_called) == 1
        assert callback_called[0].to_status == DisputeStatus.FILED

    def test_wildcard_callback(self) -> None:
        """Test wildcard callback is called for all transitions."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")

        all_transitions = []

        def on_any(record):
            all_transitions.append(record)

        case.on_transition("*", on_any)
        case.file("actor_001")
        case.start_triage("agent")

        assert len(all_transitions) == 2

    def test_get_transitions(self) -> None:
        """Test getting transition history."""
        case = DisputeCase.create(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )
        case.add_ground(AppealType.FACTUAL, "Test ground")
        case.file("actor_001")
        case.start_triage("agent")

        transitions = case.get_transitions()

        assert len(transitions) == 2
        assert transitions[0].to_status == DisputeStatus.FILED
        assert transitions[1].to_status == DisputeStatus.UNDER_TRIAGE
