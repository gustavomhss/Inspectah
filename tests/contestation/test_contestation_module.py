"""
Tests for ContestationModule — S41 Wave 0

Basic setup tests for the contestation module structure.
"""

from __future__ import annotations

import pytest

from app.contestation import ContestationModule, create_contestation_module


class TestContestationModule:
    """Tests for ContestationModule Wave 0 setup."""

    def test_create_module(self) -> None:
        """Test creating a contestation module."""
        module = ContestationModule()
        assert module is not None
        assert module.version == "1.0.0"

    def test_module_disabled_by_default(self) -> None:
        """Test module is disabled by default."""
        module = ContestationModule()
        assert not module.is_enabled()

    def test_get_version(self) -> None:
        """Test get_version returns correct version."""
        module = ContestationModule()
        assert module.get_version() == "1.0.0"

    def test_factory_function(self) -> None:
        """Test factory function creates module."""
        module = create_contestation_module()
        assert module is not None
        assert isinstance(module, ContestationModule)
        assert module.version == "1.0.0"

    def test_enable_module(self) -> None:
        """Test enabling the module."""
        module = ContestationModule()
        assert not module.is_enabled()
        module.enable()
        assert module.is_enabled()

    def test_disable_module(self) -> None:
        """Test disabling the module."""
        module = ContestationModule()
        module.enable()
        assert module.is_enabled()
        module.disable()
        assert not module.is_enabled()

    def test_service_property(self) -> None:
        """Test service property returns ContestationService."""
        from app.contestation import ContestationService
        module = ContestationModule()
        service = module.service
        assert service is not None
        assert isinstance(service, ContestationService)
        # Calling again should return same instance
        assert module.service is service

    def test_acordao_service_property(self) -> None:
        """Test acordao_service property returns AcordaoService."""
        from app.contestation import AcordaoService
        module = ContestationModule()
        service = module.acordao_service
        assert service is not None
        assert isinstance(service, AcordaoService)
        # Calling again should return same instance
        assert module.acordao_service is service

    def test_appeal_service_property(self) -> None:
        """Test appeal_service property returns AppealService."""
        from app.contestation import AppealService
        module = ContestationModule()
        service = module.appeal_service
        assert service is not None
        assert isinstance(service, AppealService)
        # Calling again should return same instance
        assert module.appeal_service is service


class TestFeatureFlagIntegration:
    """Tests for S41 feature flag integration."""

    def test_s41_feature_flags_exist(self) -> None:
        """Test S41 feature flags are registered."""
        from app.config.feature_flags import FEATURE_FLAGS

        assert "s41_guardian_orchestrator" in FEATURE_FLAGS
        assert "s41_contestation" in FEATURE_FLAGS
        assert "s41_trails" in FEATURE_FLAGS
        assert "s41_cases_lifecycle" in FEATURE_FLAGS

    def test_s41_feature_flags_default_disabled(self) -> None:
        """Test S41 feature flags are disabled by default."""
        from app.config.feature_flags import FEATURE_FLAGS

        assert FEATURE_FLAGS["s41_guardian_orchestrator"] is False
        assert FEATURE_FLAGS["s41_contestation"] is False
        assert FEATURE_FLAGS["s41_trails"] is False
        assert FEATURE_FLAGS["s41_cases_lifecycle"] is False

    def test_can_check_s41_flags_via_manager(self) -> None:
        """Test S41 flags can be checked via FeatureFlagManager."""
        from app.config.feature_flags import FeatureFlagManager

        manager = FeatureFlagManager()

        # All S41 flags should be disabled by default
        assert not manager.is_enabled("s41_guardian_orchestrator")
        assert not manager.is_enabled("s41_contestation")
        assert not manager.is_enabled("s41_trails")
        assert not manager.is_enabled("s41_cases_lifecycle")

    def test_can_enable_s41_flags_at_runtime(self) -> None:
        """Test S41 flags can be enabled at runtime."""
        from app.config.feature_flags import FeatureFlagManager

        manager = FeatureFlagManager()

        # Enable contestation flag
        manager.set("s41_contestation", True)
        assert manager.is_enabled("s41_contestation")

        # Other flags should remain disabled
        assert not manager.is_enabled("s41_guardian_orchestrator")
        assert not manager.is_enabled("s41_trails")

        # Reset
        manager.reset("s41_contestation")
        assert not manager.is_enabled("s41_contestation")
