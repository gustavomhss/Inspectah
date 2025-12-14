"""
Tests for Guardian Roles — S37

Tests for GuardianRole, RoleCapability, and role helper functions.
"""

import pytest

from app.guardian.roles import (
    GuardianRole,
    RoleCapability,
    ROLE_CAPABILITIES,
    DECISION_TYPE_ROLES,
    get_role_capabilities,
    can_role_perform,
    get_required_roles,
    get_min_validators,
)


class TestGuardianRole:
    """Tests for GuardianRole enum."""

    def test_all_roles_defined(self):
        """All expected roles are defined."""
        expected = ["proponent", "validator", "reviewer", "arbiter"]
        actual = [r.value for r in GuardianRole]
        assert set(actual) == set(expected)

    def test_role_values(self):
        """Role values match expected strings."""
        assert GuardianRole.PROPONENT.value == "proponent"
        assert GuardianRole.VALIDATOR.value == "validator"
        assert GuardianRole.REVIEWER.value == "reviewer"
        assert GuardianRole.ARBITER.value == "arbiter"

    def test_role_is_string_enum(self):
        """GuardianRole is a string enum."""
        assert isinstance(GuardianRole.PROPONENT, str)
        assert GuardianRole.PROPONENT == "proponent"


class TestRoleCapability:
    """Tests for RoleCapability enum."""

    def test_all_capabilities_defined(self):
        """All expected capabilities are defined."""
        expected = [
            "submit_decision", "vote", "approve", "reject",
            "escalate", "override", "arbitrate"
        ]
        actual = [c.value for c in RoleCapability]
        assert set(actual) == set(expected)

    def test_capability_values(self):
        """Capability values match expected strings."""
        assert RoleCapability.SUBMIT_DECISION.value == "submit_decision"
        assert RoleCapability.VOTE.value == "vote"
        assert RoleCapability.APPROVE.value == "approve"
        assert RoleCapability.REJECT.value == "reject"
        assert RoleCapability.ESCALATE.value == "escalate"
        assert RoleCapability.OVERRIDE.value == "override"
        assert RoleCapability.ARBITRATE.value == "arbitrate"


class TestRoleCapabilitiesMapping:
    """Tests for ROLE_CAPABILITIES mapping."""

    def test_proponent_capabilities(self):
        """Proponent has only submit_decision."""
        caps = ROLE_CAPABILITIES[GuardianRole.PROPONENT]
        assert caps == [RoleCapability.SUBMIT_DECISION]

    def test_validator_capabilities(self):
        """Validator can vote, approve, reject, escalate."""
        caps = ROLE_CAPABILITIES[GuardianRole.VALIDATOR]
        assert RoleCapability.VOTE in caps
        assert RoleCapability.APPROVE in caps
        assert RoleCapability.REJECT in caps
        assert RoleCapability.ESCALATE in caps
        assert RoleCapability.OVERRIDE not in caps

    def test_reviewer_capabilities(self):
        """Reviewer can approve, reject, escalate."""
        caps = ROLE_CAPABILITIES[GuardianRole.REVIEWER]
        assert RoleCapability.APPROVE in caps
        assert RoleCapability.REJECT in caps
        assert RoleCapability.ESCALATE in caps
        assert RoleCapability.VOTE not in caps

    def test_arbiter_capabilities(self):
        """Arbiter can approve, reject, override, arbitrate."""
        caps = ROLE_CAPABILITIES[GuardianRole.ARBITER]
        assert RoleCapability.APPROVE in caps
        assert RoleCapability.REJECT in caps
        assert RoleCapability.OVERRIDE in caps
        assert RoleCapability.ARBITRATE in caps
        assert RoleCapability.ESCALATE not in caps

    def test_all_roles_have_capabilities(self):
        """All roles have capabilities defined."""
        for role in GuardianRole:
            assert role in ROLE_CAPABILITIES
            assert len(ROLE_CAPABILITIES[role]) > 0


class TestGetRoleCapabilities:
    """Tests for get_role_capabilities function."""

    def test_get_proponent_capabilities(self):
        """Get proponent capabilities."""
        caps = get_role_capabilities(GuardianRole.PROPONENT)
        assert caps == [RoleCapability.SUBMIT_DECISION]

    def test_get_validator_capabilities(self):
        """Get validator capabilities."""
        caps = get_role_capabilities(GuardianRole.VALIDATOR)
        assert len(caps) == 4
        assert RoleCapability.VOTE in caps

    def test_get_reviewer_capabilities(self):
        """Get reviewer capabilities."""
        caps = get_role_capabilities(GuardianRole.REVIEWER)
        assert len(caps) == 3
        assert RoleCapability.APPROVE in caps

    def test_get_arbiter_capabilities(self):
        """Get arbiter capabilities."""
        caps = get_role_capabilities(GuardianRole.ARBITER)
        assert len(caps) == 4
        assert RoleCapability.ARBITRATE in caps


class TestCanRolePerform:
    """Tests for can_role_perform function."""

    def test_proponent_can_submit(self):
        """Proponent can submit decision."""
        assert can_role_perform(GuardianRole.PROPONENT, RoleCapability.SUBMIT_DECISION)

    def test_proponent_cannot_vote(self):
        """Proponent cannot vote."""
        assert not can_role_perform(GuardianRole.PROPONENT, RoleCapability.VOTE)

    def test_validator_can_vote(self):
        """Validator can vote."""
        assert can_role_perform(GuardianRole.VALIDATOR, RoleCapability.VOTE)

    def test_validator_can_approve(self):
        """Validator can approve."""
        assert can_role_perform(GuardianRole.VALIDATOR, RoleCapability.APPROVE)

    def test_validator_can_reject(self):
        """Validator can reject."""
        assert can_role_perform(GuardianRole.VALIDATOR, RoleCapability.REJECT)

    def test_validator_can_escalate(self):
        """Validator can escalate."""
        assert can_role_perform(GuardianRole.VALIDATOR, RoleCapability.ESCALATE)

    def test_validator_cannot_override(self):
        """Validator cannot override."""
        assert not can_role_perform(GuardianRole.VALIDATOR, RoleCapability.OVERRIDE)

    def test_reviewer_can_approve(self):
        """Reviewer can approve."""
        assert can_role_perform(GuardianRole.REVIEWER, RoleCapability.APPROVE)

    def test_reviewer_cannot_vote(self):
        """Reviewer cannot vote."""
        assert not can_role_perform(GuardianRole.REVIEWER, RoleCapability.VOTE)

    def test_arbiter_can_arbitrate(self):
        """Arbiter can arbitrate."""
        assert can_role_perform(GuardianRole.ARBITER, RoleCapability.ARBITRATE)

    def test_arbiter_can_override(self):
        """Arbiter can override."""
        assert can_role_perform(GuardianRole.ARBITER, RoleCapability.OVERRIDE)

    def test_arbiter_cannot_submit(self):
        """Arbiter cannot submit."""
        assert not can_role_perform(GuardianRole.ARBITER, RoleCapability.SUBMIT_DECISION)


class TestDecisionTypeRoles:
    """Tests for DECISION_TYPE_ROLES mapping."""

    def test_auto_approve_roles(self):
        """Auto approve requires only proponent."""
        config = DECISION_TYPE_ROLES["auto_approve"]
        assert config["required"] == [GuardianRole.PROPONENT]
        assert config["optional"] == []

    def test_human_review_roles(self):
        """Human review requires proponent and reviewer."""
        config = DECISION_TYPE_ROLES["human_review"]
        assert GuardianRole.PROPONENT in config["required"]
        assert GuardianRole.REVIEWER in config["required"]

    def test_committee_quorum_roles(self):
        """Committee quorum has min_validators."""
        config = DECISION_TYPE_ROLES["committee_quorum"]
        assert GuardianRole.PROPONENT in config["required"]
        assert GuardianRole.VALIDATOR in config["optional"]
        assert config["min_validators"] == 3

    def test_escalate_roles(self):
        """Escalate requires proponent and arbiter."""
        config = DECISION_TYPE_ROLES["escalate"]
        assert GuardianRole.PROPONENT in config["required"]
        assert GuardianRole.ARBITER in config["required"]


class TestGetRequiredRoles:
    """Tests for get_required_roles function."""

    def test_get_auto_approve_roles(self):
        """Get required roles for auto_approve."""
        roles = get_required_roles("auto_approve")
        assert roles == [GuardianRole.PROPONENT]

    def test_get_human_review_roles(self):
        """Get required roles for human_review."""
        roles = get_required_roles("human_review")
        assert GuardianRole.PROPONENT in roles
        assert GuardianRole.REVIEWER in roles

    def test_get_committee_quorum_roles(self):
        """Get required roles for committee_quorum."""
        roles = get_required_roles("committee_quorum")
        assert GuardianRole.PROPONENT in roles

    def test_get_escalate_roles(self):
        """Get required roles for escalate."""
        roles = get_required_roles("escalate")
        assert GuardianRole.PROPONENT in roles
        assert GuardianRole.ARBITER in roles

    def test_get_unknown_decision_type_roles(self):
        """Get required roles for unknown type defaults to proponent."""
        roles = get_required_roles("unknown_type")
        assert roles == [GuardianRole.PROPONENT]


class TestGetMinValidators:
    """Tests for get_min_validators function."""

    def test_get_auto_approve_min_validators(self):
        """Auto approve has 0 min validators."""
        assert get_min_validators("auto_approve") == 0

    def test_get_human_review_min_validators(self):
        """Human review has 0 min validators."""
        assert get_min_validators("human_review") == 0

    def test_get_committee_quorum_min_validators(self):
        """Committee quorum has 3 min validators."""
        assert get_min_validators("committee_quorum") == 3

    def test_get_escalate_min_validators(self):
        """Escalate has 0 min validators."""
        assert get_min_validators("escalate") == 0

    def test_get_unknown_decision_type_min_validators(self):
        """Unknown type has 0 min validators."""
        assert get_min_validators("unknown_type") == 0
