"""
Tests for Guardian Committee Management — S37

Tests for CommitteeSelector, CommitteeManager, and related functionality.
"""

import pytest

from app.guardian.committee import (
    CommitteeConfig,
    CommitteeManager,
    CommitteeSelector,
    MemberPool,
    RiskLevel,
    COMMITTEE_SIZE_RULES,
    create_manager,
    create_selector,
)
from app.guardian.models import Committee, CommitteeMember, Vote, VoteType
from app.guardian.roles import GuardianRole


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_all_risk_levels_defined(self):
        """All expected risk levels are defined."""
        expected = ["low", "medium", "high"]
        actual = [r.value for r in RiskLevel]
        assert set(actual) == set(expected)

    def test_risk_level_values(self):
        """Risk level values match expected strings."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"

    def test_risk_level_is_string_enum(self):
        """RiskLevel is a string enum."""
        assert isinstance(RiskLevel.LOW, str)
        assert RiskLevel.LOW == "low"


class TestCommitteeSizeRules:
    """Tests for committee size rules."""

    def test_low_risk_size(self):
        """LOW risk requires 3 members."""
        assert COMMITTEE_SIZE_RULES[RiskLevel.LOW] == 3

    def test_medium_risk_size(self):
        """MEDIUM risk requires 5 members."""
        assert COMMITTEE_SIZE_RULES[RiskLevel.MEDIUM] == 5

    def test_high_risk_size(self):
        """HIGH risk requires 7 members."""
        assert COMMITTEE_SIZE_RULES[RiskLevel.HIGH] == 7

    def test_all_risk_levels_have_size(self):
        """All risk levels have a defined size."""
        for risk_level in RiskLevel:
            assert risk_level in COMMITTEE_SIZE_RULES


class TestCommitteeConfig:
    """Tests for CommitteeConfig dataclass."""

    def test_create_minimal_config(self):
        """Create config with minimal parameters."""
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )
        assert config.domain == "politics"
        assert config.risk_level == RiskLevel.LOW
        assert config.quorum_required == 2
        assert config.require_proponent is True
        assert config.require_reviewer is False
        assert config.metadata == {}

    def test_create_full_config(self):
        """Create config with all parameters."""
        config = CommitteeConfig(
            domain="health",
            risk_level=RiskLevel.HIGH,
            quorum_required=5,
            require_proponent=False,
            require_reviewer=True,
            metadata={"source": "test"},
        )
        assert config.domain == "health"
        assert config.risk_level == RiskLevel.HIGH
        assert config.quorum_required == 5
        assert config.require_proponent is False
        assert config.require_reviewer is True
        assert config.metadata == {"source": "test"}


class TestMemberPool:
    """Tests for MemberPool dataclass."""

    def test_create_empty_pool(self):
        """Create empty member pool."""
        pool = MemberPool()
        assert pool.validators == []
        assert pool.reviewers == []
        assert pool.arbiters == []

    def test_create_pool_with_members(self):
        """Create pool with members."""
        pool = MemberPool(
            validators=["v1", "v2", "v3"],
            reviewers=["r1"],
            arbiters=["a1"],
        )
        assert pool.validators == ["v1", "v2", "v3"]
        assert pool.reviewers == ["r1"]
        assert pool.arbiters == ["a1"]

    def test_has_validators_true(self):
        """has_validators returns True when enough validators."""
        pool = MemberPool(validators=["v1", "v2", "v3"])
        assert pool.has_validators(3) is True
        assert pool.has_validators(2) is True
        assert pool.has_validators(1) is True

    def test_has_validators_false(self):
        """has_validators returns False when not enough validators."""
        pool = MemberPool(validators=["v1", "v2"])
        assert pool.has_validators(3) is False
        assert pool.has_validators(10) is False

    def test_has_reviewers_true(self):
        """has_reviewers returns True when enough reviewers."""
        pool = MemberPool(reviewers=["r1", "r2"])
        assert pool.has_reviewers(1) is True
        assert pool.has_reviewers(2) is True

    def test_has_reviewers_false(self):
        """has_reviewers returns False when not enough reviewers."""
        pool = MemberPool(reviewers=["r1"])
        assert pool.has_reviewers(2) is False

    def test_has_arbiters_true(self):
        """has_arbiters returns True when enough arbiters."""
        pool = MemberPool(arbiters=["a1"])
        assert pool.has_arbiters(1) is True

    def test_has_arbiters_false(self):
        """has_arbiters returns False when not enough arbiters."""
        pool = MemberPool(arbiters=[])
        assert pool.has_arbiters(1) is False


class TestCommitteeSelector:
    """Tests for CommitteeSelector."""

    def test_init_with_default_pool(self):
        """Initialize selector with default pool."""
        selector = CommitteeSelector()
        assert selector.member_pool is not None
        assert len(selector.member_pool.validators) == 7
        assert len(selector.member_pool.reviewers) == 2
        assert len(selector.member_pool.arbiters) == 1

    def test_init_with_custom_pool(self):
        """Initialize selector with custom pool."""
        pool = MemberPool(
            validators=["custom_v1", "custom_v2"],
            reviewers=["custom_r1"],
        )
        selector = CommitteeSelector(member_pool=pool)
        assert selector.member_pool == pool

    def test_select_members_low_risk(self):
        """Select members for LOW risk (3 validators)."""
        selector = CommitteeSelector()
        members = selector.select_members(
            domain="politics",
            risk_level=RiskLevel.LOW,
        )
        assert len(members) == 3
        assert all(isinstance(m, str) for m in members)

    def test_select_members_medium_risk(self):
        """Select members for MEDIUM risk (5 validators)."""
        selector = CommitteeSelector()
        members = selector.select_members(
            domain="politics",
            risk_level=RiskLevel.MEDIUM,
        )
        assert len(members) == 5

    def test_select_members_high_risk(self):
        """Select members for HIGH risk (7 validators)."""
        selector = CommitteeSelector()
        members = selector.select_members(
            domain="politics",
            risk_level=RiskLevel.HIGH,
        )
        assert len(members) == 7

    def test_select_members_with_size_override(self):
        """Select members with explicit size override."""
        selector = CommitteeSelector()
        members = selector.select_members(
            domain="politics",
            risk_level=RiskLevel.LOW,
            size=5,  # Override LOW default of 3
        )
        assert len(members) == 5

    def test_select_members_insufficient_pool(self):
        """Raise ValueError when pool has insufficient validators."""
        pool = MemberPool(validators=["v1", "v2"])  # Only 2 validators
        selector = CommitteeSelector(member_pool=pool)

        with pytest.raises(ValueError, match="Insufficient validators"):
            selector.select_members(
                domain="politics",
                risk_level=RiskLevel.LOW,  # Needs 3
            )

    def test_select_members_round_robin(self):
        """Members are selected in round-robin order."""
        pool = MemberPool(
            validators=["v1", "v2", "v3", "v4", "v5", "v6", "v7"],
        )
        selector = CommitteeSelector(member_pool=pool)

        members = selector.select_members(
            domain="politics",
            risk_level=RiskLevel.LOW,
            size=3,
        )
        assert members == ["v1", "v2", "v3"]

    def test_get_committee_size_low(self):
        """Get size for LOW risk."""
        selector = CommitteeSelector()
        assert selector.get_committee_size(RiskLevel.LOW) == 3

    def test_get_committee_size_medium(self):
        """Get size for MEDIUM risk."""
        selector = CommitteeSelector()
        assert selector.get_committee_size(RiskLevel.MEDIUM) == 5

    def test_get_committee_size_high(self):
        """Get size for HIGH risk."""
        selector = CommitteeSelector()
        assert selector.get_committee_size(RiskLevel.HIGH) == 7


class TestCommitteeManager:
    """Tests for CommitteeManager."""

    def test_init_with_default_selector(self):
        """Initialize manager with default selector."""
        manager = CommitteeManager()
        assert manager.selector is not None
        assert isinstance(manager.selector, CommitteeSelector)

    def test_init_with_custom_selector(self):
        """Initialize manager with custom selector."""
        selector = CommitteeSelector()
        manager = CommitteeManager(selector=selector)
        assert manager.selector == selector

    def test_create_committee_minimal(self):
        """Create committee with minimal config."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        assert committee.id.startswith("com_")
        assert committee.decision_id == "dec_123"
        assert committee.quorum_required == 2
        # Should have 1 proponent + 3 validators = 4 members
        assert len(committee.members) == 4

        # Check proponent
        proponent = committee.get_proponent()
        assert proponent is not None
        assert proponent.role == GuardianRole.PROPONENT

        # Check validators
        validators = committee.get_validators()
        assert len(validators) == 3

    def test_create_committee_with_proponent_agent(self):
        """Create committee with proponent agent ID."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
            proponent_agent_id="agent_999",
        )

        proponent = committee.get_proponent()
        assert proponent.agent_id == "agent_999"

    def test_create_committee_without_proponent(self):
        """Create committee without proponent."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
            require_proponent=False,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Should have only 3 validators
        assert len(committee.members) == 3
        assert committee.get_proponent() is None

    def test_create_committee_with_reviewer(self):
        """Create committee with reviewer."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
            require_reviewer=True,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Should have 1 proponent + 3 validators + 1 reviewer = 5 members
        assert len(committee.members) == 5

        reviewer = committee.get_reviewer()
        assert reviewer is not None
        assert reviewer.role == GuardianRole.REVIEWER

    def test_create_committee_medium_risk(self):
        """Create committee for MEDIUM risk."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.MEDIUM,
            quorum_required=3,
        )

        committee = manager.create_committee(
            decision_id="dec_456",
            config=config,
        )

        # Should have 1 proponent + 5 validators = 6 members
        assert len(committee.members) == 6
        validators = committee.get_validators()
        assert len(validators) == 5

    def test_create_committee_high_risk(self):
        """Create committee for HIGH risk."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.HIGH,
            quorum_required=4,
        )

        committee = manager.create_committee(
            decision_id="dec_789",
            config=config,
        )

        # Should have 1 proponent + 7 validators = 8 members
        assert len(committee.members) == 8
        validators = committee.get_validators()
        assert len(validators) == 7

    def test_get_committee_exists(self):
        """Get committee that exists."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        created = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        retrieved = manager.get_committee(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.decision_id == created.decision_id

    def test_get_committee_not_exists(self):
        """Get committee that doesn't exist returns None."""
        manager = CommitteeManager()
        retrieved = manager.get_committee("nonexistent_id")
        assert retrieved is None

    def test_record_votes_success(self):
        """Record votes for a committee."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Create votes
        member = committee.members[0]
        votes = [
            Vote.create(
                member_id=member.id,
                vote_type=VoteType.APPROVE,
                reason="Good evidence",
            ),
        ]

        manager.record_votes(committee.id, votes)

        # Verify votes recorded
        assert len(committee.votes) == 1
        retrieved_votes = manager.get_votes(committee.id)
        assert len(retrieved_votes) == 1
        assert retrieved_votes[0].member_id == member.id

    def test_record_votes_committee_not_found(self):
        """Record votes raises ValueError if committee not found."""
        manager = CommitteeManager()
        vote = Vote.create(
            member_id="mem_123",
            vote_type=VoteType.APPROVE,
        )

        with pytest.raises(ValueError, match="Committee .* not found"):
            manager.record_votes("nonexistent_id", [vote])

    def test_record_vote_success(self):
        """Record a single vote for a committee."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        member = committee.members[0]
        vote = Vote.create(
            member_id=member.id,
            vote_type=VoteType.APPROVE,
        )

        manager.record_vote(committee.id, member.id, vote)

        assert len(committee.votes) == 1
        assert committee.votes[0].member_id == member.id

    def test_record_vote_committee_not_found(self):
        """Record vote raises ValueError if committee not found."""
        manager = CommitteeManager()
        vote = Vote.create(
            member_id="mem_123",
            vote_type=VoteType.APPROVE,
        )

        with pytest.raises(ValueError, match="Committee .* not found"):
            manager.record_vote("nonexistent_id", "mem_123", vote)

    def test_record_vote_member_not_found(self):
        """Record vote raises ValueError if member not in committee."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        vote = Vote.create(
            member_id="nonexistent_member",
            vote_type=VoteType.APPROVE,
        )

        with pytest.raises(ValueError, match="Member .* not found"):
            manager.record_vote(committee.id, "nonexistent_member", vote)

    def test_get_votes_empty(self):
        """Get votes returns empty list for committee with no votes."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        votes = manager.get_votes(committee.id)
        assert votes == []

    def test_get_votes_nonexistent_committee(self):
        """Get votes returns empty list for nonexistent committee."""
        manager = CommitteeManager()
        votes = manager.get_votes("nonexistent_id")
        assert votes == []

    def test_has_quorum_true(self):
        """has_quorum returns True when quorum reached."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Add 2 votes to reach quorum of 2
        member1 = committee.members[0]
        member2 = committee.members[1]

        votes = [
            Vote.create(member_id=member1.id, vote_type=VoteType.APPROVE),
            Vote.create(member_id=member2.id, vote_type=VoteType.APPROVE),
        ]

        manager.record_votes(committee.id, votes)

        assert manager.has_quorum(committee.id) is True

    def test_has_quorum_false(self):
        """has_quorum returns False when quorum not reached."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Add only 1 vote, quorum is 2
        member = committee.members[0]
        vote = Vote.create(member_id=member.id, vote_type=VoteType.APPROVE)
        manager.record_votes(committee.id, [vote])

        assert manager.has_quorum(committee.id) is False

    def test_has_quorum_committee_not_found(self):
        """has_quorum raises ValueError if committee not found."""
        manager = CommitteeManager()

        with pytest.raises(ValueError, match="Committee .* not found"):
            manager.has_quorum("nonexistent_id")

    def test_get_decision_approve(self):
        """get_decision returns 'approve' when more approve votes."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=3,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Add 2 approve, 1 reject
        members = committee.members[:3]
        votes = [
            Vote.create(member_id=members[0].id, vote_type=VoteType.APPROVE),
            Vote.create(member_id=members[1].id, vote_type=VoteType.APPROVE),
            Vote.create(member_id=members[2].id, vote_type=VoteType.REJECT),
        ]

        manager.record_votes(committee.id, votes)

        decision = manager.get_decision(committee.id)
        assert decision == "approve"

    def test_get_decision_reject(self):
        """get_decision returns 'reject' when more reject votes."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=3,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Add 2 reject, 1 approve
        members = committee.members[:3]
        votes = [
            Vote.create(member_id=members[0].id, vote_type=VoteType.REJECT),
            Vote.create(member_id=members[1].id, vote_type=VoteType.REJECT),
            Vote.create(member_id=members[2].id, vote_type=VoteType.APPROVE),
        ]

        manager.record_votes(committee.id, votes)

        decision = manager.get_decision(committee.id)
        assert decision == "reject"

    def test_get_decision_no_quorum(self):
        """get_decision returns None when quorum not reached."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=3,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Add only 1 vote, quorum is 3
        member = committee.members[0]
        vote = Vote.create(member_id=member.id, vote_type=VoteType.APPROVE)
        manager.record_votes(committee.id, [vote])

        decision = manager.get_decision(committee.id)
        assert decision is None

    def test_get_decision_tie(self):
        """get_decision returns None on tie."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        # Add 1 approve, 1 reject (tie)
        members = committee.members[:2]
        votes = [
            Vote.create(member_id=members[0].id, vote_type=VoteType.APPROVE),
            Vote.create(member_id=members[1].id, vote_type=VoteType.REJECT),
        ]

        manager.record_votes(committee.id, votes)

        decision = manager.get_decision(committee.id)
        assert decision is None

    def test_get_decision_committee_not_found(self):
        """get_decision raises ValueError if committee not found."""
        manager = CommitteeManager()

        with pytest.raises(ValueError, match="Committee .* not found"):
            manager.get_decision("nonexistent_id")

    def test_clear(self):
        """clear removes all committees and votes."""
        manager = CommitteeManager()
        config = CommitteeConfig(
            domain="politics",
            risk_level=RiskLevel.LOW,
            quorum_required=2,
        )

        # Create committee and add vote
        committee = manager.create_committee(
            decision_id="dec_123",
            config=config,
        )

        member = committee.members[0]
        vote = Vote.create(member_id=member.id, vote_type=VoteType.APPROVE)
        manager.record_votes(committee.id, [vote])

        # Clear
        manager.clear()

        # Verify cleared
        assert manager.get_committee(committee.id) is None
        assert manager.get_votes(committee.id) == []


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_selector_default(self):
        """create_selector creates selector with default pool."""
        selector = create_selector()
        assert isinstance(selector, CommitteeSelector)
        assert selector.member_pool is not None

    def test_create_selector_custom_pool(self):
        """create_selector creates selector with custom pool."""
        pool = MemberPool(validators=["v1"])
        selector = create_selector(member_pool=pool)
        assert selector.member_pool == pool

    def test_create_manager_default(self):
        """create_manager creates manager with default selector."""
        manager = create_manager()
        assert isinstance(manager, CommitteeManager)
        assert manager.selector is not None

    def test_create_manager_custom_selector(self):
        """create_manager creates manager with custom selector."""
        selector = CommitteeSelector()
        manager = create_manager(selector=selector)
        assert manager.selector == selector
