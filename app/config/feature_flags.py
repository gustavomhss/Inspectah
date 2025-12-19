"""
S39 - Feature Flags

Centralized feature flag management for gradual rollout.
Thread-safe implementation for concurrent access.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class FeatureFlagSource(str, Enum):
    """Source of feature flag value."""

    DEFAULT = "default"
    ENV = "env"
    CONFIG = "config"
    OVERRIDE = "override"


@dataclass
class FeatureFlagValue:
    """Value of a feature flag with metadata."""

    name: str
    enabled: bool
    source: FeatureFlagSource
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


# Default feature flags for S39
FEATURE_FLAGS: Dict[str, bool] = {
    # Sharding
    "sharding_enabled": False,
    "sharding_shadow_mode": False,  # Dual-write enabled
    "sharding_read_from_new": False,  # Read from shards
    "sharding_write_to_old": True,  # Write to legacy DB
    # Kafka Streaming
    "kafka_enabled": False,  # Enable Kafka streaming
    "kafka_websocket_bridge": False,  # Enable WebSocket bridge
    # Memory Controller
    "memory_v1_enabled": False,  # Enable Memory Controller v1
    "memory_llm_summarization": False,  # Enable LLM summarization
    # Explainability
    "explain_v1_enabled": False,  # Enable Explainability v1
    "explain_drilldown": False,  # Enable drill-down feature
    # Contracts
    "contracts_v2_enabled": False,  # Enable Contracts v2
    "contracts_strict_validation": False,  # Enable strict validation
    # Scrapers
    "scrapers_v2_enabled": False,  # Enable Scrapers v2
    "scrapers_proxy_rotation": False,  # Enable proxy rotation
    # S41: Governança v1
    "s41_guardian_orchestrator": False,  # Enable GuardianOrchestrator
    "s41_contestation": False,  # Enable contestation module
    "s41_trails": False,  # Enable DecisionTrails
    "s41_cases_lifecycle": False,  # Enable cases lifecycle management
}


class FeatureFlagManager:
    """
    Manages feature flags for gradual rollout.

    Features:
    - Default values from FEATURE_FLAGS dict
    - Override from environment variables
    - Runtime overrides
    - Change callbacks

    Usage:
        flags = FeatureFlagManager()

        if flags.is_enabled("sharding_enabled"):
            # Use sharding
            ...

        # Override at runtime
        flags.set("sharding_shadow_mode", True)

        # Get all flags
        all_flags = flags.get_all()
    """

    def __init__(
        self,
        defaults: Optional[Dict[str, bool]] = None,
        env_prefix: str = "FF_",
    ):
        self._defaults = defaults or FEATURE_FLAGS.copy()
        self._overrides: Dict[str, bool] = {}
        self._env_prefix = env_prefix
        self._callbacks: Dict[str, List[Callable[[str, bool, bool], None]]] = {}
        self._history: List[FeatureFlagValue] = []
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def is_enabled(self, name: str) -> bool:
        """
        Check if a feature flag is enabled.

        Priority:
        1. Runtime overrides
        2. Environment variables (FF_<NAME>=1|0|true|false)
        3. Default values

        Args:
            name: Feature flag name

        Returns:
            True if enabled, False otherwise
        """
        with self._lock:
            # Check overrides first
            if name in self._overrides:
                return self._overrides[name]

            # Check environment variable
            env_name = f"{self._env_prefix}{name.upper()}"
            env_value = os.environ.get(env_name)
            if env_value is not None:
                return env_value.lower() in ("1", "true", "yes", "on")

            # Return default
            return self._defaults.get(name, False)

    def get(self, name: str) -> FeatureFlagValue:
        """
        Get feature flag with metadata.

        Args:
            name: Feature flag name

        Returns:
            FeatureFlagValue with enabled status and source
        """
        with self._lock:
            # Determine source and value
            if name in self._overrides:
                source = FeatureFlagSource.OVERRIDE
                enabled = self._overrides[name]
            elif os.environ.get(f"{self._env_prefix}{name.upper()}"):
                source = FeatureFlagSource.ENV
                enabled = self._is_enabled_unlocked(name)
            elif name in self._defaults:
                source = FeatureFlagSource.DEFAULT
                enabled = self._defaults[name]
            else:
                source = FeatureFlagSource.DEFAULT
                enabled = False

            return FeatureFlagValue(
                name=name,
                enabled=enabled,
                source=source,
            )

    def _is_enabled_unlocked(self, name: str) -> bool:
        """Check if enabled without lock (for internal use when lock is held)."""
        if name in self._overrides:
            return self._overrides[name]
        env_name = f"{self._env_prefix}{name.upper()}"
        env_value = os.environ.get(env_name)
        if env_value is not None:
            return env_value.lower() in ("1", "true", "yes", "on")
        return self._defaults.get(name, False)

    def set(self, name: str, enabled: bool) -> None:
        """
        Set a feature flag at runtime.

        Args:
            name: Feature flag name
            enabled: Whether to enable the flag
        """
        callbacks_to_call = []

        with self._lock:
            old_value = self._is_enabled_unlocked(name)
            self._overrides[name] = enabled

            # Record in history
            self._history.append(
                FeatureFlagValue(
                    name=name,
                    enabled=enabled,
                    source=FeatureFlagSource.OVERRIDE,
                    metadata={"previous_value": old_value},
                )
            )

            # Collect callbacks (but call them outside the lock)
            if name in self._callbacks:
                callbacks_to_call = list(self._callbacks[name])

        # Trigger callbacks outside the lock to avoid deadlocks
        for callback in callbacks_to_call:
            try:
                callback(name, old_value, enabled)
            except Exception as e:
                logger.error(f"Feature flag callback error for {name}: {e}")

        logger.info(f"Feature flag '{name}' set to {enabled} (was {old_value})")

    def reset(self, name: Optional[str] = None) -> None:
        """
        Reset feature flag(s) to default.

        Args:
            name: Specific flag to reset, or None to reset all
        """
        with self._lock:
            if name:
                self._overrides.pop(name, None)
                logger.info(f"Feature flag '{name}' reset to default")
            else:
                self._overrides.clear()
                logger.info("All feature flags reset to defaults")

    def get_all(self) -> Dict[str, FeatureFlagValue]:
        """
        Get all feature flags with their values.

        Returns:
            Dict mapping flag name to FeatureFlagValue
        """
        with self._lock:
            all_flags = {}
            for name in self._defaults:
                # Use internal method to avoid double-locking
                if name in self._overrides:
                    source = FeatureFlagSource.OVERRIDE
                    enabled = self._overrides[name]
                elif os.environ.get(f"{self._env_prefix}{name.upper()}"):
                    source = FeatureFlagSource.ENV
                    enabled = self._is_enabled_unlocked(name)
                else:
                    source = FeatureFlagSource.DEFAULT
                    enabled = self._defaults[name]
                all_flags[name] = FeatureFlagValue(
                    name=name,
                    enabled=enabled,
                    source=source,
                )
            return all_flags

    def get_enabled(self) -> List[str]:
        """Get list of enabled feature flags."""
        with self._lock:
            return [name for name in self._defaults if self._is_enabled_unlocked(name)]

    def get_disabled(self) -> List[str]:
        """Get list of disabled feature flags."""
        with self._lock:
            return [name for name in self._defaults if not self._is_enabled_unlocked(name)]

    def on_change(
        self,
        name: str,
        callback: Callable[[str, bool, bool], None],
    ) -> None:
        """
        Register callback for feature flag changes.

        Args:
            name: Feature flag name
            callback: Function called with (name, old_value, new_value)
        """
        with self._lock:
            if name not in self._callbacks:
                self._callbacks[name] = []
            self._callbacks[name].append(callback)

    def get_history(
        self,
        name: Optional[str] = None,
        limit: int = 100,
    ) -> List[FeatureFlagValue]:
        """
        Get change history for feature flags.

        Args:
            name: Specific flag to get history for, or None for all
            limit: Maximum number of entries

        Returns:
            List of FeatureFlagValue changes
        """
        with self._lock:
            if name:
                history = [h for h in self._history if h.name == name]
            else:
                history = list(self._history)
            return history[-limit:]

    def to_dict(self) -> Dict[str, bool]:
        """Export all flags as simple dict."""
        with self._lock:
            return {name: self._is_enabled_unlocked(name) for name in self._defaults}


# Global singleton instance
feature_flags = FeatureFlagManager()


# Convenience functions
def is_feature_enabled(name: str) -> bool:
    """Check if a feature is enabled."""
    return feature_flags.is_enabled(name)


def enable_feature(name: str) -> None:
    """Enable a feature."""
    feature_flags.set(name, True)


def disable_feature(name: str) -> None:
    """Disable a feature."""
    feature_flags.set(name, False)
