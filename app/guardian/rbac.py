"""
Guardian RBAC — S41

Role-Based Access Control for the Guardian governance system.
Implements fail-closed access control with full audit logging.

Key Features:
- Fail-closed design: deny by default
- Role hierarchy with permission inheritance
- Domain-scoped permissions
- Complete audit trail for all access attempts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _generate_id(prefix: str = "rbac") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid4().hex[:12]}"


class Permission(str, Enum):
    """Permission types in the Guardian system."""

    # Decision permissions
    SUBMIT_DECISION = "submit_decision"
    VIEW_DECISION = "view_decision"
    APPROVE_DECISION = "approve_decision"
    REJECT_DECISION = "reject_decision"
    ESCALATE_DECISION = "escalate_decision"

    # Contestation permissions
    CREATE_DISPUTE = "create_dispute"
    VIEW_DISPUTE = "view_dispute"
    PROCESS_DISPUTE = "process_dispute"
    RESOLVE_DISPUTE = "resolve_dispute"

    # Committee permissions
    JOIN_COMMITTEE = "join_committee"
    VOTE_IN_COMMITTEE = "vote_in_committee"
    MANAGE_COMMITTEE = "manage_committee"

    # Case permissions
    CREATE_CASE = "create_case"
    VIEW_CASE = "view_case"
    UPDATE_CASE = "update_case"
    TRANSITION_CASE = "transition_case"
    ARCHIVE_CASE = "archive_case"

    # Audit permissions
    VIEW_AUDIT_TRAIL = "view_audit_trail"
    EXPORT_AUDIT_TRAIL = "export_audit_trail"

    # Admin permissions
    MANAGE_ROLES = "manage_roles"
    MANAGE_USERS = "manage_users"
    CONFIGURE_THRESHOLDS = "configure_thresholds"
    OVERRIDE_DECISION = "override_decision"


class Role(str, Enum):
    """Roles in the Guardian system."""

    # Basic roles
    VIEWER = "viewer"
    ANALYST = "analyst"
    VALIDATOR = "validator"
    REVIEWER = "reviewer"

    # Advanced roles
    COMMITTEE_MEMBER = "committee_member"
    COMMITTEE_LEAD = "committee_lead"
    ARBITER = "arbiter"

    # Admin roles
    DOMAIN_ADMIN = "domain_admin"
    SYSTEM_ADMIN = "system_admin"


# Role hierarchy: higher roles inherit permissions from lower roles
ROLE_HIERARCHY: Dict[Role, List[Role]] = {
    Role.VIEWER: [],
    Role.ANALYST: [Role.VIEWER],
    Role.VALIDATOR: [Role.ANALYST],
    Role.REVIEWER: [Role.VALIDATOR],
    Role.COMMITTEE_MEMBER: [Role.REVIEWER],
    Role.COMMITTEE_LEAD: [Role.COMMITTEE_MEMBER],
    Role.ARBITER: [Role.COMMITTEE_LEAD],
    Role.DOMAIN_ADMIN: [Role.ARBITER],
    Role.SYSTEM_ADMIN: [Role.DOMAIN_ADMIN],
}

# Base permissions for each role
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.VIEWER: {
        Permission.VIEW_DECISION,
        Permission.VIEW_CASE,
        Permission.VIEW_DISPUTE,
    },
    Role.ANALYST: {
        Permission.SUBMIT_DECISION,
        Permission.CREATE_CASE,
        Permission.CREATE_DISPUTE,
    },
    Role.VALIDATOR: {
        Permission.JOIN_COMMITTEE,
        Permission.VOTE_IN_COMMITTEE,
    },
    Role.REVIEWER: {
        Permission.UPDATE_CASE,
        Permission.VIEW_AUDIT_TRAIL,
    },
    Role.COMMITTEE_MEMBER: {
        Permission.APPROVE_DECISION,
        Permission.REJECT_DECISION,
    },
    Role.COMMITTEE_LEAD: {
        Permission.MANAGE_COMMITTEE,
        Permission.ESCALATE_DECISION,
        Permission.TRANSITION_CASE,
    },
    Role.ARBITER: {
        Permission.PROCESS_DISPUTE,
        Permission.RESOLVE_DISPUTE,
        Permission.ARCHIVE_CASE,
    },
    Role.DOMAIN_ADMIN: {
        Permission.CONFIGURE_THRESHOLDS,
        Permission.EXPORT_AUDIT_TRAIL,
    },
    Role.SYSTEM_ADMIN: {
        Permission.MANAGE_ROLES,
        Permission.MANAGE_USERS,
        Permission.OVERRIDE_DECISION,
    },
}


@dataclass
class AccessAttempt:
    """Record of an access attempt for audit logging."""

    id: str
    user_id: str
    permission: str
    resource_type: str
    resource_id: Optional[str]
    domain: Optional[str]
    granted: bool
    reason: str
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "permission": self.permission,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "domain": self.domain,
            "granted": self.granted,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class UserRoleAssignment:
    """Assignment of a role to a user, optionally scoped to a domain."""

    user_id: str
    role: Role
    domain: Optional[str] = None  # None means global
    granted_by: Optional[str] = None
    granted_at: datetime = field(default_factory=_utcnow)
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if the role assignment has expired."""
        if self.expires_at is None:
            return False
        return _utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the role assignment is currently valid."""
        return not self.is_expired()


class RBACManager:
    """
    Role-Based Access Control Manager.

    Implements fail-closed access control with:
    - Role hierarchy and permission inheritance
    - Domain-scoped permissions
    - Complete audit logging
    - Rate limiting for failed attempts
    """

    def __init__(self) -> None:
        """Initialize the RBAC manager."""
        # In-memory storage (replace with repository in production)
        self._role_assignments: Dict[str, List[UserRoleAssignment]] = {}
        self._access_log: List[AccessAttempt] = []
        self._failed_attempts: Dict[str, int] = {}  # user_id -> count
        self._max_failed_attempts = 5

    def _get_all_permissions(self, role: Role) -> Set[Permission]:
        """
        Get all permissions for a role, including inherited permissions.

        Args:
            role: The role to get permissions for

        Returns:
            Set of all permissions (direct + inherited)
        """
        permissions = set(ROLE_PERMISSIONS.get(role, set()))

        # Add inherited permissions from parent roles
        for parent_role in ROLE_HIERARCHY.get(role, []):
            permissions.update(self._get_all_permissions(parent_role))

        return permissions

    def assign_role(
        self,
        user_id: str,
        role: Role,
        domain: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserRoleAssignment:
        """
        Assign a role to a user.

        Args:
            user_id: The user to assign the role to
            role: The role to assign
            domain: Optional domain scope
            granted_by: ID of user granting the role
            expires_at: Optional expiration time

        Returns:
            The created role assignment
        """
        assignment = UserRoleAssignment(
            user_id=user_id,
            role=role,
            domain=domain,
            granted_by=granted_by,
            expires_at=expires_at,
        )

        if user_id not in self._role_assignments:
            self._role_assignments[user_id] = []

        self._role_assignments[user_id].append(assignment)

        logger.info(
            f"Role {role.value} assigned to user {user_id} "
            f"(domain={domain}, expires={expires_at})"
        )

        return assignment

    def revoke_role(
        self,
        user_id: str,
        role: Role,
        domain: Optional[str] = None,
    ) -> bool:
        """
        Revoke a role from a user.

        Args:
            user_id: The user to revoke the role from
            role: The role to revoke
            domain: Optional domain scope

        Returns:
            True if role was revoked, False if not found
        """
        if user_id not in self._role_assignments:
            return False

        original_count = len(self._role_assignments[user_id])
        self._role_assignments[user_id] = [
            a for a in self._role_assignments[user_id]
            if not (a.role == role and a.domain == domain)
        ]

        revoked = len(self._role_assignments[user_id]) < original_count

        if revoked:
            logger.info(
                f"Role {role.value} revoked from user {user_id} "
                f"(domain={domain})"
            )

        return revoked

    def get_user_roles(
        self,
        user_id: str,
        domain: Optional[str] = None,
    ) -> List[Role]:
        """
        Get all valid roles for a user.

        Args:
            user_id: The user to get roles for
            domain: Optional domain to filter by

        Returns:
            List of valid roles for the user
        """
        assignments = self._role_assignments.get(user_id, [])

        roles = []
        for assignment in assignments:
            if not assignment.is_valid():
                continue

            # Include global roles (domain=None) and matching domain roles
            if assignment.domain is None or assignment.domain == domain:
                roles.append(assignment.role)

        return roles

    def get_user_permissions(
        self,
        user_id: str,
        domain: Optional[str] = None,
    ) -> Set[Permission]:
        """
        Get all permissions for a user.

        Args:
            user_id: The user to get permissions for
            domain: Optional domain to filter by

        Returns:
            Set of all permissions the user has
        """
        roles = self.get_user_roles(user_id, domain)

        permissions: Set[Permission] = set()
        for role in roles:
            permissions.update(self._get_all_permissions(role))

        return permissions

    def has_permission(
        self,
        user_id: str,
        permission: Permission,
        domain: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> bool:
        """
        Check if a user has a specific permission.

        This is the main access control check. It implements fail-closed
        design: if anything is unclear, access is denied.

        Args:
            user_id: The user to check
            permission: The permission to check for
            domain: Optional domain scope
            resource_id: Optional resource ID for logging

        Returns:
            True if user has permission, False otherwise
        """
        # Check rate limiting
        if self._is_rate_limited(user_id):
            self._log_access(
                user_id=user_id,
                permission=permission.value,
                resource_type="permission_check",
                resource_id=resource_id,
                domain=domain,
                granted=False,
                reason="Rate limited due to excessive failed attempts",
            )
            return False

        # Get user permissions
        user_permissions = self.get_user_permissions(user_id, domain)

        # Check permission
        granted = permission in user_permissions

        # Log the attempt
        reason = "Permission granted" if granted else "Permission denied"
        self._log_access(
            user_id=user_id,
            permission=permission.value,
            resource_type="permission_check",
            resource_id=resource_id,
            domain=domain,
            granted=granted,
            reason=reason,
        )

        # Track failed attempts
        if not granted:
            self._record_failed_attempt(user_id)
        else:
            self._clear_failed_attempts(user_id)

        return granted

    def check_permission(
        self,
        user_id: str,
        permission: str,
        domain: Optional[str] = None,
    ) -> bool:
        """
        Check if a user has permission (string-based interface).

        Supports composite permissions like "submit_decision:politics".

        Args:
            user_id: The user to check
            permission: Permission string (may include domain suffix)
            domain: Optional domain override

        Returns:
            True if user has permission, False otherwise
        """
        # Parse permission string
        parts = permission.split(":")
        perm_name = parts[0]
        perm_domain = parts[1] if len(parts) > 1 else domain

        # Try to convert to Permission enum
        try:
            perm = Permission(perm_name)
        except ValueError:
            # Unknown permission - fail closed
            self._log_access(
                user_id=user_id,
                permission=perm_name,
                resource_type="permission_check",
                resource_id=None,
                domain=perm_domain,
                granted=False,
                reason=f"Unknown permission: {perm_name}",
            )
            return False

        return self.has_permission(user_id, perm, perm_domain)

    def _log_access(
        self,
        user_id: str,
        permission: str,
        resource_type: str,
        resource_id: Optional[str],
        domain: Optional[str],
        granted: bool,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessAttempt:
        """
        Log an access attempt.

        Args:
            user_id: User making the attempt
            permission: Permission being checked
            resource_type: Type of resource
            resource_id: ID of specific resource
            domain: Domain scope
            granted: Whether access was granted
            reason: Reason for the decision
            metadata: Additional metadata

        Returns:
            The logged access attempt
        """
        attempt = AccessAttempt(
            id=_generate_id("acc"),
            user_id=user_id,
            permission=permission,
            resource_type=resource_type,
            resource_id=resource_id,
            domain=domain,
            granted=granted,
            reason=reason,
            metadata=metadata or {},
        )

        self._access_log.append(attempt)

        # Log to standard logger
        log_level = logging.DEBUG if granted else logging.WARNING
        logger.log(
            log_level,
            f"Access {'granted' if granted else 'denied'}: "
            f"user={user_id}, permission={permission}, "
            f"domain={domain}, reason={reason}"
        )

        return attempt

    def _is_rate_limited(self, user_id: str) -> bool:
        """Check if a user is rate limited due to failed attempts."""
        return self._failed_attempts.get(user_id, 0) >= self._max_failed_attempts

    def _record_failed_attempt(self, user_id: str) -> None:
        """Record a failed access attempt."""
        self._failed_attempts[user_id] = self._failed_attempts.get(user_id, 0) + 1

        if self._failed_attempts[user_id] >= self._max_failed_attempts:
            logger.warning(
                f"User {user_id} rate limited after "
                f"{self._failed_attempts[user_id]} failed attempts"
            )

    def _clear_failed_attempts(self, user_id: str) -> None:
        """Clear failed attempt counter for a user."""
        if user_id in self._failed_attempts:
            del self._failed_attempts[user_id]

    def get_access_log(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AccessAttempt]:
        """
        Get access log entries.

        Args:
            user_id: Optional filter by user
            limit: Maximum number of entries to return

        Returns:
            List of access attempts
        """
        if user_id:
            entries = [a for a in self._access_log if a.user_id == user_id]
        else:
            entries = self._access_log

        # Return most recent entries
        return sorted(entries, key=lambda a: a.timestamp, reverse=True)[:limit]

    def get_denied_attempts(
        self,
        limit: int = 100,
    ) -> List[AccessAttempt]:
        """
        Get denied access attempts for security monitoring.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of denied access attempts
        """
        denied = [a for a in self._access_log if not a.granted]
        return sorted(denied, key=lambda a: a.timestamp, reverse=True)[:limit]

    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._role_assignments.clear()
        self._access_log.clear()
        self._failed_attempts.clear()


# Singleton instance
_rbac_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get or create the default RBACManager instance."""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager


def reset_rbac_manager() -> None:
    """Reset the global RBACManager instance (for testing)."""
    global _rbac_manager
    _rbac_manager = None
