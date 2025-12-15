"""
S38: Tests for Policy Version Service
"""
import pytest
from datetime import datetime, timezone

from app.policies.models import PromotionPolicyConfig
from app.policies.version_service import (
    PolicyStatus,
    ChangeType,
    PolicyVersion,
    PolicyVersionRepository,
    PolicyVersionService,
)


class TestPolicyVersionRepository:
    """Tests for PolicyVersionRepository."""

    @pytest.fixture
    def repo(self):
        return PolicyVersionRepository()

    def test_save_and_get_version(self, repo):
        """Test saving and retrieving a version."""
        config = PromotionPolicyConfig(
            name="test_policy",
            domain="health",
            min_confidence=0.8,
            min_sources=3,
        )

        version = PolicyVersion(
            version_id="pv_test123",
            policy_id="policy:health:test_policy",
            version_number=1,
            config=config,
            status=PolicyStatus.DRAFT,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            created_by="test@example.com",
            content_hash="abc123",
        )

        repo.save_version(version)
        result = repo.get_version("pv_test123")

        assert result is not None
        assert result.version_id == "pv_test123"
        assert result.config.name == "test_policy"

    def test_get_versions_for_policy(self, repo):
        """Test getting all versions for a policy."""
        config = PromotionPolicyConfig(
            name="multi_version",
            domain="politics",
            min_confidence=0.9,
            min_sources=5,
        )

        for i in range(3):
            version = PolicyVersion(
                version_id=f"pv_v{i}",
                policy_id="policy:politics:multi_version",
                version_number=i + 1,
                config=config,
                status=PolicyStatus.DRAFT,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                created_by="test@example.com",
                content_hash=f"hash{i}",
            )
            repo.save_version(version)

        versions = repo.get_versions_for_policy("policy:politics:multi_version")
        assert len(versions) == 3


class TestPolicyVersionService:
    """Tests for PolicyVersionService."""

    @pytest.fixture
    def service(self):
        return PolicyVersionService(approval_required=True)

    @pytest.fixture
    def service_no_approval(self):
        return PolicyVersionService(approval_required=False)

    def test_create_version(self, service):
        """Test creating a new version."""
        config = PromotionPolicyConfig(
            name="new_policy",
            domain="economy",
            min_confidence=0.75,
            min_sources=2,
        )

        version = service.create_version(
            config=config,
            created_by="admin@example.com",
            changelog="Initial version",
        )

        assert version.version_id.startswith("pv_")
        assert version.status == PolicyStatus.DRAFT
        assert version.version_number == 1
        assert version.created_by == "admin@example.com"

    def test_create_version_increments_number(self, service):
        """Test that version numbers increment."""
        config = PromotionPolicyConfig(
            name="versioned",
            domain="tech",
            min_confidence=0.7,
            min_sources=2,
        )

        v1 = service.create_version(config, "user@example.com")
        v2 = service.create_version(config, "user@example.com")

        assert v1.version_number == 1
        assert v2.version_number == 2

    def test_submit_for_review(self, service):
        """Test submitting a draft for review."""
        config = PromotionPolicyConfig(
            name="review_test",
            domain="science",
            min_confidence=0.85,
            min_sources=4,
        )

        version = service.create_version(config, "creator@example.com")
        assert version.status == PolicyStatus.DRAFT

        reviewed = service.submit_for_review(version.version_id, "creator@example.com")
        assert reviewed.status == PolicyStatus.PENDING_REVIEW

    def test_approve_version(self, service):
        """Test approving a version."""
        config = PromotionPolicyConfig(
            name="approval_test",
            domain="environment",
            min_confidence=0.8,
            min_sources=3,
        )

        version = service.create_version(config, "creator@example.com")
        service.submit_for_review(version.version_id, "creator@example.com")

        approved = service.approve(
            version.version_id,
            "approver@example.com",
            "Looks good!",
        )

        assert approved.status == PolicyStatus.APPROVED
        assert approved.approved_by == "approver@example.com"
        assert approved.approved_at is not None

    def test_activate_version(self, service):
        """Test activating a version."""
        config = PromotionPolicyConfig(
            name="activation_test",
            domain="sports",
            min_confidence=0.7,
            min_sources=2,
        )

        version = service.create_version(config, "creator@example.com")
        service.submit_for_review(version.version_id, "creator@example.com")
        service.approve(version.version_id, "approver@example.com")

        activated = service.activate(version.version_id, "admin@example.com")

        assert activated.status == PolicyStatus.ACTIVE
        assert activated.activated_at is not None

    def test_activate_without_approval_fails(self, service):
        """Test that activation requires approval when configured."""
        config = PromotionPolicyConfig(
            name="no_approval",
            domain="test",
            min_confidence=0.5,
            min_sources=1,
        )

        version = service.create_version(config, "creator@example.com")

        with pytest.raises(ValueError) as exc:
            service.activate(version.version_id, "admin@example.com")

        assert "APPROVED" in str(exc.value)

    def test_activate_without_approval_succeeds(self, service_no_approval):
        """Test activation without approval when not required."""
        config = PromotionPolicyConfig(
            name="quick_deploy",
            domain="test",
            min_confidence=0.5,
            min_sources=1,
        )

        version = service_no_approval.create_version(config, "creator@example.com")
        activated = service_no_approval.activate(version.version_id, "admin@example.com")

        assert activated.status == PolicyStatus.ACTIVE

    def test_get_active_policy(self, service_no_approval):
        """Test getting active policy for domain."""
        config = PromotionPolicyConfig(
            name="active_test",
            domain="active_domain",
            min_confidence=0.8,
            min_sources=3,
        )

        version = service_no_approval.create_version(config, "user@example.com")
        service_no_approval.activate(version.version_id, "admin@example.com")

        active = service_no_approval.get_active_policy("active_domain")

        assert active is not None
        assert active.name == "active_test"

    def test_compare_versions(self, service):
        """Test comparing two versions."""
        config1 = PromotionPolicyConfig(
            name="compare_test",
            domain="compare",
            min_confidence=0.7,
            min_sources=2,
        )
        config2 = PromotionPolicyConfig(
            name="compare_test",
            domain="compare",
            min_confidence=0.9,  # Different
            min_sources=5,       # Different
        )

        v1 = service.create_version(config1, "user@example.com")
        v2 = service.create_version(config2, "user@example.com")

        comparison = service.compare_versions(v1.version_id, v2.version_id)

        assert len(comparison.differences) >= 2
        diff_fields = [d["field"] for d in comparison.differences]
        assert "min_confidence" in diff_fields
        assert "min_sources" in diff_fields

    def test_audit_log(self, service):
        """Test audit log entries are created."""
        config = PromotionPolicyConfig(
            name="audit_test",
            domain="audit",
            min_confidence=0.8,
            min_sources=3,
        )

        version = service.create_version(config, "user@example.com")
        service.submit_for_review(version.version_id, "user@example.com")

        audit_log = service.get_audit_log()

        assert len(audit_log) >= 2  # CREATE and UPDATE
        assert any(e.change_type == ChangeType.CREATE for e in audit_log)

    def test_validation_rejects_invalid_config(self, service):
        """Test that invalid configs are rejected."""
        invalid_config = PromotionPolicyConfig(
            name="",  # Invalid: empty name
            domain="test",
            min_confidence=1.5,  # Invalid: > 1
            min_sources=-1,      # Invalid: < 0
        )

        with pytest.raises(ValueError):
            service.create_version(invalid_config, "user@example.com")

    # Additional tests for 100% coverage

    def test_version_to_dict_with_all_dates(self, service):
        """Test PolicyVersion.to_dict with all optional dates set."""
        config = PromotionPolicyConfig(
            name="to_dict_test",
            domain="test",
            min_confidence=0.8,
            min_sources=2,
        )
        version = service.create_version(config, "user@example.com")
        service.submit_for_review(version.version_id, "user@example.com")
        service.approve(version.version_id, "admin@example.com")
        activated = service.activate(version.version_id, "admin@example.com")

        result = activated.to_dict()
        assert result["approved_at"] is not None
        assert result["activated_at"] is not None

    def test_deactivate_version(self, service):
        """Test deactivating a version directly."""
        config = PromotionPolicyConfig(
            name="deactivate_test",
            domain="deactivate_domain",
            min_confidence=0.7,
            min_sources=2,
        )
        version = service.create_version(config, "user@example.com")
        service.submit_for_review(version.version_id, "user@example.com")
        service.approve(version.version_id, "admin@example.com")
        service.activate(version.version_id, "admin@example.com")

        deactivated = service.deactivate(
            version.version_id,
            "admin@example.com",
            "Testing deactivation",
        )

        assert deactivated.status == PolicyStatus.DEPRECATED
        assert deactivated.deactivated_at is not None

    def test_deactivate_not_found(self, service):
        """Test deactivate raises when version not found."""
        with pytest.raises(ValueError, match="not found"):
            service.deactivate("nonexistent_id", "admin@example.com")

    def test_rollback(self, service):
        """Test rollback to previous version."""
        config1 = PromotionPolicyConfig(
            name="rollback_test",
            domain="rollback_domain",
            min_confidence=0.7,
            min_sources=2,
        )
        config2 = PromotionPolicyConfig(
            name="rollback_test",
            domain="rollback_domain",
            min_confidence=0.9,
            min_sources=5,
        )

        # Create and activate v1
        v1 = service.create_version(config1, "user@example.com")
        service.submit_for_review(v1.version_id, "user@example.com")
        service.approve(v1.version_id, "admin@example.com")
        service.activate(v1.version_id, "admin@example.com")

        # Create and activate v2
        v2 = service.create_version(config2, "user@example.com")
        service.submit_for_review(v2.version_id, "user@example.com")
        service.approve(v2.version_id, "admin@example.com")
        service.activate(v2.version_id, "admin@example.com")

        # Rollback to v1
        rolled_back = service.rollback(
            "rollback_domain",
            v1.version_id,
            "admin@example.com",
            "Bug in v2",
        )

        assert rolled_back.status == PolicyStatus.ACTIVE
        assert rolled_back.config.min_confidence == config1.min_confidence

    def test_rollback_not_found(self, service):
        """Test rollback raises when target version not found."""
        with pytest.raises(ValueError, match="not found"):
            service.rollback(
                "test_domain",
                "nonexistent_id",
                "admin@example.com",
                "reason",
            )

    def test_rollback_wrong_domain(self, service):
        """Test rollback raises when version is from different domain."""
        config = PromotionPolicyConfig(
            name="wrong_domain_test",
            domain="domain_a",
            min_confidence=0.7,
            min_sources=2,
        )
        version = service.create_version(config, "user@example.com")

        with pytest.raises(ValueError, match="not for domain"):
            service.rollback(
                "domain_b",  # Different domain
                version.version_id,
                "admin@example.com",
                "reason",
            )

    def test_submit_for_review_not_found(self, service):
        """Test submit_for_review raises when version not found."""
        with pytest.raises(ValueError, match="not found"):
            service.submit_for_review("nonexistent_id", "user@example.com")

    def test_submit_for_review_wrong_status(self, service):
        """Test submit_for_review raises when not in DRAFT status."""
        config = PromotionPolicyConfig(
            name="status_test",
            domain="test",
            min_confidence=0.8,
            min_sources=2,
        )
        version = service.create_version(config, "user@example.com")
        service.submit_for_review(version.version_id, "user@example.com")

        with pytest.raises(ValueError, match="DRAFT"):
            service.submit_for_review(version.version_id, "user@example.com")

    def test_approve_not_found(self, service):
        """Test approve raises when version not found."""
        with pytest.raises(ValueError, match="not found"):
            service.approve("nonexistent_id", "admin@example.com")

    def test_approve_wrong_status(self, service):
        """Test approve raises when not in PENDING_REVIEW status."""
        config = PromotionPolicyConfig(
            name="approve_status_test",
            domain="test",
            min_confidence=0.8,
            min_sources=2,
        )
        version = service.create_version(config, "user@example.com")

        with pytest.raises(ValueError, match="PENDING_REVIEW"):
            service.approve(version.version_id, "admin@example.com")

    def test_activate_not_found(self, service):
        """Test activate raises when version not found."""
        with pytest.raises(ValueError, match="not found"):
            service.activate("nonexistent_id", "admin@example.com")

    def test_compare_versions_not_found(self, service):
        """Test compare_versions raises when version not found."""
        config = PromotionPolicyConfig(
            name="compare_error_test",
            domain="test",
            min_confidence=0.8,
            min_sources=2,
        )
        version = service.create_version(config, "user@example.com")

        with pytest.raises(ValueError, match="must exist"):
            service.compare_versions(version.version_id, "nonexistent_id")

    def test_get_version_history_by_domain_only(self, service):
        """Test get_version_history with domain only (no name)."""
        config1 = PromotionPolicyConfig(
            name="history_a",
            domain="history_domain",
            min_confidence=0.7,
            min_sources=2,
        )
        config2 = PromotionPolicyConfig(
            name="history_b",
            domain="history_domain",
            min_confidence=0.8,
            min_sources=3,
        )

        service.create_version(config1, "user@example.com")
        service.create_version(config2, "user@example.com")

        history = service.get_version_history("history_domain")
        assert len(history) == 2

    def test_get_active_policy_none(self, service):
        """Test get_active_policy returns None when no active."""
        result = service.get_active_policy("nonexistent_domain")
        assert result is None

    def test_custom_validator(self, service):
        """Test registering and using custom validator."""
        def custom_validator(config):
            errors = []
            if config.min_sources > 10:
                errors.append("min_sources cannot exceed 10")
            return errors

        service.register_validator(custom_validator)

        config = PromotionPolicyConfig(
            name="validator_test",
            domain="test",
            min_confidence=0.8,
            min_sources=15,  # Will fail custom validator
        )

        with pytest.raises(ValueError, match="exceed 10"):
            service.create_version(config, "user@example.com")

    def test_audit_log_filtered_by_policy(self, service):
        """Test audit log filtering by policy_id."""
        config1 = PromotionPolicyConfig(
            name="audit_a",
            domain="audit_filter",
            min_confidence=0.7,
            min_sources=2,
        )
        config2 = PromotionPolicyConfig(
            name="audit_b",
            domain="audit_filter",
            min_confidence=0.8,
            min_sources=3,
        )

        v1 = service.create_version(config1, "user@example.com")
        service.create_version(config2, "user@example.com")

        policy_id = f"policy:{config1.domain}:{config1.name}"
        log = service.get_audit_log(policy_id=policy_id)

        # Should only have entries for policy_a
        assert all(e.policy_id == policy_id for e in log)


class TestPolicyAuditEntry:
    """Tests for PolicyAuditEntry dataclass."""

    def test_audit_entry_to_dict_with_status(self):
        """Test audit entry to_dict with status values."""
        from app.policies.version_service import PolicyAuditEntry

        entry = PolicyAuditEntry(
            audit_id="pa_test",
            policy_id="policy:test:test",
            version_id="pv_test",
            change_type=ChangeType.UPDATE,
            changed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            changed_by="user@example.com",
            old_status=PolicyStatus.DRAFT,
            new_status=PolicyStatus.PENDING_REVIEW,
            details={"note": "testing"},
        )

        result = entry.to_dict()
        assert result["old_status"] == "draft"
        assert result["new_status"] == "pending_review"
        assert result["details"]["note"] == "testing"

    def test_audit_entry_to_dict_without_status(self):
        """Test audit entry to_dict with null status values."""
        from app.policies.version_service import PolicyAuditEntry

        entry = PolicyAuditEntry(
            audit_id="pa_test",
            policy_id="policy:test:test",
            version_id="pv_test",
            change_type=ChangeType.CREATE,
            changed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            changed_by="user@example.com",
        )

        result = entry.to_dict()
        assert result["old_status"] is None
        assert result["new_status"] is None
