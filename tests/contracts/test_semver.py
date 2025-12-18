"""
S39: Tests for Semantic Versioning Enforcement
"""
import pytest
from datetime import datetime, timezone, timedelta

from app.contracts.semver import (
    SemVer,
    VersionRange,
    VersionedContract,
    SemverEnforcer,
    VersionChangeType,
    CompatibilityLevel,
    parse_version,
    is_compatible,
    get_enforcer,
)


class TestSemVerParsing:
    """Tests for SemVer parsing."""

    def test_parse_simple_version(self):
        version = SemVer.parse("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_zero_version(self):
        version = SemVer.parse("0.0.0")
        assert version.major == 0
        assert version.minor == 0
        assert version.patch == 0

    def test_parse_large_version(self):
        version = SemVer.parse("100.200.300")
        assert version.major == 100
        assert version.minor == 200
        assert version.patch == 300

    def test_parse_with_prerelease(self):
        version = SemVer.parse("1.0.0-alpha")
        assert version.major == 1
        assert version.minor == 0
        assert version.patch == 0
        assert version.prerelease == "alpha"

    def test_parse_with_numeric_prerelease(self):
        version = SemVer.parse("1.0.0-alpha.1")
        assert version.prerelease == "alpha.1"

    def test_parse_with_build(self):
        version = SemVer.parse("1.0.0+build.123")
        assert version.build == "build.123"

    def test_parse_with_prerelease_and_build(self):
        version = SemVer.parse("1.0.0-beta.2+build.456")
        assert version.prerelease == "beta.2"
        assert version.build == "build.456"

    def test_parse_invalid_format(self):
        with pytest.raises(ValueError):
            SemVer.parse("invalid")

    def test_parse_missing_patch(self):
        with pytest.raises(ValueError):
            SemVer.parse("1.2")

    def test_parse_leading_zeros(self):
        with pytest.raises(ValueError):
            SemVer.parse("01.2.3")

    def test_try_parse_valid(self):
        version = SemVer.try_parse("1.2.3")
        assert version is not None
        assert version.major == 1

    def test_try_parse_invalid(self):
        version = SemVer.try_parse("invalid")
        assert version is None


class TestSemVerStringConversion:
    """Tests for SemVer string conversion."""

    def test_simple_version_str(self):
        version = SemVer(1, 2, 3)
        assert str(version) == "1.2.3"

    def test_version_with_prerelease_str(self):
        version = SemVer(1, 0, 0, prerelease="alpha")
        assert str(version) == "1.0.0-alpha"

    def test_version_with_build_str(self):
        version = SemVer(1, 0, 0, build="build.123")
        assert str(version) == "1.0.0+build.123"

    def test_version_with_all_components_str(self):
        version = SemVer(1, 0, 0, prerelease="rc.1", build="build.456")
        assert str(version) == "1.0.0-rc.1+build.456"


class TestSemVerComparison:
    """Tests for SemVer comparison."""

    def test_equal_versions(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("1.0.0")
        assert v1 == v2

    def test_less_than_major(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("2.0.0")
        assert v1 < v2

    def test_less_than_minor(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("1.1.0")
        assert v1 < v2

    def test_less_than_patch(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("1.0.1")
        assert v1 < v2

    def test_greater_than(self):
        v1 = SemVer.parse("2.0.0")
        v2 = SemVer.parse("1.9.9")
        assert v1 > v2

    def test_prerelease_lower_than_release(self):
        v1 = SemVer.parse("1.0.0-alpha")
        v2 = SemVer.parse("1.0.0")
        assert v1 < v2

    def test_prerelease_comparison_numeric(self):
        v1 = SemVer.parse("1.0.0-alpha.1")
        v2 = SemVer.parse("1.0.0-alpha.2")
        assert v1 < v2

    def test_prerelease_comparison_alpha(self):
        v1 = SemVer.parse("1.0.0-alpha")
        v2 = SemVer.parse("1.0.0-beta")
        assert v1 < v2

    def test_prerelease_numeric_vs_alpha(self):
        v1 = SemVer.parse("1.0.0-1")
        v2 = SemVer.parse("1.0.0-alpha")
        assert v1 < v2  # Numeric has lower precedence

    def test_less_than_or_equal(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("1.0.0")
        v3 = SemVer.parse("1.0.1")
        assert v1 <= v2
        assert v1 <= v3

    def test_greater_than_or_equal(self):
        v1 = SemVer.parse("1.0.1")
        v2 = SemVer.parse("1.0.0")
        v3 = SemVer.parse("1.0.1")
        assert v1 >= v2
        assert v1 >= v3


class TestSemVerBumping:
    """Tests for SemVer version bumping."""

    def test_bump_major(self):
        version = SemVer.parse("1.2.3")
        bumped = version.bump_major()
        assert str(bumped) == "2.0.0"

    def test_bump_minor(self):
        version = SemVer.parse("1.2.3")
        bumped = version.bump_minor()
        assert str(bumped) == "1.3.0"

    def test_bump_patch(self):
        version = SemVer.parse("1.2.3")
        bumped = version.bump_patch()
        assert str(bumped) == "1.2.4"

    def test_with_prerelease(self):
        version = SemVer.parse("1.0.0")
        with_pre = version.with_prerelease("alpha")
        assert str(with_pre) == "1.0.0-alpha"

    def test_with_build(self):
        version = SemVer.parse("1.0.0")
        with_build = version.with_build("build.123")
        assert str(with_build) == "1.0.0+build.123"


class TestSemVerMethods:
    """Tests for other SemVer methods."""

    def test_is_stable_release(self):
        stable = SemVer.parse("1.0.0")
        assert stable.is_stable() is True

    def test_is_not_stable_prerelease(self):
        prerelease = SemVer.parse("1.0.0-alpha")
        assert prerelease.is_stable() is False

    def test_is_compatible_same_major(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("1.9.9")
        assert v1.is_compatible_with(v2) is True

    def test_is_not_compatible_different_major(self):
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("2.0.0")
        assert v1.is_compatible_with(v2) is False

    def test_to_tuple(self):
        version = SemVer.parse("1.2.3")
        assert version.to_tuple() == (1, 2, 3)


class TestVersionRange:
    """Tests for VersionRange."""

    def test_parse_exact_version(self):
        range_ = VersionRange.parse("1.2.3")
        assert range_.contains(SemVer.parse("1.2.3"))
        assert not range_.contains(SemVer.parse("1.2.4"))

    def test_parse_exact_with_equals(self):
        range_ = VersionRange.parse("=1.2.3")
        assert range_.contains(SemVer.parse("1.2.3"))

    def test_parse_greater_than_or_equal(self):
        range_ = VersionRange.parse(">=1.0.0")
        assert range_.contains(SemVer.parse("1.0.0"))
        assert range_.contains(SemVer.parse("2.0.0"))
        assert not range_.contains(SemVer.parse("0.9.9"))

    def test_parse_greater_than(self):
        range_ = VersionRange.parse(">1.0.0")
        assert not range_.contains(SemVer.parse("1.0.0"))
        assert range_.contains(SemVer.parse("1.0.1"))

    def test_parse_less_than_or_equal(self):
        range_ = VersionRange.parse("<=2.0.0")
        assert range_.contains(SemVer.parse("2.0.0"))
        assert range_.contains(SemVer.parse("1.0.0"))
        assert not range_.contains(SemVer.parse("2.0.1"))

    def test_parse_less_than(self):
        range_ = VersionRange.parse("<2.0.0")
        assert not range_.contains(SemVer.parse("2.0.0"))
        assert range_.contains(SemVer.parse("1.9.9"))

    def test_parse_caret_range(self):
        range_ = VersionRange.parse("^1.2.3")
        assert range_.contains(SemVer.parse("1.2.3"))
        assert range_.contains(SemVer.parse("1.9.9"))
        assert not range_.contains(SemVer.parse("2.0.0"))

    def test_parse_caret_range_zero_major(self):
        range_ = VersionRange.parse("^0.2.3")
        assert range_.contains(SemVer.parse("0.2.3"))
        assert range_.contains(SemVer.parse("0.2.9"))
        assert not range_.contains(SemVer.parse("0.3.0"))

    def test_parse_tilde_range(self):
        range_ = VersionRange.parse("~1.2.3")
        assert range_.contains(SemVer.parse("1.2.3"))
        assert range_.contains(SemVer.parse("1.2.9"))
        assert not range_.contains(SemVer.parse("1.3.0"))

    def test_parse_hyphen_range(self):
        range_ = VersionRange.parse("1.0.0 - 2.0.0")
        assert range_.contains(SemVer.parse("1.0.0"))
        assert range_.contains(SemVer.parse("1.5.0"))
        assert range_.contains(SemVer.parse("2.0.0"))
        assert not range_.contains(SemVer.parse("2.0.1"))

    def test_range_str(self):
        range_ = VersionRange.parse(">=1.0.0")
        assert ">=1.0.0" in str(range_)


class TestVersionedContract:
    """Tests for VersionedContract."""

    def test_create_contract(self):
        contract = VersionedContract(
            name="TestContract",
            version=SemVer.parse("1.0.0"),
        )
        assert contract.name == "TestContract"
        assert contract.deprecated is False

    def test_is_active_no_sunset(self):
        contract = VersionedContract(
            name="TestContract",
            version=SemVer.parse("1.0.0"),
        )
        assert contract.is_active() is True

    def test_is_active_future_sunset(self):
        future = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30)
        contract = VersionedContract(
            name="TestContract",
            version=SemVer.parse("1.0.0"),
            sunset_at=future,
        )
        assert contract.is_active() is True

    def test_is_not_active_past_sunset(self):
        past = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        contract = VersionedContract(
            name="TestContract",
            version=SemVer.parse("1.0.0"),
            sunset_at=past,
        )
        assert contract.is_active() is False


class TestSemverEnforcer:
    """Tests for SemverEnforcer."""

    def test_create_enforcer(self):
        enforcer = SemverEnforcer()
        assert enforcer.current_version == SemVer.parse("2.0.0")
        assert enforcer.min_supported == SemVer.parse("2.0.0")

    def test_create_custom_enforcer(self):
        enforcer = SemverEnforcer(
            current_version="3.0.0",
            min_supported_version="2.0.0",
        )
        assert enforcer.current_version == SemVer.parse("3.0.0")
        assert enforcer.min_supported == SemVer.parse("2.0.0")

    def test_register_contract(self):
        enforcer = SemverEnforcer()
        contract = enforcer.register_contract("TestAPI", "1.0.0")
        assert contract.name == "TestAPI"
        assert contract.version == SemVer.parse("1.0.0")

    def test_get_contract(self):
        enforcer = SemverEnforcer()
        enforcer.register_contract("TestAPI", "1.0.0")
        contract = enforcer.get_contract("TestAPI", "1.0.0")
        assert contract is not None
        assert contract.name == "TestAPI"

    def test_get_nonexistent_contract(self):
        enforcer = SemverEnforcer()
        contract = enforcer.get_contract("NonExistent", "1.0.0")
        assert contract is None

    def test_get_latest_contract(self):
        enforcer = SemverEnforcer()
        enforcer.register_contract("TestAPI", "1.0.0")
        enforcer.register_contract("TestAPI", "1.1.0")
        enforcer.register_contract("TestAPI", "2.0.0")

        latest = enforcer.get_latest_contract("TestAPI")
        assert latest is not None
        assert latest.version == SemVer.parse("2.0.0")

    def test_deprecate_contract(self):
        enforcer = SemverEnforcer()
        enforcer.register_contract("TestAPI", "1.0.0")
        contract = enforcer.deprecate_contract("TestAPI", "1.0.0", "2.0.0")

        assert contract is not None
        assert contract.deprecated is True
        assert contract.successor_version == SemVer.parse("2.0.0")
        assert contract.sunset_at is not None


class TestCompatibilityChecks:
    """Tests for compatibility checking."""

    def test_compatible_same_version(self):
        enforcer = SemverEnforcer()
        level = enforcer.check_compatibility("1.0.0", "1.0.0")
        assert level == CompatibilityLevel.COMPATIBLE

    def test_backward_compatible_minor(self):
        enforcer = SemverEnforcer()
        level = enforcer.check_compatibility("1.0.0", "1.1.0")
        assert level == CompatibilityLevel.BACKWARD_COMPATIBLE

    def test_compatible_patch(self):
        enforcer = SemverEnforcer()
        level = enforcer.check_compatibility("1.0.0", "1.0.1")
        assert level == CompatibilityLevel.COMPATIBLE

    def test_incompatible_major(self):
        enforcer = SemverEnforcer()
        level = enforcer.check_compatibility("1.0.0", "2.0.0")
        assert level == CompatibilityLevel.INCOMPATIBLE

    def test_incompatible_downgrade(self):
        enforcer = SemverEnforcer()
        level = enforcer.check_compatibility("2.0.0", "1.0.0")
        assert level == CompatibilityLevel.INCOMPATIBLE


class TestChangeTypeDetection:
    """Tests for change type detection."""

    def test_detect_no_change(self):
        enforcer = SemverEnforcer()
        change = enforcer.detect_change_type("1.0.0", "1.0.0")
        assert change == VersionChangeType.NONE

    def test_detect_major_change(self):
        enforcer = SemverEnforcer()
        change = enforcer.detect_change_type("1.0.0", "2.0.0")
        assert change == VersionChangeType.MAJOR

    def test_detect_minor_change(self):
        enforcer = SemverEnforcer()
        change = enforcer.detect_change_type("1.0.0", "1.1.0")
        assert change == VersionChangeType.MINOR

    def test_detect_patch_change(self):
        enforcer = SemverEnforcer()
        change = enforcer.detect_change_type("1.0.0", "1.0.1")
        assert change == VersionChangeType.PATCH


class TestBreakingChanges:
    """Tests for breaking change tracking."""

    def test_record_breaking_change(self):
        enforcer = SemverEnforcer()
        enforcer.record_breaking_change(
            version="2.0.0",
            description="Removed deprecated endpoints",
            affected_endpoints=["/v1/claims"],
            migration_guide="Use /v2/claims instead",
        )

        changes = enforcer.get_breaking_changes()
        assert len(changes) == 1
        assert changes[0]["version"] == "2.0.0"
        assert changes[0]["description"] == "Removed deprecated endpoints"

    def test_get_breaking_changes_filtered(self):
        enforcer = SemverEnforcer()
        enforcer.record_breaking_change("1.0.0", "Change 1")
        enforcer.record_breaking_change("2.0.0", "Change 2")
        enforcer.record_breaking_change("3.0.0", "Change 3")

        changes = enforcer.get_breaking_changes(from_version="1.5.0")
        assert len(changes) == 2

        changes = enforcer.get_breaking_changes(to_version="2.0.0")
        assert len(changes) == 2


class TestVersionSuggestion:
    """Tests for next version suggestion."""

    def test_suggest_major_bump(self):
        enforcer = SemverEnforcer(current_version="1.0.0")
        suggested = enforcer.suggest_next_version(VersionChangeType.MAJOR)
        assert suggested == SemVer.parse("2.0.0")

    def test_suggest_minor_bump(self):
        enforcer = SemverEnforcer(current_version="1.0.0")
        suggested = enforcer.suggest_next_version(VersionChangeType.MINOR)
        assert suggested == SemVer.parse("1.1.0")

    def test_suggest_patch_bump(self):
        enforcer = SemverEnforcer(current_version="1.0.0")
        suggested = enforcer.suggest_next_version(VersionChangeType.PATCH)
        assert suggested == SemVer.parse("1.0.1")

    def test_suggest_no_change(self):
        enforcer = SemverEnforcer(current_version="1.0.0")
        suggested = enforcer.suggest_next_version(VersionChangeType.NONE)
        assert suggested == SemVer.parse("1.0.0")

    def test_suggest_from_custom_version(self):
        enforcer = SemverEnforcer()
        suggested = enforcer.suggest_next_version(VersionChangeType.MAJOR, "3.5.2")
        assert suggested == SemVer.parse("4.0.0")


class TestVersionSupport:
    """Tests for version support checking."""

    def test_version_supported(self):
        enforcer = SemverEnforcer(current_version="2.1.0", min_supported_version="2.0.0")
        assert enforcer.is_version_supported("2.0.0") is True
        assert enforcer.is_version_supported("2.1.0") is True

    def test_version_not_supported_too_old(self):
        enforcer = SemverEnforcer(current_version="2.0.0", min_supported_version="2.0.0")
        assert enforcer.is_version_supported("1.0.0") is False

    def test_version_not_supported_different_major(self):
        enforcer = SemverEnforcer(current_version="2.0.0", min_supported_version="2.0.0")
        assert enforcer.is_version_supported("3.0.0") is False


class TestDeprecationWarnings:
    """Tests for deprecation warnings."""

    def test_no_warning_current_version(self):
        enforcer = SemverEnforcer(current_version="2.0.0", min_supported_version="2.0.0")
        warning = enforcer.get_deprecation_warning("2.0.0")
        assert warning is None

    def test_warning_old_version(self):
        enforcer = SemverEnforcer(current_version="2.1.0", min_supported_version="2.0.0")
        warning = enforcer.get_deprecation_warning("2.0.0")
        assert warning is not None
        assert "deprecated" in warning.lower()

    def test_warning_unsupported_version(self):
        enforcer = SemverEnforcer(current_version="2.0.0", min_supported_version="2.0.0")
        warning = enforcer.get_deprecation_warning("1.0.0")
        assert warning is not None
        assert "no longer supported" in warning.lower()


class TestVersionInfo:
    """Tests for version info retrieval."""

    def test_get_version_info(self):
        enforcer = SemverEnforcer()
        enforcer.register_contract("TestAPI", "1.0.0")
        enforcer.register_contract("TestAPI", "2.0.0")

        info = enforcer.get_version_info()
        assert "current" in info
        assert "min_supported" in info
        assert "contracts" in info
        assert "TestAPI" in info["contracts"]


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_parse_version_function(self):
        version = parse_version("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_is_compatible_function(self):
        assert is_compatible("1.0.0", "1.5.0") is True
        assert is_compatible("1.0.0", "2.0.0") is False

    def test_get_enforcer_singleton(self):
        enforcer = get_enforcer()
        assert enforcer is not None
        assert isinstance(enforcer, SemverEnforcer)


class TestEdgeCases:
    """Tests for edge cases."""

    def test_prerelease_comparison_different_lengths(self):
        v1 = SemVer.parse("1.0.0-alpha")
        v2 = SemVer.parse("1.0.0-alpha.1")
        assert v1 < v2

    def test_hash_equality(self):
        v1 = SemVer(1, 0, 0)
        v2 = SemVer(1, 0, 0)
        assert hash(v1) == hash(v2)
        assert {v1} == {v2}

    def test_compatible_versions_query(self):
        enforcer = SemverEnforcer()
        enforcer.register_contract("API", "1.0.0")
        enforcer.register_contract("API", "1.1.0")
        enforcer.register_contract("API", "2.0.0")

        compatible = enforcer.get_compatible_versions("API", "1.0.0")
        assert len(compatible) == 2
        assert all(c.version.major == 1 for c in compatible)


class TestSemverAdditionalCoverage:
    """Additional tests for better coverage."""

    def test_comparison_with_non_semver(self):
        v1 = SemVer(1, 0, 0)
        # NotImplemented triggers TypeError in Python when used with comparison operators
        # Test that comparing with non-SemVer raises TypeError
        with pytest.raises(TypeError):
            _ = v1 < "not a semver"
        with pytest.raises(TypeError):
            _ = v1 <= "not a semver"
        with pytest.raises(TypeError):
            _ = v1 > "not a semver"
        with pytest.raises(TypeError):
            _ = v1 >= "not a semver"

    def test_prerelease_longer_than_other(self):
        v1 = SemVer.parse("1.0.0-alpha.1.2")
        v2 = SemVer.parse("1.0.0-alpha.1")
        assert v1 > v2

    def test_prerelease_equal_length(self):
        v1 = SemVer.parse("1.0.0-alpha.1")
        v2 = SemVer.parse("1.0.0-alpha.1")
        assert v1 == v2

    def test_version_range_no_constraints(self):
        range_ = VersionRange()
        assert range_.contains(SemVer.parse("1.0.0"))
        assert range_.contains(SemVer.parse("99.99.99"))

    def test_version_range_str_exact(self):
        range_ = VersionRange(
            min_version=SemVer(1, 0, 0),
            max_version=SemVer(1, 0, 0),
            min_inclusive=True,
            max_inclusive=True,
        )
        assert "=1.0.0" in str(range_)

    def test_version_range_str_empty(self):
        range_ = VersionRange()
        assert "*" in str(range_)

    def test_get_compatible_versions_empty(self):
        enforcer = SemverEnforcer()
        compatible = enforcer.get_compatible_versions("NonExistent", "1.0.0")
        assert len(compatible) == 0

    def test_deprecate_nonexistent_contract(self):
        enforcer = SemverEnforcer()
        result = enforcer.deprecate_contract("NonExistent", "1.0.0")
        assert result is None

    def test_get_latest_nonexistent(self):
        enforcer = SemverEnforcer()
        result = enforcer.get_latest_contract("NonExistent")
        assert result is None

    def test_get_latest_empty(self):
        enforcer = SemverEnforcer()
        enforcer._contracts["Empty"] = {}
        result = enforcer.get_latest_contract("Empty")
        assert result is None

    def test_contract_with_changelog(self):
        enforcer = SemverEnforcer()
        contract = enforcer.register_contract(
            "TestAPI",
            "1.0.0",
            changelog=["Initial release", "Bug fixes"],
        )
        assert len(contract.changelog) == 2

    def test_versioned_contract_defaults(self):
        contract = VersionedContract(
            name="Test",
            version=SemVer.parse("1.0.0"),
        )
        assert contract.deprecated is False
        assert contract.deprecated_at is None
        assert contract.sunset_at is None
        assert contract.successor_version is None

    def test_prerelease_short_vs_long(self):
        """Test when first prerelease is shorter."""
        v1 = SemVer.parse("1.0.0-a")
        v2 = SemVer.parse("1.0.0-a.b")
        assert v1 < v2

    def test_prerelease_both_numeric(self):
        """Test numeric prerelease comparison."""
        v1 = SemVer.parse("1.0.0-1")
        v2 = SemVer.parse("1.0.0-2")
        assert v1 < v2

    def test_prerelease_mixed_numeric_alpha(self):
        """Test mixed numeric and alpha prerelease."""
        v1 = SemVer.parse("1.0.0-1")
        v2 = SemVer.parse("1.0.0-a")
        assert v1 < v2  # Numeric has lower precedence

    def test_compare_minor_greater(self):
        """Test minor version comparison."""
        enforcer = SemverEnforcer()
        level = enforcer.check_compatibility("1.5.0", "1.3.0")
        assert level == CompatibilityLevel.INCOMPATIBLE

    def test_breaking_changes_range(self):
        enforcer = SemverEnforcer()
        enforcer.record_breaking_change("1.0.0", "Change 1")
        enforcer.record_breaking_change("1.5.0", "Change 2")
        enforcer.record_breaking_change("2.0.0", "Change 3")
        enforcer.record_breaking_change("2.5.0", "Change 4")

        # Both filters
        changes = enforcer.get_breaking_changes(from_version="1.0.0", to_version="2.0.0")
        assert len(changes) == 2  # 1.5.0 and 2.0.0

    def test_try_parse_attribute_error(self):
        """Test try_parse with None."""
        result = SemVer.try_parse(None)
        assert result is None


class TestPrereleaseCoverageTargeted:
    """Targeted tests for prerelease comparison coverage."""

    def test_release_vs_prerelease_returns_one(self):
        """Line 147: Release version > prerelease version."""
        release = SemVer(1, 0, 0)  # No prerelease
        prerelease = SemVer(1, 0, 0, prerelease="alpha")
        assert release > prerelease  # Triggers line 147

    def test_prerelease_numeric_comparison_returns_one(self):
        """Line 178: Numeric prerelease comparison returns 1."""
        v1 = SemVer(1, 0, 0, prerelease="2")  # Numeric prerelease
        v2 = SemVer(1, 0, 0, prerelease="1")  # Lower numeric
        assert v1 > v2  # 2 > 1 triggers line 178

    def test_prerelease_alpha_vs_numeric_returns_one(self):
        """Line 182: Alpha identifier > numeric identifier."""
        v1 = SemVer(1, 0, 0, prerelease="alpha")  # Alpha
        v2 = SemVer(1, 0, 0, prerelease="1")  # Numeric
        assert v1 > v2  # Triggers line 182

    def test_prerelease_alpha_comparison_returns_one(self):
        """Lines 187-189: Alphanumeric comparison returns 1."""
        v1 = SemVer(1, 0, 0, prerelease="beta")
        v2 = SemVer(1, 0, 0, prerelease="alpha")
        assert v1 > v2  # "beta" > "alpha" triggers lines 187-189

    def test_prerelease_multi_part_comparison(self):
        """Test multi-part prerelease comparison."""
        v1 = SemVer(1, 0, 0, prerelease="alpha.2")
        v2 = SemVer(1, 0, 0, prerelease="alpha.1")
        assert v1 > v2

    def test_prerelease_equal_parts(self):
        """Test equal prerelease parts (line 189 return 0)."""
        v1 = SemVer(1, 0, 0, prerelease="alpha.1")
        v2 = SemVer(1, 0, 0, prerelease="alpha.1")
        assert v1 == v2

    def test_prerelease_longer_parts(self):
        """Test prerelease with more parts."""
        v1 = SemVer(1, 0, 0, prerelease="alpha.1.1")
        v2 = SemVer(1, 0, 0, prerelease="alpha.1")
        assert v1 > v2  # More parts means higher precedence
