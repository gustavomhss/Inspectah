"""
Tests for the Appeal Service — S41

Comprehensive tests for app/contestation/appeal.py
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from app.contestation.appeal import (
    AppealStatus,
    AppealBasis,
    AppealModel,
    AppealService,
    get_appeal_service,
    reset_appeal_service,
    _utcnow,
    _generate_id,
)


class TestAppealStatus:
    """Tests for AppealStatus enum."""

    def test_all_statuses_exist(self):
        """All expected statuses are defined."""
        assert AppealStatus.DRAFT == "draft"
        assert AppealStatus.FILED == "filed"
        assert AppealStatus.UNDER_REVIEW == "under_review"
        assert AppealStatus.ACCEPTED == "accepted"
        assert AppealStatus.REJECTED == "rejected"
        assert AppealStatus.CLOSED == "closed"

    def test_status_is_string(self):
        """Statuses are string enums."""
        assert isinstance(AppealStatus.DRAFT.value, str)


class TestAppealBasis:
    """Tests for AppealBasis enum."""

    def test_all_bases_exist(self):
        """All expected bases are defined."""
        assert AppealBasis.NEW_EVIDENCE == "new_evidence"
        assert AppealBasis.PROCEDURAL_ERROR == "procedural_error"
        assert AppealBasis.BIAS == "bias"
        assert AppealBasis.LEGAL_ERROR == "legal_error"
        assert AppealBasis.FACTUAL_ERROR == "factual_error"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_utcnow_returns_timezone_aware(self):
        """_utcnow returns timezone-aware datetime."""
        now = _utcnow()
        assert now.tzinfo is not None
        assert now.tzinfo == timezone.utc

    def test_generate_id_default_prefix(self):
        """_generate_id uses default prefix."""
        id1 = _generate_id()
        assert id1.startswith("apl_")
        assert len(id1) == 16  # "apl_" + 12 hex chars

    def test_generate_id_custom_prefix(self):
        """_generate_id uses custom prefix."""
        id1 = _generate_id("test")
        assert id1.startswith("test_")

    def test_generate_id_unique(self):
        """_generate_id produces unique IDs."""
        ids = [_generate_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestAppealModel:
    """Tests for AppealModel dataclass."""

    def test_create_default_model(self):
        """Create model with defaults."""
        model = AppealModel()
        assert model.id.startswith("apl_")
        assert model.acordao_id == ""
        assert model.dispute_case_id == ""
        assert model.appellant_id == ""
        assert model.appellant_name is None
        assert model.status == AppealStatus.DRAFT
        assert model.basis == AppealBasis.NEW_EVIDENCE
        assert model.grounds == ""
        assert model.new_evidence_ids == []
        assert model.response is None
        assert model.decision is None
        assert model.decision_by is None
        assert model.filed_at is None
        assert model.decided_at is None
        assert model.metadata == {}

    def test_create_model_with_values(self):
        """Create model with specific values."""
        model = AppealModel(
            id="apl_test123",
            acordao_id="acd_456",
            dispute_case_id="dsp_789",
            appellant_id="user_001",
            appellant_name="John Doe",
            status=AppealStatus.FILED,
            basis=AppealBasis.BIAS,
            grounds="Allegation of bias in decision",
            new_evidence_ids=["ev1", "ev2"],
            metadata={"key": "value"},
        )
        assert model.id == "apl_test123"
        assert model.acordao_id == "acd_456"
        assert model.dispute_case_id == "dsp_789"
        assert model.appellant_id == "user_001"
        assert model.appellant_name == "John Doe"
        assert model.status == AppealStatus.FILED
        assert model.basis == AppealBasis.BIAS
        assert model.grounds == "Allegation of bias in decision"
        assert model.new_evidence_ids == ["ev1", "ev2"]
        assert model.metadata == {"key": "value"}

    def test_to_dict(self):
        """to_dict serializes correctly."""
        now = _utcnow()
        model = AppealModel(
            id="apl_test",
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            appellant_name="Jane",
            status=AppealStatus.ACCEPTED,
            basis=AppealBasis.LEGAL_ERROR,
            grounds="Error in law application",
            new_evidence_ids=["e1"],
            response="Reviewed",
            decision="Accepted due to clear error",
            decision_by="judge_1",
            created_at=now,
            updated_at=now,
            filed_at=now,
            decided_at=now,
            metadata={"extra": "data"},
        )
        d = model.to_dict()
        assert d["id"] == "apl_test"
        assert d["acordao_id"] == "acd_1"
        assert d["dispute_case_id"] == "dsp_1"
        assert d["appellant_id"] == "user_1"
        assert d["appellant_name"] == "Jane"
        assert d["status"] == "accepted"
        assert d["basis"] == "legal_error"
        assert d["grounds"] == "Error in law application"
        assert d["new_evidence_ids"] == ["e1"]
        assert d["response"] == "Reviewed"
        assert d["decision"] == "Accepted due to clear error"
        assert d["decision_by"] == "judge_1"
        assert d["filed_at"] == now.isoformat()
        assert d["decided_at"] == now.isoformat()
        assert d["metadata"] == {"extra": "data"}

    def test_to_dict_with_none_dates(self):
        """to_dict handles None dates correctly."""
        model = AppealModel()
        d = model.to_dict()
        assert d["filed_at"] is None
        assert d["decided_at"] is None


class TestAppealService:
    """Tests for AppealService."""

    @pytest.fixture
    def service(self):
        """Create a fresh service for each test."""
        return AppealService()

    def test_init(self, service):
        """Service initializes correctly."""
        assert service._appeals == {}

    def test_create_appeal(self, service):
        """Create appeal successfully."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.NEW_EVIDENCE,
            grounds="Found new evidence",
        )
        assert appeal.id.startswith("apl_")
        assert appeal.acordao_id == "acd_1"
        assert appeal.dispute_case_id == "dsp_1"
        assert appeal.appellant_id == "user_1"
        assert appeal.basis == AppealBasis.NEW_EVIDENCE
        assert appeal.grounds == "Found new evidence"
        assert appeal.status == AppealStatus.DRAFT
        assert appeal.id in service._appeals

    def test_create_appeal_with_optional_params(self, service):
        """Create appeal with all optional parameters."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.PROCEDURAL_ERROR,
            grounds="Procedural violation",
            appellant_name="John Doe",
            new_evidence_ids=["ev1", "ev2"],
            metadata={"priority": "high"},
        )
        assert appeal.appellant_name == "John Doe"
        assert appeal.new_evidence_ids == ["ev1", "ev2"]
        assert appeal.metadata == {"priority": "high"}

    def test_file_appeal_success(self, service):
        """File appeal from DRAFT status."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Clear bias detected",
        )
        filed = service.file_appeal(appeal.id, "user_1")
        assert filed.status == AppealStatus.FILED
        assert filed.filed_at is not None

    def test_file_appeal_not_found(self, service):
        """File appeal fails if not found."""
        with pytest.raises(ValueError, match="Appeal not found"):
            service.file_appeal("nonexistent", "user_1")

    def test_file_appeal_wrong_status(self, service):
        """File appeal fails if not in DRAFT status."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias detected",
        )
        service.file_appeal(appeal.id, "user_1")
        with pytest.raises(ValueError, match="Cannot file appeal in status"):
            service.file_appeal(appeal.id, "user_1")

    def test_file_appeal_without_grounds(self, service):
        """File appeal fails without grounds."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="",  # Empty grounds
        )
        with pytest.raises(ValueError, match="Cannot file appeal without grounds"):
            service.file_appeal(appeal.id, "user_1")

    def test_start_review_success(self, service):
        """Start review from FILED status."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.FACTUAL_ERROR,
            grounds="Factual error in determination",
        )
        service.file_appeal(appeal.id, "user_1")
        reviewed = service.start_review(appeal.id, "reviewer_1")
        assert reviewed.status == AppealStatus.UNDER_REVIEW

    def test_start_review_not_found(self, service):
        """Start review fails if not found."""
        with pytest.raises(ValueError, match="Appeal not found"):
            service.start_review("nonexistent", "reviewer_1")

    def test_start_review_wrong_status(self, service):
        """Start review fails if not FILED."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias",
        )
        with pytest.raises(ValueError, match="Cannot start review"):
            service.start_review(appeal.id, "reviewer_1")

    def test_accept_appeal_success(self, service):
        """Accept appeal from UNDER_REVIEW status."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.LEGAL_ERROR,
            grounds="Law misapplied",
        )
        service.file_appeal(appeal.id, "user_1")
        service.start_review(appeal.id, "reviewer_1")
        accepted = service.accept_appeal(
            appeal.id,
            decision="Appeal has merit, law was misapplied",
            decision_by="judge_1",
        )
        assert accepted.status == AppealStatus.ACCEPTED
        assert accepted.decision == "Appeal has merit, law was misapplied"
        assert accepted.decision_by == "judge_1"
        assert accepted.decided_at is not None

    def test_accept_appeal_not_found(self, service):
        """Accept appeal fails if not found."""
        with pytest.raises(ValueError, match="Appeal not found"):
            service.accept_appeal("nonexistent", "decision", "judge")

    def test_accept_appeal_wrong_status(self, service):
        """Accept appeal fails if not UNDER_REVIEW."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias",
        )
        with pytest.raises(ValueError, match="Cannot accept appeal"):
            service.accept_appeal(appeal.id, "decision", "judge")

    def test_reject_appeal_success(self, service):
        """Reject appeal from UNDER_REVIEW status."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.PROCEDURAL_ERROR,
            grounds="Process error claimed",
        )
        service.file_appeal(appeal.id, "user_1")
        service.start_review(appeal.id, "reviewer_1")
        rejected = service.reject_appeal(
            appeal.id,
            decision="No procedural error found",
            decision_by="judge_1",
        )
        assert rejected.status == AppealStatus.REJECTED
        assert rejected.decision == "No procedural error found"
        assert rejected.decision_by == "judge_1"
        assert rejected.decided_at is not None

    def test_reject_appeal_not_found(self, service):
        """Reject appeal fails if not found."""
        with pytest.raises(ValueError, match="Appeal not found"):
            service.reject_appeal("nonexistent", "decision", "judge")

    def test_reject_appeal_wrong_status(self, service):
        """Reject appeal fails if not UNDER_REVIEW."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias",
        )
        service.file_appeal(appeal.id, "user_1")
        with pytest.raises(ValueError, match="Cannot reject appeal"):
            service.reject_appeal(appeal.id, "decision", "judge")

    def test_close_appeal_after_accepted(self, service):
        """Close appeal after ACCEPTED."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.NEW_EVIDENCE,
            grounds="New evidence",
        )
        service.file_appeal(appeal.id, "user_1")
        service.start_review(appeal.id, "reviewer_1")
        service.accept_appeal(appeal.id, "Accepted", "judge_1")
        closed = service.close_appeal(appeal.id, "admin_1")
        assert closed.status == AppealStatus.CLOSED

    def test_close_appeal_after_rejected(self, service):
        """Close appeal after REJECTED."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias alleged",
        )
        service.file_appeal(appeal.id, "user_1")
        service.start_review(appeal.id, "reviewer_1")
        service.reject_appeal(appeal.id, "Rejected", "judge_1")
        closed = service.close_appeal(appeal.id, "admin_1")
        assert closed.status == AppealStatus.CLOSED

    def test_close_appeal_not_found(self, service):
        """Close appeal fails if not found."""
        with pytest.raises(ValueError, match="Appeal not found"):
            service.close_appeal("nonexistent", "admin")

    def test_close_appeal_wrong_status(self, service):
        """Close appeal fails if not ACCEPTED or REJECTED."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias",
        )
        with pytest.raises(ValueError, match="Cannot close appeal"):
            service.close_appeal(appeal.id, "admin")

    def test_get_appeal_exists(self, service):
        """Get existing appeal."""
        appeal = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="Bias",
        )
        retrieved = service.get_appeal(appeal.id)
        assert retrieved == appeal

    def test_get_appeal_not_exists(self, service):
        """Get nonexistent appeal returns None."""
        retrieved = service.get_appeal("nonexistent")
        assert retrieved is None

    def test_list_appeals_all(self, service):
        """List all appeals."""
        for i in range(3):
            service.create_appeal(
                acordao_id=f"acd_{i}",
                dispute_case_id=f"dsp_{i}",
                appellant_id=f"user_{i}",
                basis=AppealBasis.BIAS,
                grounds=f"Grounds {i}",
            )
        appeals = service.list_appeals()
        assert len(appeals) == 3

    def test_list_appeals_filter_by_acordao(self, service):
        """List appeals filtered by acordao_id."""
        service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="G1",
        )
        service.create_appeal(
            acordao_id="acd_2",
            dispute_case_id="dsp_2",
            appellant_id="user_2",
            basis=AppealBasis.BIAS,
            grounds="G2",
        )
        appeals = service.list_appeals(acordao_id="acd_1")
        assert len(appeals) == 1
        assert appeals[0].acordao_id == "acd_1"

    def test_list_appeals_filter_by_appellant(self, service):
        """List appeals filtered by appellant_id."""
        service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="G1",
        )
        service.create_appeal(
            acordao_id="acd_2",
            dispute_case_id="dsp_2",
            appellant_id="user_2",
            basis=AppealBasis.BIAS,
            grounds="G2",
        )
        appeals = service.list_appeals(appellant_id="user_1")
        assert len(appeals) == 1
        assert appeals[0].appellant_id == "user_1"

    def test_list_appeals_filter_by_status(self, service):
        """List appeals filtered by status."""
        appeal1 = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="G1",
        )
        service.create_appeal(
            acordao_id="acd_2",
            dispute_case_id="dsp_2",
            appellant_id="user_2",
            basis=AppealBasis.BIAS,
            grounds="G2",
        )
        service.file_appeal(appeal1.id, "user_1")
        appeals = service.list_appeals(status=AppealStatus.FILED)
        assert len(appeals) == 1
        assert appeals[0].status == AppealStatus.FILED

    def test_list_appeals_with_limit(self, service):
        """List appeals respects limit."""
        for i in range(10):
            service.create_appeal(
                acordao_id=f"acd_{i}",
                dispute_case_id=f"dsp_{i}",
                appellant_id=f"user_{i}",
                basis=AppealBasis.BIAS,
                grounds=f"G{i}",
            )
        appeals = service.list_appeals(limit=5)
        assert len(appeals) == 5

    def test_list_appeals_sorted_by_created_at(self, service):
        """List appeals sorted by created_at descending."""
        # Create with delays to ensure order
        a1 = service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="First",
        )
        a2 = service.create_appeal(
            acordao_id="acd_2",
            dispute_case_id="dsp_2",
            appellant_id="user_2",
            basis=AppealBasis.BIAS,
            grounds="Second",
        )
        # Manually adjust created_at for testing
        a1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        a2.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)

        appeals = service.list_appeals()
        assert appeals[0].grounds == "Second"
        assert appeals[1].grounds == "First"

    def test_clear(self, service):
        """Clear removes all appeals."""
        service.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="G",
        )
        assert len(service._appeals) == 1
        service.clear()
        assert len(service._appeals) == 0


class TestSingleton:
    """Tests for singleton functions."""

    def setup_method(self):
        """Reset singleton before each test."""
        reset_appeal_service()

    def teardown_method(self):
        """Reset singleton after each test."""
        reset_appeal_service()

    def test_get_appeal_service_creates_instance(self):
        """get_appeal_service creates singleton."""
        service = get_appeal_service()
        assert service is not None
        assert isinstance(service, AppealService)

    def test_get_appeal_service_returns_same_instance(self):
        """get_appeal_service returns same instance."""
        s1 = get_appeal_service()
        s2 = get_appeal_service()
        assert s1 is s2

    def test_reset_appeal_service(self):
        """reset_appeal_service resets the singleton."""
        s1 = get_appeal_service()
        s1.create_appeal(
            acordao_id="acd_1",
            dispute_case_id="dsp_1",
            appellant_id="user_1",
            basis=AppealBasis.BIAS,
            grounds="G",
        )
        reset_appeal_service()
        s2 = get_appeal_service()
        assert s1 is not s2
        assert len(s2._appeals) == 0
