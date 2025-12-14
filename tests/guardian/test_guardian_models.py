"""
Tests for Guardian Models — S37

Tests for DecisionStatus, VoteType, CommitteeMember, Vote, Committee,
Decision, and DecisionBlock.
"""

import pytest
from datetime import datetime, timezone, timedelta

from app.guardian.models import (
    DecisionStatus,
    VoteType,
    CommitteeMember,
    Vote,
    Committee,
    Decision,
    DecisionBlock,
)
from app.guardian.roles import GuardianRole


class TestDecisionStatus:
    """Tests for DecisionStatus enum."""

    def test_all_statuses_defined(self):
        """All expected statuses are defined."""
        expected = [
            "pending", "validating", "awaiting_review", "awaiting_quorum",
            "approved", "rejected", "escalated", "timed_out", "cancelled"
        ]
        actual = [s.value for s in DecisionStatus]
        assert set(actual) == set(expected)

    def test_status_values(self):
        """Status values match expected strings."""
        assert DecisionStatus.PENDING.value == "pending"
        assert DecisionStatus.APPROVED.value == "approved"
        assert DecisionStatus.REJECTED.value == "rejected"

    def test_status_is_string_enum(self):
        """DecisionStatus is a string enum."""
        assert isinstance(DecisionStatus.PENDING, str)
        assert DecisionStatus.PENDING == "pending"


class TestVoteType:
    """Tests for VoteType enum."""

    def test_all_vote_types_defined(self):
        """All expected vote types are defined."""
        expected = ["approve", "reject", "abstain"]
        actual = [v.value for v in VoteType]
        assert set(actual) == set(expected)

    def test_vote_type_values(self):
        """Vote type values match expected strings."""
        assert VoteType.APPROVE.value == "approve"
        assert VoteType.REJECT.value == "reject"
        assert VoteType.ABSTAIN.value == "abstain"


class TestCommitteeMember:
    """Tests for CommitteeMember dataclass."""

    def test_create_member_with_agent(self):
        """Create member with agent ID."""
        member = CommitteeMember.create(
            role=GuardianRole.VALIDATOR,
            agent_id="agent_123",
        )
        assert member.id.startswith("mem_")
        assert member.role == GuardianRole.VALIDATOR
        assert member.agent_id == "agent_123"
        assert member.user_id is None
        assert isinstance(member.assigned_at, datetime)

    def test_create_member_with_user(self):
        """Create member with user ID."""
        member = CommitteeMember.create(
            role=GuardianRole.REVIEWER,
            user_id="user_456",
        )
        assert member.role == GuardianRole.REVIEWER
        assert member.user_id == "user_456"
        assert member.agent_id is None

    def test_create_proponent(self):
        """Create proponent member."""
        member = CommitteeMember.create(role=GuardianRole.PROPONENT)
        assert member.role == GuardianRole.PROPONENT

    def test_unique_ids(self):
        """Each member gets a unique ID."""
        m1 = CommitteeMember.create(role=GuardianRole.VALIDATOR)
        m2 = CommitteeMember.create(role=GuardianRole.VALIDATOR)
        assert m1.id != m2.id


class TestVote:
    """Tests for Vote dataclass."""

    def test_create_approve_vote(self):
        """Create approve vote."""
        vote = Vote.create(
            member_id="mem_123",
            vote_type=VoteType.APPROVE,
            reason="Evidence is strong",
            confidence=0.95,
        )
        assert vote.id.startswith("vot_")
        assert vote.member_id == "mem_123"
        assert vote.vote_type == VoteType.APPROVE
        assert vote.reason == "Evidence is strong"
        assert vote.confidence == 0.95
        assert isinstance(vote.voted_at, datetime)

    def test_create_reject_vote(self):
        """Create reject vote."""
        vote = Vote.create(
            member_id="mem_456",
            vote_type=VoteType.REJECT,
        )
        assert vote.vote_type == VoteType.REJECT
        assert vote.reason is None
        assert vote.confidence == 1.0  # Default

    def test_create_abstain_vote(self):
        """Create abstain vote."""
        vote = Vote.create(
            member_id="mem_789",
            vote_type=VoteType.ABSTAIN,
            confidence=0.5,
        )
        assert vote.vote_type == VoteType.ABSTAIN
        assert vote.confidence == 0.5

    def test_unique_vote_ids(self):
        """Each vote gets a unique ID."""
        v1 = Vote.create(member_id="m1", vote_type=VoteType.APPROVE)
        v2 = Vote.create(member_id="m2", vote_type=VoteType.APPROVE)
        assert v1.id != v2.id


class TestCommittee:
    """Tests for Committee dataclass."""

    def test_create_committee(self):
        """Create committee with default quorum."""
        committee = Committee.create(decision_id="dec_123")
        assert committee.id.startswith("com_")
        assert committee.decision_id == "dec_123"
        assert committee.quorum_required == 1
        assert committee.members == []
        assert committee.votes == []

    def test_create_committee_with_quorum(self):
        """Create committee with custom quorum."""
        committee = Committee.create(decision_id="dec_456", quorum_required=3)
        assert committee.quorum_required == 3

    def test_add_member(self):
        """Add member to committee."""
        committee = Committee.create(decision_id="dec_123")
        member = CommitteeMember.create(role=GuardianRole.VALIDATOR)
        committee.add_member(member)
        assert len(committee.members) == 1
        assert committee.members[0] == member

    def test_add_vote(self):
        """Add vote to committee."""
        committee = Committee.create(decision_id="dec_123")
        vote = Vote.create(member_id="mem_1", vote_type=VoteType.APPROVE)
        committee.add_vote(vote)
        assert len(committee.votes) == 1
        assert committee.votes[0] == vote

    def test_get_proponent(self):
        """Get proponent member."""
        committee = Committee.create(decision_id="dec_123")
        proponent = CommitteeMember.create(role=GuardianRole.PROPONENT)
        validator = CommitteeMember.create(role=GuardianRole.VALIDATOR)
        committee.add_member(proponent)
        committee.add_member(validator)
        assert committee.get_proponent() == proponent

    def test_get_proponent_none(self):
        """Get proponent when none exists."""
        committee = Committee.create(decision_id="dec_123")
        assert committee.get_proponent() is None

    def test_get_validators(self):
        """Get all validators."""
        committee = Committee.create(decision_id="dec_123")
        v1 = CommitteeMember.create(role=GuardianRole.VALIDATOR)
        v2 = CommitteeMember.create(role=GuardianRole.VALIDATOR)
        reviewer = CommitteeMember.create(role=GuardianRole.REVIEWER)
        committee.add_member(v1)
        committee.add_member(v2)
        committee.add_member(reviewer)
        validators = committee.get_validators()
        assert len(validators) == 2
        assert v1 in validators
        assert v2 in validators
        assert reviewer not in validators

    def test_get_reviewer(self):
        """Get reviewer member."""
        committee = Committee.create(decision_id="dec_123")
        reviewer = CommitteeMember.create(role=GuardianRole.REVIEWER)
        committee.add_member(reviewer)
        assert committee.get_reviewer() == reviewer

    def test_get_reviewer_none(self):
        """Get reviewer when none exists."""
        committee = Committee.create(decision_id="dec_123")
        assert committee.get_reviewer() is None

    def test_count_votes(self):
        """Count votes by type."""
        committee = Committee.create(decision_id="dec_123")
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        committee.add_vote(Vote.create("m2", VoteType.APPROVE))
        committee.add_vote(Vote.create("m3", VoteType.REJECT))
        counts = committee.count_votes()
        assert counts[VoteType.APPROVE] == 2
        assert counts[VoteType.REJECT] == 1
        assert counts[VoteType.ABSTAIN] == 0

    def test_count_votes_empty(self):
        """Count votes when no votes."""
        committee = Committee.create(decision_id="dec_123")
        counts = committee.count_votes()
        assert counts[VoteType.APPROVE] == 0
        assert counts[VoteType.REJECT] == 0
        assert counts[VoteType.ABSTAIN] == 0

    def test_has_quorum_true(self):
        """Check quorum reached."""
        committee = Committee.create(decision_id="dec_123", quorum_required=2)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        assert not committee.has_quorum()
        committee.add_vote(Vote.create("m2", VoteType.REJECT))
        assert committee.has_quorum()

    def test_has_quorum_false(self):
        """Check quorum not reached."""
        committee = Committee.create(decision_id="dec_123", quorum_required=3)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        assert not committee.has_quorum()

    def test_get_decision_approve(self):
        """Get decision when approve wins."""
        committee = Committee.create(decision_id="dec_123", quorum_required=3)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        committee.add_vote(Vote.create("m2", VoteType.APPROVE))
        committee.add_vote(Vote.create("m3", VoteType.REJECT))
        assert committee.get_decision() == VoteType.APPROVE

    def test_get_decision_reject(self):
        """Get decision when reject wins."""
        committee = Committee.create(decision_id="dec_123", quorum_required=3)
        committee.add_vote(Vote.create("m1", VoteType.REJECT))
        committee.add_vote(Vote.create("m2", VoteType.REJECT))
        committee.add_vote(Vote.create("m3", VoteType.APPROVE))
        assert committee.get_decision() == VoteType.REJECT

    def test_get_decision_tie(self):
        """Get decision when tied."""
        committee = Committee.create(decision_id="dec_123", quorum_required=2)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        committee.add_vote(Vote.create("m2", VoteType.REJECT))
        assert committee.get_decision() is None

    def test_get_decision_no_quorum(self):
        """Get decision when no quorum."""
        committee = Committee.create(decision_id="dec_123", quorum_required=3)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        assert committee.get_decision() is None


class TestDecision:
    """Tests for Decision dataclass."""

    def test_create_decision(self):
        """Create decision with defaults."""
        decision = Decision.create(
            claim_id="claim_123",
            domain="politics",
            gate="G7",
            proposed_state="verified",
        )
        assert decision.id.startswith("dec_")
        assert decision.claim_id == "claim_123"
        assert decision.domain == "politics"
        assert decision.gate == "G7"
        assert decision.proposed_state == "verified"
        assert decision.status == DecisionStatus.PENDING
        assert decision.context == {}
        assert decision.timeout_at is not None

    def test_create_decision_with_context(self):
        """Create decision with context."""
        ctx = {"evidence_refs": ["ev_1", "ev_2"], "confidence": 0.9}
        decision = Decision.create(
            claim_id="claim_123",
            domain="health",
            gate="G1",
            proposed_state="disputed",
            context=ctx,
            policy_name="health_policy_v1",
        )
        assert decision.context == ctx
        assert decision.policy_name == "health_policy_v1"

    def test_create_decision_custom_timeout(self):
        """Create decision with custom timeout."""
        decision = Decision.create(
            claim_id="claim_123",
            domain="politics",
            gate="G7",
            proposed_state="verified",
            timeout_seconds=60,
        )
        # Timeout should be ~60 seconds from now
        now = datetime.now(timezone.utc)
        diff = (decision.timeout_at - now).total_seconds()
        assert 59 <= diff <= 61

    def test_is_terminal_pending(self):
        """Pending is not terminal."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        assert not decision.is_terminal()

    def test_is_terminal_approved(self):
        """Approved is terminal."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.status = DecisionStatus.APPROVED
        assert decision.is_terminal()

    def test_is_terminal_rejected(self):
        """Rejected is terminal."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.status = DecisionStatus.REJECTED
        assert decision.is_terminal()

    def test_is_terminal_escalated(self):
        """Escalated is terminal."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.status = DecisionStatus.ESCALATED
        assert decision.is_terminal()

    def test_is_terminal_timed_out(self):
        """Timed out is terminal."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.status = DecisionStatus.TIMED_OUT
        assert decision.is_terminal()

    def test_is_terminal_cancelled(self):
        """Cancelled is terminal."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.status = DecisionStatus.CANCELLED
        assert decision.is_terminal()

    def test_is_terminal_non_terminal_states(self):
        """Non-terminal states."""
        non_terminal = [
            DecisionStatus.VALIDATING,
            DecisionStatus.AWAITING_REVIEW,
            DecisionStatus.AWAITING_QUORUM,
        ]
        for status in non_terminal:
            decision = Decision.create("c1", "d1", "G1", "verified")
            decision.status = status
            assert not decision.is_terminal()

    def test_is_timed_out_false(self):
        """Not timed out when timeout in future."""
        decision = Decision.create("c1", "d1", "G1", "verified", timeout_seconds=60)
        assert not decision.is_timed_out()

    def test_is_timed_out_true(self):
        """Timed out when timeout in past."""
        decision = Decision.create("c1", "d1", "G1", "verified", timeout_seconds=0)
        # Force timeout to past
        decision.timeout_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        assert decision.is_timed_out()

    def test_is_timed_out_no_timeout(self):
        """Not timed out when no timeout set."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.timeout_at = None
        assert not decision.is_timed_out()

    def test_complete_approved(self):
        """Complete decision as approved."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.complete(
            status=DecisionStatus.APPROVED,
            final_state="verified",
            reason="approved_by_policy",
        )
        assert decision.status == DecisionStatus.APPROVED
        assert decision.final_state == "verified"
        assert decision.final_reason == "approved_by_policy"
        assert decision.completed_at is not None

    def test_complete_rejected(self):
        """Complete decision as rejected."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        decision.complete(
            status=DecisionStatus.REJECTED,
            final_state="rejected",
            reason="insufficient_evidence",
        )
        assert decision.status == DecisionStatus.REJECTED
        assert decision.final_state == "rejected"


class TestDecisionBlock:
    """Tests for DecisionBlock dataclass."""

    def test_create_block_without_committee(self):
        """Create block without committee."""
        decision = Decision.create("c1", "politics", "G7", "verified")
        decision.complete(DecisionStatus.APPROVED, "verified", "auto_approved")

        block = DecisionBlock.create(
            decision=decision,
            committee=None,
            policy_version="v1.0",
            invariants={"inv1": True, "inv2": True},
            evidence_refs=["ev_1", "ev_2"],
            latency_ms=150,
        )

        assert block.id.startswith("blk_")
        assert block.decision_id == decision.id
        assert block.claim_id == "c1"
        assert block.domain == "politics"
        assert block.gate == "G7"
        assert block.initial_state == "verified"
        assert block.final_state == "verified"
        assert block.policy_version == "v1.0"
        assert block.committee_summary is None
        assert block.invariants_checked == {"inv1": True, "inv2": True}
        assert block.evidence_refs == ["ev_1", "ev_2"]
        assert block.latency_ms == 150

    def test_create_block_with_committee(self):
        """Create block with committee."""
        decision = Decision.create("c1", "politics", "G7", "verified")
        decision.complete(DecisionStatus.APPROVED, "verified", "committee_approved")

        committee = Committee.create(decision_id=decision.id, quorum_required=3)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        committee.add_vote(Vote.create("m2", VoteType.APPROVE))
        committee.add_vote(Vote.create("m3", VoteType.REJECT))

        block = DecisionBlock.create(
            decision=decision,
            committee=committee,
            policy_version="v2.0",
            invariants={"inv1": True},
        )

        assert block.committee_summary is not None
        assert block.committee_summary["committee_id"] == committee.id
        assert block.committee_summary["member_count"] == 0  # No members added
        assert block.committee_summary["vote_counts"]["approve"] == 2
        assert block.committee_summary["vote_counts"]["reject"] == 1
        assert block.committee_summary["quorum_required"] == 3
        assert block.committee_summary["quorum_reached"] is True

    def test_to_dict(self):
        """Convert block to dictionary."""
        decision = Decision.create("c1", "politics", "G7", "verified")
        decision.complete(DecisionStatus.APPROVED, "verified", "auto")

        block = DecisionBlock.create(
            decision=decision,
            committee=None,
            policy_version="v1.0",
            invariants={"inv1": True},
            latency_ms=100,
        )

        d = block.to_dict()
        assert d["id"] == block.id
        assert d["decision_id"] == decision.id
        assert d["claim_id"] == "c1"
        assert d["domain"] == "politics"
        assert d["gate"] == "G7"
        assert d["initial_state"] == "verified"
        assert d["final_state"] == "verified"
        assert d["policy_version"] == "v1.0"
        assert d["invariants_checked"] == {"inv1": True}
        assert d["latency_ms"] == 100
        assert "created_at" in d

    def test_block_final_state_fallback(self):
        """Block uses proposed_state if final_state is None."""
        decision = Decision.create("c1", "politics", "G7", "verified")
        # Don't set final_state
        decision.status = DecisionStatus.APPROVED

        block = DecisionBlock.create(
            decision=decision,
            committee=None,
            policy_version=None,
            invariants={},
        )

        assert block.final_state == "verified"  # Falls back to proposed_state
