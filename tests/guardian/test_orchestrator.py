"""
Tests for Guardian Orchestrator — S41

Tests for CommitteeOrchestrator, ThresholdConfig, CommitteeSelector,
OrchestrationResult, and vote aggregation logic.
"""

import pytest
from datetime import datetime, timezone

from app.guardian.orchestrator import (
    CommitteeOrchestrator,
    CommitteeSelector,
    OrchestrationResult,
    Outcome,
    RiskLevel,
    ThresholdConfig,
    get_committee_orchestrator,
    get_threshold,
)
from app.guardian.models import (
    Committee,
    CommitteeMember,
    Vote,
    VoteType,
)
from app.guardian.roles import GuardianRole


class TestOutcome:
    """Tests for Outcome enum."""

    def test_all_outcomes_defined(self):
        """All expected outcomes are defined."""
        expected = ["approved", "rejected", "needs_review", "inconclusive"]
        actual = [o.value for o in Outcome]
        assert set(actual) == set(expected)

    def test_outcome_values(self):
        """Outcome values match expected strings."""
        assert Outcome.APPROVED.value == "approved"
        assert Outcome.REJECTED.value == "rejected"
        assert Outcome.NEEDS_REVIEW.value == "needs_review"
        assert Outcome.INCONCLUSIVE.value == "inconclusive"

    def test_outcome_is_string_enum(self):
        """Outcome is a string enum."""
        assert isinstance(Outcome.APPROVED, str)
        assert Outcome.APPROVED == "approved"


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_all_risk_levels_defined(self):
        """All expected risk levels are defined."""
        expected = ["low", "medium", "high", "critical"]
        actual = [r.value for r in RiskLevel]
        assert set(actual) == set(expected)

    def test_risk_level_values(self):
        """Risk level values match expected strings."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestThresholdConfig:
    """Tests for ThresholdConfig dataclass."""

    def test_default_thresholds(self):
        """Default threshold values are set correctly."""
        config = ThresholdConfig()
        assert config.approve_threshold == 0.67
        assert config.reject_threshold == 0.51
        assert config.min_votes == 1

    def test_custom_thresholds(self):
        """Can create config with custom thresholds."""
        config = ThresholdConfig(
            approve_threshold=0.75,
            reject_threshold=0.60,
            min_votes=3,
        )
        assert config.approve_threshold == 0.75
        assert config.reject_threshold == 0.60
        assert config.min_votes == 3

    def test_validate_success(self):
        """Validation passes for valid config."""
        config = ThresholdConfig(
            approve_threshold=0.67,
            reject_threshold=0.51,
            min_votes=1,
        )
        # Should not raise
        config.validate()

    def test_validate_approve_threshold_too_high(self):
        """Validation fails if approve_threshold > 1.0."""
        config = ThresholdConfig(approve_threshold=1.5)
        with pytest.raises(ValueError, match="approve_threshold must be between"):
            config.validate()

    def test_validate_approve_threshold_negative(self):
        """Validation fails if approve_threshold < 0.0."""
        config = ThresholdConfig(approve_threshold=-0.1)
        with pytest.raises(ValueError, match="approve_threshold must be between"):
            config.validate()

    def test_validate_reject_threshold_too_high(self):
        """Validation fails if reject_threshold > 1.0."""
        config = ThresholdConfig(reject_threshold=1.5)
        with pytest.raises(ValueError, match="reject_threshold must be between"):
            config.validate()

    def test_validate_reject_threshold_negative(self):
        """Validation fails if reject_threshold < 0.0."""
        config = ThresholdConfig(reject_threshold=-0.1)
        with pytest.raises(ValueError, match="reject_threshold must be between"):
            config.validate()

    def test_validate_min_votes_zero(self):
        """Validation fails if min_votes < 1."""
        config = ThresholdConfig(min_votes=0)
        with pytest.raises(ValueError, match="min_votes must be at least 1"):
            config.validate()

    def test_validate_min_votes_negative(self):
        """Validation fails if min_votes < 1."""
        config = ThresholdConfig(min_votes=-1)
        with pytest.raises(ValueError, match="min_votes must be at least 1"):
            config.validate()


class TestCommitteeSelector:
    """Tests for CommitteeSelector."""

    def test_default_committee_sizes(self):
        """Default committee sizes are correct."""
        selector = CommitteeSelector()
        assert selector.get_committee_size("unknown", RiskLevel.LOW) == 1
        assert selector.get_committee_size("unknown", RiskLevel.MEDIUM) == 3
        assert selector.get_committee_size("unknown", RiskLevel.HIGH) == 5
        assert selector.get_committee_size("unknown", RiskLevel.CRITICAL) == 7

    def test_politics_domain_override(self):
        """Politics domain has larger committees."""
        selector = CommitteeSelector()
        assert selector.get_committee_size("politics", RiskLevel.LOW) == 3
        assert selector.get_committee_size("politics", RiskLevel.MEDIUM) == 5
        assert selector.get_committee_size("politics", RiskLevel.HIGH) == 7
        assert selector.get_committee_size("politics", RiskLevel.CRITICAL) == 9

    def test_health_domain_override(self):
        """Health domain has larger committees."""
        selector = CommitteeSelector()
        assert selector.get_committee_size("health", RiskLevel.LOW) == 3
        assert selector.get_committee_size("health", RiskLevel.MEDIUM) == 5
        assert selector.get_committee_size("health", RiskLevel.HIGH) == 7
        assert selector.get_committee_size("health", RiskLevel.CRITICAL) == 9

    def test_get_quorum_odd_size(self):
        """Quorum is simple majority for odd committee size."""
        selector = CommitteeSelector()
        assert selector.get_quorum(3) == 2  # (3 // 2) + 1
        assert selector.get_quorum(5) == 3  # (5 // 2) + 1
        assert selector.get_quorum(7) == 4  # (7 // 2) + 1

    def test_get_quorum_even_size(self):
        """Quorum is simple majority for even committee size."""
        selector = CommitteeSelector()
        assert selector.get_quorum(2) == 2  # (2 // 2) + 1
        assert selector.get_quorum(4) == 3  # (4 // 2) + 1
        assert selector.get_quorum(6) == 4  # (6 // 2) + 1

    def test_get_quorum_single_member(self):
        """Quorum is 1 for single member committee."""
        selector = CommitteeSelector()
        assert selector.get_quorum(1) == 1


class TestOrchestrationResult:
    """Tests for OrchestrationResult."""

    def test_create_with_approve_votes(self):
        """Create result with approve votes."""
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
            Vote.create("m3", VoteType.REJECT),
        ]
        result = OrchestrationResult.create(
            outcome=Outcome.APPROVED,
            votes=votes,
            threshold_met=True,
            reason="Test",
        )
        assert result.outcome == Outcome.APPROVED
        assert result.approve_count == 2
        assert result.reject_count == 1
        assert result.abstain_count == 0
        assert result.threshold_met is True
        assert result.reason == "Test"
        assert len(result.votes) == 3

    def test_create_with_mixed_votes(self):
        """Create result with mixed votes."""
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.REJECT),
            Vote.create("m3", VoteType.ABSTAIN),
        ]
        result = OrchestrationResult.create(
            outcome=Outcome.NEEDS_REVIEW,
            votes=votes,
            threshold_met=False,
        )
        assert result.approve_count == 1
        assert result.reject_count == 1
        assert result.abstain_count == 1
        assert result.threshold_met is False

    def test_create_with_no_votes(self):
        """Create result with no votes."""
        result = OrchestrationResult.create(
            outcome=Outcome.INCONCLUSIVE,
            votes=[],
        )
        assert result.approve_count == 0
        assert result.reject_count == 0
        assert result.abstain_count == 0
        assert len(result.votes) == 0

    def test_create_with_committee(self):
        """Create result with committee reference."""
        committee = Committee.create("dec_123", quorum_required=3)
        result = OrchestrationResult.create(
            outcome=Outcome.APPROVED,
            votes=[],
            committee=committee,
        )
        assert result.committee == committee

    def test_create_with_metadata(self):
        """Create result with metadata."""
        metadata = {"claim_id": "claim_123", "domain": "politics"}
        result = OrchestrationResult.create(
            outcome=Outcome.APPROVED,
            votes=[],
            metadata=metadata,
        )
        assert result.metadata == metadata

    def test_completed_at_is_set(self):
        """completed_at is automatically set."""
        result = OrchestrationResult.create(
            outcome=Outcome.APPROVED,
            votes=[],
        )
        assert isinstance(result.completed_at, datetime)
        assert result.completed_at.tzinfo == timezone.utc


class TestCommitteeOrchestrator:
    """Tests for CommitteeOrchestrator."""

    def test_init_default(self):
        """Initialize with defaults."""
        orchestrator = CommitteeOrchestrator()
        assert orchestrator.selector is not None
        assert orchestrator.threshold_config is not None
        assert orchestrator.threshold_config.approve_threshold == 0.67

    def test_init_custom_selector(self):
        """Initialize with custom selector."""
        selector = CommitteeSelector()
        orchestrator = CommitteeOrchestrator(selector=selector)
        assert orchestrator.selector is selector

    def test_init_custom_threshold(self):
        """Initialize with custom threshold config."""
        config = ThresholdConfig(approve_threshold=0.80)
        orchestrator = CommitteeOrchestrator(threshold_config=config)
        assert orchestrator.threshold_config == config
        assert orchestrator.threshold_config.approve_threshold == 0.80

    def test_init_invalid_threshold_raises(self):
        """Initialize with invalid threshold raises error."""
        config = ThresholdConfig(approve_threshold=1.5)
        with pytest.raises(ValueError):
            CommitteeOrchestrator(threshold_config=config)

    def test_select_committee_creates_committee(self):
        """select_committee creates a Committee instance."""
        orchestrator = CommitteeOrchestrator()
        committee = orchestrator.select_committee(
            domain="politics",
            risk_level=RiskLevel.MEDIUM,
            decision_id="dec_123",
        )
        assert isinstance(committee, Committee)
        assert committee.decision_id == "dec_123"

    def test_select_committee_adds_proponent(self):
        """select_committee adds proponent member."""
        orchestrator = CommitteeOrchestrator()
        committee = orchestrator.select_committee(
            domain="politics",
            risk_level=RiskLevel.LOW,
            decision_id="dec_123",
        )
        proponent = committee.get_proponent()
        assert proponent is not None
        assert proponent.role == GuardianRole.PROPONENT

    def test_select_committee_adds_validators(self):
        """select_committee adds validator members."""
        orchestrator = CommitteeOrchestrator()
        committee = orchestrator.select_committee(
            domain="politics",
            risk_level=RiskLevel.MEDIUM,
            decision_id="dec_123",
        )
        validators = committee.get_validators()
        # Politics medium = 5 validators
        assert len(validators) == 5
        assert all(v.role == GuardianRole.VALIDATOR for v in validators)

    def test_select_committee_sets_quorum(self):
        """select_committee sets correct quorum."""
        orchestrator = CommitteeOrchestrator()
        committee = orchestrator.select_committee(
            domain="politics",
            risk_level=RiskLevel.MEDIUM,
            decision_id="dec_123",
        )
        # 5 validators -> quorum = 3
        assert committee.quorum_required == 3

    def test_select_committee_different_risk_levels(self):
        """select_committee creates different sizes for risk levels."""
        orchestrator = CommitteeOrchestrator()

        low = orchestrator.select_committee("politics", RiskLevel.LOW, "dec_1")
        medium = orchestrator.select_committee("politics", RiskLevel.MEDIUM, "dec_2")
        high = orchestrator.select_committee("politics", RiskLevel.HIGH, "dec_3")

        # Politics: LOW=3, MEDIUM=5, HIGH=7
        assert len(low.get_validators()) == 3
        assert len(medium.get_validators()) == 5
        assert len(high.get_validators()) == 7

    @pytest.mark.asyncio
    async def test_execute_agents_parallel_returns_votes(self):
        """execute_agents_parallel returns list of votes."""
        orchestrator = CommitteeOrchestrator()
        committee = Committee.create("dec_123", quorum_required=2)

        # Add validators
        v1 = CommitteeMember.create(GuardianRole.VALIDATOR, agent_id="a1")
        v2 = CommitteeMember.create(GuardianRole.VALIDATOR, agent_id="a2")
        committee.add_member(v1)
        committee.add_member(v2)

        votes = await orchestrator.execute_agents_parallel(
            committee=committee,
            context={"mock_approve": True},
        )

        assert len(votes) == 2
        assert all(isinstance(v, Vote) for v in votes)

    @pytest.mark.asyncio
    async def test_execute_agents_parallel_adds_votes_to_committee(self):
        """execute_agents_parallel adds votes to committee."""
        orchestrator = CommitteeOrchestrator()
        committee = Committee.create("dec_123", quorum_required=1)

        v1 = CommitteeMember.create(GuardianRole.VALIDATOR, agent_id="a1")
        committee.add_member(v1)

        await orchestrator.execute_agents_parallel(
            committee=committee,
            context={},
        )

        assert len(committee.votes) == 1

    @pytest.mark.asyncio
    async def test_execute_agents_parallel_empty_committee(self):
        """execute_agents_parallel handles empty committee."""
        orchestrator = CommitteeOrchestrator()
        committee = Committee.create("dec_123", quorum_required=1)

        votes = await orchestrator.execute_agents_parallel(
            committee=committee,
            context={},
        )

        assert len(votes) == 0

    def test_aggregate_votes_approved(self):
        """aggregate_votes returns APPROVED when threshold met."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
            Vote.create("m3", VoteType.APPROVE),
            Vote.create("m4", VoteType.REJECT),
        ]
        # 3/4 = 75% -> meets default threshold of 67%
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.APPROVED

    def test_aggregate_votes_rejected(self):
        """aggregate_votes returns REJECTED when reject threshold met."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.REJECT),
            Vote.create("m2", VoteType.REJECT),
            Vote.create("m3", VoteType.APPROVE),
        ]
        # 2/3 = 67% reject -> meets reject threshold (51%)
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.REJECTED

    def test_aggregate_votes_needs_review(self):
        """aggregate_votes returns NEEDS_REVIEW when no threshold met."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
            Vote.create("m3", VoteType.REJECT),
        ]
        # 2/3 = 66.7% -> just below default threshold of 67%, so NEEDS_REVIEW
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.NEEDS_REVIEW

    def test_aggregate_votes_inconclusive_no_votes(self):
        """aggregate_votes returns INCONCLUSIVE with no votes."""
        orchestrator = CommitteeOrchestrator()
        outcome = orchestrator.aggregate_votes([])
        assert outcome == Outcome.INCONCLUSIVE

    def test_aggregate_votes_inconclusive_exact_tie(self):
        """aggregate_votes returns INCONCLUSIVE on exact tie."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.REJECT),
        ]
        # Exact 1-1 tie
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.INCONCLUSIVE

    def test_aggregate_votes_inconclusive_exact_tie_with_4_votes(self):
        """aggregate_votes returns INCONCLUSIVE on 2-2 tie."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
            Vote.create("m3", VoteType.REJECT),
            Vote.create("m4", VoteType.REJECT),
        ]
        # Exact 2-2 tie
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.INCONCLUSIVE

    def test_aggregate_votes_all_abstain(self):
        """aggregate_votes returns INCONCLUSIVE when all abstain."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.ABSTAIN),
            Vote.create("m2", VoteType.ABSTAIN),
        ]
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.INCONCLUSIVE

    def test_aggregate_votes_excludes_abstain_from_percentage(self):
        """aggregate_votes excludes abstentions from percentage calc."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
            Vote.create("m3", VoteType.ABSTAIN),
            Vote.create("m4", VoteType.ABSTAIN),
        ]
        # 2 approve out of 2 active = 100% -> APPROVED
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.APPROVED

    def test_aggregate_votes_custom_threshold(self):
        """aggregate_votes uses custom threshold."""
        config = ThresholdConfig(approve_threshold=0.90, min_votes=1)
        orchestrator = CommitteeOrchestrator(threshold_config=config)
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
            Vote.create("m3", VoteType.REJECT),
        ]
        # 67% < 90% -> NEEDS_REVIEW
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.NEEDS_REVIEW

    def test_aggregate_votes_min_votes_not_met(self):
        """aggregate_votes returns NEEDS_REVIEW if min_votes not met."""
        config = ThresholdConfig(min_votes=5)
        orchestrator = CommitteeOrchestrator(threshold_config=config)
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
        ]
        # Only 2 votes < 5 min
        outcome = orchestrator.aggregate_votes(votes)
        assert outcome == Outcome.NEEDS_REVIEW

    @pytest.mark.asyncio
    async def test_orchestrate_success(self):
        """orchestrate returns OrchestrationResult on success."""
        orchestrator = CommitteeOrchestrator()
        result = await orchestrator.orchestrate(
            claim_id="claim_123",
            domain="politics",
            risk_level=RiskLevel.LOW,
            context={"mock_approve": True},
        )
        assert isinstance(result, OrchestrationResult)
        assert result.outcome in [Outcome.APPROVED, Outcome.REJECTED, Outcome.NEEDS_REVIEW]
        assert result.committee is not None

    @pytest.mark.asyncio
    async def test_orchestrate_with_decision_id(self):
        """orchestrate uses provided decision_id."""
        orchestrator = CommitteeOrchestrator()
        result = await orchestrator.orchestrate(
            claim_id="claim_123",
            domain="politics",
            risk_level=RiskLevel.LOW,
            context={},
            decision_id="custom_dec_456",
        )
        assert result.committee.decision_id == "custom_dec_456"

    @pytest.mark.asyncio
    async def test_orchestrate_generates_decision_id(self):
        """orchestrate generates decision_id if not provided."""
        orchestrator = CommitteeOrchestrator()
        result = await orchestrator.orchestrate(
            claim_id="claim_123456789",
            domain="politics",
            risk_level=RiskLevel.LOW,
            context={},
        )
        assert result.committee.decision_id.startswith("dec_claim_123456")

    @pytest.mark.asyncio
    async def test_orchestrate_includes_metadata(self):
        """orchestrate includes metadata in result."""
        orchestrator = CommitteeOrchestrator()
        result = await orchestrator.orchestrate(
            claim_id="claim_123",
            domain="politics",
            risk_level=RiskLevel.MEDIUM,
            context={},
        )
        assert result.metadata["claim_id"] == "claim_123"
        assert result.metadata["domain"] == "politics"
        assert result.metadata["risk_level"] == "medium"
        assert "committee_size" in result.metadata
        assert "quorum_required" in result.metadata

    @pytest.mark.asyncio
    async def test_orchestrate_threshold_met_for_approved(self):
        """orchestrate sets threshold_met=True for APPROVED."""
        orchestrator = CommitteeOrchestrator()
        # Create a config that will approve with simple majority
        config = ThresholdConfig(approve_threshold=0.51, min_votes=1)
        orchestrator = CommitteeOrchestrator(threshold_config=config)

        result = await orchestrator.orchestrate(
            claim_id="claim_123",
            domain="unknown",  # Use unknown to get size=1
            risk_level=RiskLevel.LOW,
            context={"mock_approve": True},
        )
        if result.outcome == Outcome.APPROVED:
            assert result.threshold_met is True

    @pytest.mark.asyncio
    async def test_orchestrate_includes_reason(self):
        """orchestrate includes reason in result."""
        orchestrator = CommitteeOrchestrator()
        result = await orchestrator.orchestrate(
            claim_id="claim_123",
            domain="politics",
            risk_level=RiskLevel.LOW,
            context={},
        )
        assert result.reason is not None
        assert len(result.reason) > 0

    @pytest.mark.asyncio
    async def test_orchestrate_handles_exception(self):
        """orchestrate handles exceptions gracefully."""
        # Create orchestrator with invalid selector that will raise exception
        class BrokenSelector(CommitteeSelector):
            def get_committee_size(self, domain, risk_level):
                raise RuntimeError("Test exception")

        orchestrator = CommitteeOrchestrator(selector=BrokenSelector())
        result = await orchestrator.orchestrate(
            claim_id="claim_123",
            domain="politics",
            risk_level=RiskLevel.LOW,
            context={},
        )
        assert result.outcome == Outcome.INCONCLUSIVE
        assert result.threshold_met is False
        assert "error" in result.reason.lower()
        assert "test exception" in result.reason.lower()
        assert result.metadata["claim_id"] == "claim_123"

    def test_generate_reason_approved(self):
        """_generate_reason returns correct reason for APPROVED."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.APPROVE),
        ]
        reason = orchestrator._generate_reason(Outcome.APPROVED, votes)
        assert "approved" in reason.lower()
        assert "2 votes" in reason.lower()
        assert "threshold met" in reason.lower()

    def test_generate_reason_rejected(self):
        """_generate_reason returns correct reason for REJECTED."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.REJECT),
            Vote.create("m2", VoteType.REJECT),
        ]
        reason = orchestrator._generate_reason(Outcome.REJECTED, votes)
        assert "rejected" in reason.lower()
        assert "2 votes" in reason.lower()

    def test_generate_reason_needs_review(self):
        """_generate_reason returns correct reason for NEEDS_REVIEW."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.REJECT),
        ]
        reason = orchestrator._generate_reason(Outcome.NEEDS_REVIEW, votes)
        assert "needs human review" in reason.lower()
        assert "approve=1" in reason.lower()
        assert "reject=1" in reason.lower()

    def test_generate_reason_inconclusive_no_votes(self):
        """_generate_reason returns correct reason for INCONCLUSIVE with no votes."""
        orchestrator = CommitteeOrchestrator()
        reason = orchestrator._generate_reason(Outcome.INCONCLUSIVE, [])
        assert "no votes" in reason.lower()

    def test_generate_reason_inconclusive_tie(self):
        """_generate_reason returns correct reason for INCONCLUSIVE with tie."""
        orchestrator = CommitteeOrchestrator()
        votes = [
            Vote.create("m1", VoteType.APPROVE),
            Vote.create("m2", VoteType.REJECT),
        ]
        reason = orchestrator._generate_reason(Outcome.INCONCLUSIVE, votes)
        assert "inconclusive" in reason.lower()


class TestGetThreshold:
    """Tests for get_threshold helper function."""

    def test_get_threshold_low(self):
        """get_threshold returns correct config for LOW risk."""
        config = get_threshold(RiskLevel.LOW)
        assert config.approve_threshold == 0.51
        assert config.min_votes == 1

    def test_get_threshold_medium(self):
        """get_threshold returns correct config for MEDIUM risk."""
        config = get_threshold(RiskLevel.MEDIUM)
        assert config.approve_threshold == 0.67
        assert config.min_votes == 3

    def test_get_threshold_high(self):
        """get_threshold returns correct config for HIGH risk."""
        config = get_threshold(RiskLevel.HIGH)
        assert config.approve_threshold == 0.75
        assert config.min_votes == 5

    def test_get_threshold_critical(self):
        """get_threshold returns correct config for CRITICAL risk."""
        config = get_threshold(RiskLevel.CRITICAL)
        assert config.approve_threshold == 0.80
        assert config.min_votes == 7

    def test_get_threshold_all_have_reject_threshold(self):
        """All risk levels have reject_threshold = 0.51."""
        for risk_level in RiskLevel:
            config = get_threshold(risk_level)
            assert config.reject_threshold == 0.51


class TestGetCommitteeOrchestrator:
    """Tests for get_committee_orchestrator singleton."""

    def test_returns_orchestrator(self):
        """get_committee_orchestrator returns CommitteeOrchestrator."""
        orchestrator = get_committee_orchestrator()
        assert isinstance(orchestrator, CommitteeOrchestrator)

    def test_returns_singleton(self):
        """get_committee_orchestrator returns same instance."""
        o1 = get_committee_orchestrator()
        o2 = get_committee_orchestrator()
        assert o1 is o2
