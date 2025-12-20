"""
Tests for Guardian RBAC (Role-Based Access Control) — S41

Tests for fail-closed access control with role hierarchy,
domain-scoped permissions, and complete audit logging.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Set

import pytest

from app.guardian.rbac import (
    AccessAttempt,
    Permission,
    Role,
    ROLE_HIERARCHY,
    ROLE_PERMISSIONS,
    RBACManager,
    UserRoleAssignment,
    _generate_id,
    _utcnow,
    get_rbac_manager,
    reset_rbac_manager,
)


# ==============================================================================
# Helper Functions Tests
# ==============================================================================


class TestUtcnow:
    """Tests for _utcnow helper function."""

    def test_returns_datetime(self) -> None:
        """_utcnow should return a datetime object."""
        result = _utcnow()
        assert isinstance(result, datetime)

    def test_returns_timezone_aware(self) -> None:
        """_utcnow should return a timezone-aware datetime."""
        result = _utcnow()
        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc

    def test_returns_current_time(self) -> None:
        """_utcnow should return approximately current time."""
        before = datetime.now(timezone.utc)
        result = _utcnow()
        after = datetime.now(timezone.utc)
        assert before <= result <= after


class TestGenerateId:
    """Tests for _generate_id helper function."""

    def test_returns_string(self) -> None:
        """_generate_id should return a string."""
        result = _generate_id()
        assert isinstance(result, str)

    def test_uses_default_prefix(self) -> None:
        """_generate_id should use 'rbac' as default prefix."""
        result = _generate_id()
        assert result.startswith("rbac_")

    def test_uses_custom_prefix(self) -> None:
        """_generate_id should use custom prefix when provided."""
        result = _generate_id("custom")
        assert result.startswith("custom_")

    def test_generates_unique_ids(self) -> None:
        """_generate_id should generate unique IDs."""
        ids = {_generate_id() for _ in range(100)}
        assert len(ids) == 100


# ==============================================================================
# Enum Tests
# ==============================================================================


class TestPermission:
    """Tests for Permission enum."""

    def test_all_permissions_defined(self) -> None:
        """All expected permissions should be defined."""
        expected = [
            "SUBMIT_DECISION",
            "VIEW_DECISION",
            "APPROVE_DECISION",
            "REJECT_DECISION",
            "ESCALATE_DECISION",
            "CREATE_DISPUTE",
            "VIEW_DISPUTE",
            "PROCESS_DISPUTE",
            "RESOLVE_DISPUTE",
            "JOIN_COMMITTEE",
            "VOTE_IN_COMMITTEE",
            "MANAGE_COMMITTEE",
            "CREATE_CASE",
            "VIEW_CASE",
            "UPDATE_CASE",
            "TRANSITION_CASE",
            "ARCHIVE_CASE",
            "VIEW_AUDIT_TRAIL",
            "EXPORT_AUDIT_TRAIL",
            "MANAGE_ROLES",
            "MANAGE_USERS",
            "CONFIGURE_THRESHOLDS",
            "OVERRIDE_DECISION",
        ]
        for perm_name in expected:
            assert hasattr(Permission, perm_name)

    def test_permission_is_string_enum(self) -> None:
        """Permission should be a string enum."""
        assert isinstance(Permission.VIEW_DECISION, str)
        assert Permission.VIEW_DECISION == "view_decision"

    def test_decision_permissions(self) -> None:
        """Decision permissions should have correct values."""
        assert Permission.SUBMIT_DECISION.value == "submit_decision"
        assert Permission.VIEW_DECISION.value == "view_decision"
        assert Permission.APPROVE_DECISION.value == "approve_decision"
        assert Permission.REJECT_DECISION.value == "reject_decision"
        assert Permission.ESCALATE_DECISION.value == "escalate_decision"

    def test_contestation_permissions(self) -> None:
        """Contestation permissions should have correct values."""
        assert Permission.CREATE_DISPUTE.value == "create_dispute"
        assert Permission.VIEW_DISPUTE.value == "view_dispute"
        assert Permission.PROCESS_DISPUTE.value == "process_dispute"
        assert Permission.RESOLVE_DISPUTE.value == "resolve_dispute"

    def test_committee_permissions(self) -> None:
        """Committee permissions should have correct values."""
        assert Permission.JOIN_COMMITTEE.value == "join_committee"
        assert Permission.VOTE_IN_COMMITTEE.value == "vote_in_committee"
        assert Permission.MANAGE_COMMITTEE.value == "manage_committee"


class TestRole:
    """Tests for Role enum."""

    def test_all_roles_defined(self) -> None:
        """All expected roles should be defined."""
        expected = [
            "VIEWER",
            "ANALYST",
            "VALIDATOR",
            "REVIEWER",
            "COMMITTEE_MEMBER",
            "COMMITTEE_LEAD",
            "ARBITER",
            "DOMAIN_ADMIN",
            "SYSTEM_ADMIN",
        ]
        for role_name in expected:
            assert hasattr(Role, role_name)

    def test_role_is_string_enum(self) -> None:
        """Role should be a string enum."""
        assert isinstance(Role.VIEWER, str)
        assert Role.VIEWER == "viewer"

    def test_role_values(self) -> None:
        """Roles should have correct values."""
        assert Role.VIEWER.value == "viewer"
        assert Role.ANALYST.value == "analyst"
        assert Role.VALIDATOR.value == "validator"
        assert Role.REVIEWER.value == "reviewer"
        assert Role.SYSTEM_ADMIN.value == "system_admin"


# ==============================================================================
# Constants Tests
# ==============================================================================


class TestRoleHierarchy:
    """Tests for ROLE_HIERARCHY constant."""

    def test_all_roles_in_hierarchy(self) -> None:
        """All roles should be in the hierarchy."""
        for role in Role:
            assert role in ROLE_HIERARCHY

    def test_viewer_has_no_parents(self) -> None:
        """Viewer should have no parent roles."""
        assert ROLE_HIERARCHY[Role.VIEWER] == []

    def test_analyst_inherits_viewer(self) -> None:
        """Analyst should inherit from Viewer."""
        assert Role.VIEWER in ROLE_HIERARCHY[Role.ANALYST]

    def test_system_admin_is_top(self) -> None:
        """System admin should inherit from domain admin."""
        assert Role.DOMAIN_ADMIN in ROLE_HIERARCHY[Role.SYSTEM_ADMIN]

    def test_hierarchy_is_valid(self) -> None:
        """Hierarchy should form a valid DAG."""
        # No cycles, all references valid
        for role, parents in ROLE_HIERARCHY.items():
            for parent in parents:
                assert parent in Role


class TestRolePermissions:
    """Tests for ROLE_PERMISSIONS constant."""

    def test_all_roles_have_permissions(self) -> None:
        """All roles should have permissions defined."""
        for role in Role:
            assert role in ROLE_PERMISSIONS

    def test_viewer_permissions(self) -> None:
        """Viewer should have correct base permissions."""
        perms = ROLE_PERMISSIONS[Role.VIEWER]
        assert Permission.VIEW_DECISION in perms
        assert Permission.VIEW_CASE in perms
        assert Permission.VIEW_DISPUTE in perms

    def test_analyst_permissions(self) -> None:
        """Analyst should have correct base permissions."""
        perms = ROLE_PERMISSIONS[Role.ANALYST]
        assert Permission.SUBMIT_DECISION in perms
        assert Permission.CREATE_CASE in perms
        assert Permission.CREATE_DISPUTE in perms

    def test_system_admin_permissions(self) -> None:
        """System admin should have admin permissions."""
        perms = ROLE_PERMISSIONS[Role.SYSTEM_ADMIN]
        assert Permission.MANAGE_ROLES in perms
        assert Permission.MANAGE_USERS in perms
        assert Permission.OVERRIDE_DECISION in perms


# ==============================================================================
# AccessAttempt Tests
# ==============================================================================


class TestAccessAttempt:
    """Tests for AccessAttempt dataclass."""

    def test_create_access_attempt(self) -> None:
        """Should create AccessAttempt with required fields."""
        attempt = AccessAttempt(
            id="acc_123",
            user_id="user_1",
            permission="view_decision",
            resource_type="decision",
            resource_id="dec_456",
            domain="politics",
            granted=True,
            reason="Permission granted",
        )
        assert attempt.id == "acc_123"
        assert attempt.user_id == "user_1"
        assert attempt.permission == "view_decision"
        assert attempt.granted is True

    def test_access_attempt_defaults(self) -> None:
        """Should have correct default values."""
        attempt = AccessAttempt(
            id="acc_123",
            user_id="user_1",
            permission="view_decision",
            resource_type="decision",
            resource_id=None,
            domain=None,
            granted=False,
            reason="Denied",
        )
        assert attempt.metadata == {}
        assert isinstance(attempt.timestamp, datetime)

    def test_to_dict(self) -> None:
        """to_dict should return correct dictionary."""
        attempt = AccessAttempt(
            id="acc_123",
            user_id="user_1",
            permission="view_decision",
            resource_type="decision",
            resource_id="dec_456",
            domain="politics",
            granted=True,
            reason="Permission granted",
            metadata={"extra": "data"},
        )
        result = attempt.to_dict()
        assert result["id"] == "acc_123"
        assert result["user_id"] == "user_1"
        assert result["permission"] == "view_decision"
        assert result["resource_type"] == "decision"
        assert result["resource_id"] == "dec_456"
        assert result["domain"] == "politics"
        assert result["granted"] is True
        assert result["reason"] == "Permission granted"
        assert result["metadata"] == {"extra": "data"}
        assert "timestamp" in result

    def test_to_dict_timestamp_is_iso_format(self) -> None:
        """to_dict should return timestamp in ISO format."""
        attempt = AccessAttempt(
            id="acc_123",
            user_id="user_1",
            permission="view_decision",
            resource_type="decision",
            resource_id=None,
            domain=None,
            granted=True,
            reason="OK",
        )
        result = attempt.to_dict()
        # Should be parseable as ISO format
        datetime.fromisoformat(result["timestamp"])


# ==============================================================================
# UserRoleAssignment Tests
# ==============================================================================


class TestUserRoleAssignment:
    """Tests for UserRoleAssignment dataclass."""

    def test_create_assignment(self) -> None:
        """Should create assignment with required fields."""
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
        )
        assert assignment.user_id == "user_1"
        assert assignment.role == Role.ANALYST
        assert assignment.domain is None

    def test_assignment_with_domain(self) -> None:
        """Should create assignment with domain scope."""
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
            domain="politics",
        )
        assert assignment.domain == "politics"

    def test_assignment_with_expiration(self) -> None:
        """Should create assignment with expiration."""
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
            expires_at=expires,
        )
        assert assignment.expires_at == expires

    def test_is_expired_false_when_no_expiration(self) -> None:
        """is_expired should return False when no expiration set."""
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
        )
        assert assignment.is_expired() is False

    def test_is_expired_false_when_future_expiration(self) -> None:
        """is_expired should return False when expiration is in future."""
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
            expires_at=expires,
        )
        assert assignment.is_expired() is False

    def test_is_expired_true_when_past_expiration(self) -> None:
        """is_expired should return True when expiration is in past."""
        expires = datetime.now(timezone.utc) - timedelta(days=1)
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
            expires_at=expires,
        )
        assert assignment.is_expired() is True

    def test_is_valid_true_when_not_expired(self) -> None:
        """is_valid should return True when not expired."""
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
        )
        assert assignment.is_valid() is True

    def test_is_valid_false_when_expired(self) -> None:
        """is_valid should return False when expired."""
        expires = datetime.now(timezone.utc) - timedelta(days=1)
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
            expires_at=expires,
        )
        assert assignment.is_valid() is False

    def test_granted_by_field(self) -> None:
        """Should store granted_by field."""
        assignment = UserRoleAssignment(
            user_id="user_1",
            role=Role.ANALYST,
            granted_by="admin_1",
        )
        assert assignment.granted_by == "admin_1"


# ==============================================================================
# RBACManager Tests
# ==============================================================================


class TestRBACManagerInit:
    """Tests for RBACManager initialization."""

    def test_init_creates_empty_state(self) -> None:
        """Init should create manager with empty state."""
        manager = RBACManager()
        assert manager._role_assignments == {}
        assert manager._access_log == []
        assert manager._failed_attempts == {}

    def test_init_sets_max_failed_attempts(self) -> None:
        """Init should set default max failed attempts."""
        manager = RBACManager()
        assert manager._max_failed_attempts == 5


class TestRBACManagerAssignRole:
    """Tests for RBACManager.assign_role method."""

    def test_assign_role_creates_assignment(self) -> None:
        """assign_role should create and return assignment."""
        manager = RBACManager()
        assignment = manager.assign_role("user_1", Role.ANALYST)
        assert assignment.user_id == "user_1"
        assert assignment.role == Role.ANALYST

    def test_assign_role_with_domain(self) -> None:
        """assign_role should support domain scope."""
        manager = RBACManager()
        assignment = manager.assign_role("user_1", Role.ANALYST, domain="politics")
        assert assignment.domain == "politics"

    def test_assign_role_with_granted_by(self) -> None:
        """assign_role should support granted_by."""
        manager = RBACManager()
        assignment = manager.assign_role("user_1", Role.ANALYST, granted_by="admin_1")
        assert assignment.granted_by == "admin_1"

    def test_assign_role_with_expiration(self) -> None:
        """assign_role should support expiration."""
        manager = RBACManager()
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        assignment = manager.assign_role("user_1", Role.ANALYST, expires_at=expires)
        assert assignment.expires_at == expires

    def test_assign_multiple_roles_to_user(self) -> None:
        """Should be able to assign multiple roles to same user."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST)
        manager.assign_role("user_1", Role.REVIEWER)
        roles = manager.get_user_roles("user_1")
        assert Role.ANALYST in roles
        assert Role.REVIEWER in roles


class TestRBACManagerRevokeRole:
    """Tests for RBACManager.revoke_role method."""

    def test_revoke_existing_role(self) -> None:
        """revoke_role should remove existing role."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST)
        result = manager.revoke_role("user_1", Role.ANALYST)
        assert result is True
        roles = manager.get_user_roles("user_1")
        assert Role.ANALYST not in roles

    def test_revoke_nonexistent_role(self) -> None:
        """revoke_role should return False for nonexistent role."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST)
        result = manager.revoke_role("user_1", Role.REVIEWER)
        assert result is False

    def test_revoke_from_nonexistent_user(self) -> None:
        """revoke_role should return False for nonexistent user."""
        manager = RBACManager()
        result = manager.revoke_role("user_1", Role.ANALYST)
        assert result is False

    def test_revoke_domain_specific_role(self) -> None:
        """revoke_role should only revoke matching domain."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST, domain="politics")
        manager.assign_role("user_1", Role.ANALYST, domain="health")

        result = manager.revoke_role("user_1", Role.ANALYST, domain="politics")
        assert result is True

        # Health domain should still have role
        roles = manager.get_user_roles("user_1", domain="health")
        assert Role.ANALYST in roles


class TestRBACManagerGetUserRoles:
    """Tests for RBACManager.get_user_roles method."""

    def test_get_roles_for_user_with_roles(self) -> None:
        """Should return all valid roles for user."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST)
        manager.assign_role("user_1", Role.REVIEWER)
        roles = manager.get_user_roles("user_1")
        assert len(roles) == 2
        assert Role.ANALYST in roles
        assert Role.REVIEWER in roles

    def test_get_roles_for_user_without_roles(self) -> None:
        """Should return empty list for user without roles."""
        manager = RBACManager()
        roles = manager.get_user_roles("user_1")
        assert roles == []

    def test_get_roles_filters_by_domain(self) -> None:
        """Should filter roles by domain."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST, domain="politics")
        manager.assign_role("user_1", Role.REVIEWER, domain="health")

        roles = manager.get_user_roles("user_1", domain="politics")
        assert Role.ANALYST in roles
        assert Role.REVIEWER not in roles

    def test_get_roles_includes_global_roles(self) -> None:
        """Should include global roles (domain=None) for any domain."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST)  # Global
        manager.assign_role("user_1", Role.REVIEWER, domain="politics")

        roles = manager.get_user_roles("user_1", domain="politics")
        assert Role.ANALYST in roles  # Global role included
        assert Role.REVIEWER in roles  # Domain-specific role included

    def test_get_roles_excludes_expired(self) -> None:
        """Should exclude expired roles."""
        manager = RBACManager()
        expires = datetime.now(timezone.utc) - timedelta(days=1)
        manager.assign_role("user_1", Role.ANALYST, expires_at=expires)
        manager.assign_role("user_1", Role.REVIEWER)

        roles = manager.get_user_roles("user_1")
        assert Role.ANALYST not in roles
        assert Role.REVIEWER in roles


class TestRBACManagerGetUserPermissions:
    """Tests for RBACManager.get_user_permissions method."""

    def test_get_permissions_for_role(self) -> None:
        """Should return permissions for user's role."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        perms = manager.get_user_permissions("user_1")
        assert Permission.VIEW_DECISION in perms
        assert Permission.VIEW_CASE in perms

    def test_get_permissions_includes_inherited(self) -> None:
        """Should include inherited permissions from parent roles."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST)  # Inherits from VIEWER
        perms = manager.get_user_permissions("user_1")
        # ANALYST permissions
        assert Permission.SUBMIT_DECISION in perms
        # VIEWER permissions (inherited)
        assert Permission.VIEW_DECISION in perms

    def test_get_permissions_for_user_without_roles(self) -> None:
        """Should return empty set for user without roles."""
        manager = RBACManager()
        perms = manager.get_user_permissions("user_1")
        assert perms == set()

    def test_get_permissions_with_domain_filter(self) -> None:
        """Should filter permissions by domain."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST, domain="politics")

        # Should have permissions for politics domain
        perms = manager.get_user_permissions("user_1", domain="politics")
        assert Permission.SUBMIT_DECISION in perms

        # Should NOT have permissions for health domain
        perms = manager.get_user_permissions("user_1", domain="health")
        assert perms == set()


class TestRBACManagerHasPermission:
    """Tests for RBACManager.has_permission method."""

    def test_has_permission_granted(self) -> None:
        """Should return True when user has permission."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        result = manager.has_permission("user_1", Permission.VIEW_DECISION)
        assert result is True

    def test_has_permission_denied(self) -> None:
        """Should return False when user lacks permission."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        result = manager.has_permission("user_1", Permission.SUBMIT_DECISION)
        assert result is False

    def test_has_permission_no_roles(self) -> None:
        """Should return False when user has no roles."""
        manager = RBACManager()
        result = manager.has_permission("user_1", Permission.VIEW_DECISION)
        assert result is False

    def test_has_permission_logs_access(self) -> None:
        """Should log access attempt."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        manager.has_permission("user_1", Permission.VIEW_DECISION)
        log = manager.get_access_log("user_1")
        assert len(log) == 1
        assert log[0].granted is True

    def test_has_permission_with_domain(self) -> None:
        """Should check domain-scoped permissions."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST, domain="politics")

        # Should have permission in politics domain
        result = manager.has_permission(
            "user_1", Permission.SUBMIT_DECISION, domain="politics"
        )
        assert result is True

        # Should NOT have permission in health domain
        result = manager.has_permission(
            "user_1", Permission.SUBMIT_DECISION, domain="health"
        )
        assert result is False


class TestRBACManagerRateLimiting:
    """Tests for rate limiting in RBACManager."""

    def test_rate_limiting_after_max_failed_attempts(self) -> None:
        """Should rate limit after max failed attempts."""
        manager = RBACManager()
        manager._max_failed_attempts = 3

        # Make 3 failed attempts
        for _ in range(3):
            manager.has_permission("user_1", Permission.SUBMIT_DECISION)

        # Next attempt should be rate limited
        result = manager.has_permission("user_1", Permission.VIEW_DECISION)
        assert result is False

        # Check log shows rate limited
        log = manager.get_access_log("user_1")
        assert log[0].reason == "Rate limited due to excessive failed attempts"

    def test_successful_attempt_clears_failed_count(self) -> None:
        """Successful attempt should clear failed attempt counter."""
        manager = RBACManager()
        manager._max_failed_attempts = 5
        manager.assign_role("user_1", Role.VIEWER)

        # Make some failed attempts
        for _ in range(3):
            manager.has_permission("user_1", Permission.SUBMIT_DECISION)

        # Make successful attempt
        manager.has_permission("user_1", Permission.VIEW_DECISION)

        # Counter should be cleared, can make more failed attempts
        assert manager._failed_attempts.get("user_1") is None


class TestRBACManagerCheckPermission:
    """Tests for RBACManager.check_permission string interface."""

    def test_check_permission_simple(self) -> None:
        """Should check simple permission string."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        result = manager.check_permission("user_1", "view_decision")
        assert result is True

    def test_check_permission_with_domain_suffix(self) -> None:
        """Should parse domain from permission string."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.ANALYST, domain="politics")
        result = manager.check_permission("user_1", "submit_decision:politics")
        assert result is True

    def test_check_permission_unknown_permission(self) -> None:
        """Should return False for unknown permission (fail-closed)."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.SYSTEM_ADMIN)
        result = manager.check_permission("user_1", "unknown_permission")
        assert result is False

    def test_check_permission_logs_unknown(self) -> None:
        """Should log unknown permission attempt."""
        manager = RBACManager()
        manager.check_permission("user_1", "invalid_perm")
        log = manager.get_access_log("user_1")
        assert len(log) == 1
        assert "Unknown permission" in log[0].reason


class TestRBACManagerAccessLog:
    """Tests for RBACManager access logging."""

    def test_get_access_log_empty(self) -> None:
        """Should return empty list when no logs."""
        manager = RBACManager()
        log = manager.get_access_log()
        assert log == []

    def test_get_access_log_filters_by_user(self) -> None:
        """Should filter log by user_id."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        manager.assign_role("user_2", Role.VIEWER)
        manager.has_permission("user_1", Permission.VIEW_DECISION)
        manager.has_permission("user_2", Permission.VIEW_DECISION)

        log = manager.get_access_log("user_1")
        assert len(log) == 1
        assert log[0].user_id == "user_1"

    def test_get_access_log_respects_limit(self) -> None:
        """Should respect limit parameter."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        for _ in range(10):
            manager.has_permission("user_1", Permission.VIEW_DECISION)

        log = manager.get_access_log("user_1", limit=5)
        assert len(log) == 5

    def test_get_access_log_returns_most_recent_first(self) -> None:
        """Should return most recent entries first."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        manager.has_permission("user_1", Permission.VIEW_DECISION)
        manager.has_permission("user_1", Permission.VIEW_CASE)

        log = manager.get_access_log("user_1")
        # Most recent (VIEW_CASE) should be first
        assert log[0].permission == "view_case"

    def test_get_denied_attempts(self) -> None:
        """Should return only denied attempts."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        manager.has_permission("user_1", Permission.VIEW_DECISION)  # Granted
        manager.has_permission("user_1", Permission.SUBMIT_DECISION)  # Denied

        denied = manager.get_denied_attempts()
        assert len(denied) == 1
        assert denied[0].granted is False
        assert denied[0].permission == "submit_decision"

    def test_get_denied_attempts_respects_limit(self) -> None:
        """Should respect limit for denied attempts."""
        manager = RBACManager()
        for i in range(10):
            manager.has_permission(f"user_{i}", Permission.SUBMIT_DECISION)

        denied = manager.get_denied_attempts(limit=5)
        assert len(denied) == 5


class TestRBACManagerClear:
    """Tests for RBACManager.clear method."""

    def test_clear_removes_all_data(self) -> None:
        """clear should remove all data."""
        manager = RBACManager()
        manager.assign_role("user_1", Role.VIEWER)
        manager.has_permission("user_1", Permission.VIEW_DECISION)

        manager.clear()

        assert manager._role_assignments == {}
        assert manager._access_log == []
        assert manager._failed_attempts == {}


class TestRBACManagerGetAllPermissions:
    """Tests for RBACManager._get_all_permissions method."""

    def test_get_all_permissions_base_role(self) -> None:
        """Should return base permissions for role."""
        manager = RBACManager()
        perms = manager._get_all_permissions(Role.VIEWER)
        assert Permission.VIEW_DECISION in perms
        assert Permission.VIEW_CASE in perms

    def test_get_all_permissions_with_inheritance(self) -> None:
        """Should include inherited permissions."""
        manager = RBACManager()
        perms = manager._get_all_permissions(Role.ANALYST)
        # ANALYST's own permissions
        assert Permission.SUBMIT_DECISION in perms
        # Inherited from VIEWER
        assert Permission.VIEW_DECISION in perms

    def test_get_all_permissions_deep_inheritance(self) -> None:
        """Should handle deep inheritance chain."""
        manager = RBACManager()
        perms = manager._get_all_permissions(Role.SYSTEM_ADMIN)
        # SYSTEM_ADMIN permissions
        assert Permission.MANAGE_ROLES in perms
        # Should inherit all the way down to VIEWER
        assert Permission.VIEW_DECISION in perms


# ==============================================================================
# Singleton Tests
# ==============================================================================


class TestSingleton:
    """Tests for singleton pattern."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        reset_rbac_manager()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        reset_rbac_manager()

    def test_get_rbac_manager_creates_instance(self) -> None:
        """get_rbac_manager should create instance."""
        manager = get_rbac_manager()
        assert manager is not None
        assert isinstance(manager, RBACManager)

    def test_get_rbac_manager_returns_same_instance(self) -> None:
        """get_rbac_manager should return same instance."""
        manager1 = get_rbac_manager()
        manager2 = get_rbac_manager()
        assert manager1 is manager2

    def test_reset_rbac_manager_clears_instance(self) -> None:
        """reset_rbac_manager should clear singleton."""
        manager1 = get_rbac_manager()
        reset_rbac_manager()
        manager2 = get_rbac_manager()
        assert manager1 is not manager2
