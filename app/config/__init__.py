"""
S39 - Configuration Module

Provides configuration management including:
- Feature flags for gradual rollout
"""

from app.config.feature_flags import (
    FEATURE_FLAGS,
    FeatureFlagManager,
    FeatureFlagSource,
    FeatureFlagValue,
    feature_flags,
    is_feature_enabled,
    enable_feature,
    disable_feature,
)

__all__ = [
    "FEATURE_FLAGS",
    "FeatureFlagManager",
    "FeatureFlagSource",
    "FeatureFlagValue",
    "feature_flags",
    "is_feature_enabled",
    "enable_feature",
    "disable_feature",
]
