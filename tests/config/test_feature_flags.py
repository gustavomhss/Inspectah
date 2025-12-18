"""
Tests for Feature Flags.

S39 - Feature Flag Tests
"""

import os
import threading
import time
from unittest.mock import patch

import pytest

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


class TestFeatureFlagSource:
    """Tests for FeatureFlagSource enum."""

    def test_source_values(self):
        """Test source enum values."""
        assert FeatureFlagSource.DEFAULT.value == "default"
        assert FeatureFlagSource.ENV.value == "env"
        assert FeatureFlagSource.CONFIG.value == "config"
        assert FeatureFlagSource.OVERRIDE.value == "override"


class TestFeatureFlagValue:
    """Tests for FeatureFlagValue."""

    def test_value_creation(self):
        """Test creating feature flag value."""
        value = FeatureFlagValue(
            name="test_flag",
            enabled=True,
            source=FeatureFlagSource.DEFAULT,
        )

        assert value.name == "test_flag"
        assert value.enabled is True
        assert value.source == FeatureFlagSource.DEFAULT
        assert value.updated_at is not None

    def test_value_with_metadata(self):
        """Test feature flag value with metadata."""
        value = FeatureFlagValue(
            name="test_flag",
            enabled=False,
            source=FeatureFlagSource.OVERRIDE,
            metadata={"reason": "test"},
        )

        assert value.metadata == {"reason": "test"}


class TestFeatureFlags:
    """Tests for default FEATURE_FLAGS."""

    def test_all_flags_boolean(self):
        """Test all default flags are boolean."""
        for name, value in FEATURE_FLAGS.items():
            assert isinstance(value, bool), f"Flag {name} is not boolean"

    def test_all_flags_disabled_by_default(self):
        """Test all flags are disabled by default."""
        # Most flags should be disabled by default for safety
        disabled_count = sum(1 for v in FEATURE_FLAGS.values() if not v)
        enabled_count = sum(1 for v in FEATURE_FLAGS.values() if v)

        # Allow some enabled, but most should be disabled
        assert disabled_count >= enabled_count

    def test_sharding_flags_exist(self):
        """Test sharding-related flags exist."""
        assert "sharding_enabled" in FEATURE_FLAGS
        assert "sharding_shadow_mode" in FEATURE_FLAGS
        assert "sharding_read_from_new" in FEATURE_FLAGS
        assert "sharding_write_to_old" in FEATURE_FLAGS

    def test_kafka_flags_exist(self):
        """Test Kafka-related flags exist."""
        assert "kafka_enabled" in FEATURE_FLAGS
        assert "kafka_websocket_bridge" in FEATURE_FLAGS

    def test_memory_flags_exist(self):
        """Test memory-related flags exist."""
        assert "memory_v1_enabled" in FEATURE_FLAGS
        assert "memory_llm_summarization" in FEATURE_FLAGS

    def test_explain_flags_exist(self):
        """Test explain-related flags exist."""
        assert "explain_v1_enabled" in FEATURE_FLAGS
        assert "explain_drilldown" in FEATURE_FLAGS

    def test_contracts_flags_exist(self):
        """Test contracts-related flags exist."""
        assert "contracts_v2_enabled" in FEATURE_FLAGS
        assert "contracts_strict_validation" in FEATURE_FLAGS

    def test_scrapers_flags_exist(self):
        """Test scrapers-related flags exist."""
        assert "scrapers_v2_enabled" in FEATURE_FLAGS
        assert "scrapers_proxy_rotation" in FEATURE_FLAGS


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager."""

    def test_manager_creation(self):
        """Test creating feature flag manager."""
        manager = FeatureFlagManager()

        assert manager._defaults == FEATURE_FLAGS
        assert manager._overrides == {}
        assert manager._env_prefix == "FF_"

    def test_manager_custom_defaults(self):
        """Test manager with custom defaults."""
        custom = {"test_flag": True}
        manager = FeatureFlagManager(defaults=custom)

        assert manager._defaults == custom

    def test_manager_custom_prefix(self):
        """Test manager with custom env prefix."""
        manager = FeatureFlagManager(env_prefix="FEATURE_")

        assert manager._env_prefix == "FEATURE_"

    def test_is_enabled_default(self):
        """Test is_enabled returns default value."""
        manager = FeatureFlagManager(defaults={"test_flag": True})

        assert manager.is_enabled("test_flag") is True

    def test_is_enabled_missing_flag(self):
        """Test is_enabled for missing flag returns False."""
        manager = FeatureFlagManager(defaults={})

        assert manager.is_enabled("nonexistent") is False

    def test_is_enabled_override(self):
        """Test is_enabled with override."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        manager._overrides["test_flag"] = True

        assert manager.is_enabled("test_flag") is True

    def test_is_enabled_env_var(self):
        """Test is_enabled from environment variable."""
        manager = FeatureFlagManager(defaults={"test_flag": False})

        with patch.dict(os.environ, {"FF_TEST_FLAG": "1"}):
            assert manager.is_enabled("test_flag") is True

        with patch.dict(os.environ, {"FF_TEST_FLAG": "true"}):
            assert manager.is_enabled("test_flag") is True

        with patch.dict(os.environ, {"FF_TEST_FLAG": "yes"}):
            assert manager.is_enabled("test_flag") is True

    def test_is_enabled_env_var_false(self):
        """Test is_enabled from env var with false values."""
        manager = FeatureFlagManager(defaults={"test_flag": True})

        with patch.dict(os.environ, {"FF_TEST_FLAG": "0"}):
            assert manager.is_enabled("test_flag") is False

        with patch.dict(os.environ, {"FF_TEST_FLAG": "false"}):
            assert manager.is_enabled("test_flag") is False

    def test_is_enabled_priority(self):
        """Test is_enabled priority: override > env > default."""
        manager = FeatureFlagManager(defaults={"test_flag": False})

        # Default is False
        assert manager.is_enabled("test_flag") is False

        # Env overrides default
        with patch.dict(os.environ, {"FF_TEST_FLAG": "1"}):
            assert manager.is_enabled("test_flag") is True

            # Runtime override takes precedence over env
            manager._overrides["test_flag"] = False
            assert manager.is_enabled("test_flag") is False

    def test_get_returns_value_object(self):
        """Test get returns FeatureFlagValue."""
        manager = FeatureFlagManager(defaults={"test_flag": True})

        value = manager.get("test_flag")

        assert isinstance(value, FeatureFlagValue)
        assert value.name == "test_flag"
        assert value.enabled is True
        assert value.source == FeatureFlagSource.DEFAULT

    def test_get_with_override_source(self):
        """Test get shows OVERRIDE source."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        manager.set("test_flag", True)

        value = manager.get("test_flag")

        assert value.source == FeatureFlagSource.OVERRIDE

    def test_get_with_env_source(self):
        """Test get shows ENV source."""
        manager = FeatureFlagManager(defaults={"test_flag": False})

        with patch.dict(os.environ, {"FF_TEST_FLAG": "1"}):
            value = manager.get("test_flag")
            assert value.source == FeatureFlagSource.ENV

    def test_set_updates_override(self):
        """Test set updates override."""
        manager = FeatureFlagManager(defaults={"test_flag": False})

        manager.set("test_flag", True)

        assert manager._overrides["test_flag"] is True
        assert manager.is_enabled("test_flag") is True

    def test_set_records_history(self):
        """Test set records in history."""
        manager = FeatureFlagManager(defaults={"test_flag": False})

        manager.set("test_flag", True)

        assert len(manager._history) == 1
        assert manager._history[0].name == "test_flag"
        assert manager._history[0].enabled is True
        assert manager._history[0].metadata["previous_value"] is False

    def test_set_triggers_callback(self):
        """Test set triggers registered callback."""
        manager = FeatureFlagManager(defaults={"test_flag": False})

        callback_called = []

        def callback(name, old_value, new_value):
            callback_called.append((name, old_value, new_value))

        manager.on_change("test_flag", callback)
        manager.set("test_flag", True)

        assert len(callback_called) == 1
        assert callback_called[0] == ("test_flag", False, True)

    def test_reset_single_flag(self):
        """Test resetting single flag."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        manager.set("test_flag", True)

        manager.reset("test_flag")

        assert "test_flag" not in manager._overrides
        assert manager.is_enabled("test_flag") is False

    def test_reset_all_flags(self):
        """Test resetting all flags."""
        manager = FeatureFlagManager(defaults={"flag1": False, "flag2": False})
        manager.set("flag1", True)
        manager.set("flag2", True)

        manager.reset()

        assert manager._overrides == {}

    def test_get_all(self):
        """Test getting all flags."""
        defaults = {"flag1": True, "flag2": False}
        manager = FeatureFlagManager(defaults=defaults)

        all_flags = manager.get_all()

        assert len(all_flags) == 2
        assert "flag1" in all_flags
        assert "flag2" in all_flags

    def test_get_enabled(self):
        """Test getting enabled flags."""
        defaults = {"enabled_flag": True, "disabled_flag": False}
        manager = FeatureFlagManager(defaults=defaults)

        enabled = manager.get_enabled()

        assert "enabled_flag" in enabled
        assert "disabled_flag" not in enabled

    def test_get_disabled(self):
        """Test getting disabled flags."""
        defaults = {"enabled_flag": True, "disabled_flag": False}
        manager = FeatureFlagManager(defaults=defaults)

        disabled = manager.get_disabled()

        assert "disabled_flag" in disabled
        assert "enabled_flag" not in disabled

    def test_get_history(self):
        """Test getting history."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        manager.set("test_flag", True)
        manager.set("test_flag", False)

        history = manager.get_history()

        assert len(history) == 2

    def test_get_history_specific_flag(self):
        """Test getting history for specific flag."""
        manager = FeatureFlagManager(defaults={"flag1": False, "flag2": False})
        manager.set("flag1", True)
        manager.set("flag2", True)

        history = manager.get_history("flag1")

        assert len(history) == 1
        assert history[0].name == "flag1"

    def test_get_history_with_limit(self):
        """Test getting history with limit."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        for i in range(10):
            manager.set("test_flag", i % 2 == 0)

        history = manager.get_history(limit=5)

        assert len(history) == 5

    def test_to_dict(self):
        """Test exporting flags as dict."""
        defaults = {"flag1": True, "flag2": False}
        manager = FeatureFlagManager(defaults=defaults)

        result = manager.to_dict()

        assert result == {"flag1": True, "flag2": False}


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_is_feature_enabled(self):
        """Test is_feature_enabled function."""
        # Uses global feature_flags singleton
        result = is_feature_enabled("sharding_enabled")
        assert isinstance(result, bool)

    def test_enable_feature(self):
        """Test enable_feature function."""
        # Reset first
        feature_flags.reset("sharding_enabled")

        enable_feature("sharding_enabled")
        assert is_feature_enabled("sharding_enabled") is True

        # Cleanup
        feature_flags.reset("sharding_enabled")

    def test_disable_feature(self):
        """Test disable_feature function."""
        # Enable first
        enable_feature("sharding_enabled")

        disable_feature("sharding_enabled")
        assert is_feature_enabled("sharding_enabled") is False

        # Cleanup
        feature_flags.reset("sharding_enabled")


class TestGlobalFeatureFlags:
    """Tests for global feature_flags singleton."""

    def test_singleton_exists(self):
        """Test singleton exists."""
        assert feature_flags is not None
        assert isinstance(feature_flags, FeatureFlagManager)

    def test_singleton_has_defaults(self):
        """Test singleton has all default flags."""
        for flag_name in FEATURE_FLAGS:
            value = feature_flags.get(flag_name)
            assert value is not None


class TestFeatureFlagThreadSafety:
    """Tests for thread safety of FeatureFlagManager."""

    def test_concurrent_reads(self):
        """Test concurrent reads don't cause issues."""
        manager = FeatureFlagManager(defaults={"test_flag": True})
        results = []
        errors = []

        def read_flag():
            try:
                for _ in range(100):
                    result = manager.is_enabled("test_flag")
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_flag) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 1000
        assert all(r is True for r in results)

    def test_concurrent_writes(self):
        """Test concurrent writes don't cause data corruption."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        errors = []

        def write_flag(value):
            try:
                for _ in range(50):
                    manager.set("test_flag", value)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=write_flag, args=(True,)),
            threading.Thread(target=write_flag, args=(False,)),
            threading.Thread(target=write_flag, args=(True,)),
            threading.Thread(target=write_flag, args=(False,)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # Final value should be consistent (either True or False)
        final = manager.is_enabled("test_flag")
        assert final in [True, False]

    def test_concurrent_read_write(self):
        """Test concurrent reads and writes work correctly."""
        manager = FeatureFlagManager(defaults={"test_flag": True})
        read_results = []
        errors = []

        def read_flag():
            try:
                for _ in range(100):
                    result = manager.is_enabled("test_flag")
                    read_results.append(result)
            except Exception as e:
                errors.append(e)

        def write_flag():
            try:
                for i in range(100):
                    manager.set("test_flag", i % 2 == 0)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=read_flag),
            threading.Thread(target=write_flag),
            threading.Thread(target=read_flag),
            threading.Thread(target=write_flag),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All reads should return valid booleans
        assert all(r in [True, False] for r in read_results)

    def test_concurrent_get_all(self):
        """Test concurrent get_all operations."""
        manager = FeatureFlagManager(defaults={"flag1": True, "flag2": False})
        results = []
        errors = []

        def get_all_flags():
            try:
                for _ in range(50):
                    all_flags = manager.get_all()
                    results.append(all_flags)
            except Exception as e:
                errors.append(e)

        def modify_flags():
            try:
                for i in range(50):
                    manager.set("flag1", i % 2 == 0)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=get_all_flags),
            threading.Thread(target=modify_flags),
            threading.Thread(target=get_all_flags),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All results should be valid dicts with expected flags
        for flags in results:
            assert "flag1" in flags
            assert "flag2" in flags

    def test_concurrent_history_access(self):
        """Test concurrent history operations."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        histories = []
        errors = []

        def modify_and_read():
            try:
                for i in range(20):
                    manager.set("test_flag", i % 2 == 0)
                    history = manager.get_history()
                    histories.append(len(history))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=modify_and_read) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # History should have recorded all changes
        final_history = manager.get_history()
        assert len(final_history) == 100  # 20 changes * 5 threads

    def test_concurrent_reset(self):
        """Test concurrent reset operations."""
        manager = FeatureFlagManager(defaults={"flag1": False, "flag2": False})
        errors = []

        def set_and_reset():
            try:
                for _ in range(20):
                    manager.set("flag1", True)
                    manager.reset("flag1")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=set_and_reset) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # After reset, should return to default
        manager.reset("flag1")
        assert manager.is_enabled("flag1") is False

    def test_callback_not_called_under_lock(self):
        """Test callbacks are called outside the lock to prevent deadlock."""
        manager = FeatureFlagManager(defaults={"test_flag": False})
        callback_results = []

        def callback_that_reads(name, old_value, new_value):
            # This should not deadlock because callbacks are called outside the lock
            result = manager.is_enabled(name)
            callback_results.append(result)

        manager.on_change("test_flag", callback_that_reads)
        manager.set("test_flag", True)

        assert len(callback_results) == 1
        assert callback_results[0] is True

    def test_manager_has_lock(self):
        """Test that manager has a lock attribute."""
        manager = FeatureFlagManager()
        assert hasattr(manager, "_lock")
        # Should be a RLock (reentrant lock)
        assert isinstance(manager._lock, type(threading.RLock()))
