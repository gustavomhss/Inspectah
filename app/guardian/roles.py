"""
Guardian Roles — S37

Defines the roles in the Guardian validation system.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional


class GuardianRole(str, Enum):
    """Roles in the Guardian validation committee."""

    PROPONENT = "proponent"
    VALIDATOR = "validator"
    REVIEWER = "reviewer"
    ARBITER = "arbiter"


class RoleCapability(str, Enum):
    """Capabilities associated with each role."""

    SUBMIT_DECISION = "submit_decision"
    VOTE = "vote"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    OVERRIDE = "override"
    ARBITRATE = "arbitrate"


# Role capability mappings
ROLE_CAPABILITIES = {
    GuardianRole.PROPONENT: [
        RoleCapability.SUBMIT_DECISION,
    ],
    GuardianRole.VALIDATOR: [
        RoleCapability.VOTE,
        RoleCapability.APPROVE,
        RoleCapability.REJECT,
        RoleCapability.ESCALATE,
    ],
    GuardianRole.REVIEWER: [
        RoleCapability.APPROVE,
        RoleCapability.REJECT,
        RoleCapability.ESCALATE,
    ],
    GuardianRole.ARBITER: [
        RoleCapability.APPROVE,
        RoleCapability.REJECT,
        RoleCapability.OVERRIDE,
        RoleCapability.ARBITRATE,
    ],
}


def get_role_capabilities(role: GuardianRole) -> List[RoleCapability]:
    """Get capabilities for a role."""
    return ROLE_CAPABILITIES.get(role, [])


def can_role_perform(role: GuardianRole, capability: RoleCapability) -> bool:
    """Check if a role can perform a capability."""
    return capability in get_role_capabilities(role)


# Decision type to required roles mapping
DECISION_TYPE_ROLES = {
    "auto_approve": {
        "required": [GuardianRole.PROPONENT],
        "optional": [],
    },
    "human_review": {
        "required": [GuardianRole.PROPONENT, GuardianRole.REVIEWER],
        "optional": [],
    },
    "committee_quorum": {
        "required": [GuardianRole.PROPONENT],
        "optional": [GuardianRole.VALIDATOR],
        "min_validators": 3,
    },
    "escalate": {
        "required": [GuardianRole.PROPONENT, GuardianRole.ARBITER],
        "optional": [GuardianRole.REVIEWER],
    },
}


def get_required_roles(decision_type: str) -> List[GuardianRole]:
    """Get required roles for a decision type."""
    config = DECISION_TYPE_ROLES.get(decision_type, {})
    return config.get("required", [GuardianRole.PROPONENT])


def get_min_validators(decision_type: str) -> int:
    """Get minimum number of validators for a decision type."""
    config = DECISION_TYPE_ROLES.get(decision_type, {})
    return config.get("min_validators", 0)
