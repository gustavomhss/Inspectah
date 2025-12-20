"""
Tests for Guardian Thresholds — S41

Tests for ThresholdConfig, DomainThresholds, and threshold helper functions.
"""

import pytest

from app.guardian.thresholds import (
    RiskLevel,
    ThresholdConfig,
    DomainThresholds,
    get_global_thresholds,
    set_global_thresholds,
    get_threshold,
    validate_quorum,
)


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_all_risk_levels_defined(self):
        """All expected risk levels are defined."""
        expected = ["low", "medium", "high"]
        actual = [r.value for r in RiskLevel]
        assert set(actual) == set(expected)

    def test_risk_level_values(self):
        """Risk level values match expected strings."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"

    def test_risk_level_is_string_enum(self):
        """RiskLevel is a string enum."""
        assert isinstance(RiskLevel.LOW, str)
        assert RiskLevel.LOW == "low"


class TestThresholdConfig:
    """Tests for ThresholdConfig dataclass."""

    def test_create_valid_threshold_config(self):
        """Create a valid threshold configuration."""
        config = ThresholdConfig(
            domain="governo",
            risk_level=RiskLevel.HIGH,
            threshold=0.80,
            quorum=0.75,
        )
        assert config.domain == "governo"
        assert config.risk_level == RiskLevel.HIGH
        assert config.threshold == 0.80
        assert config.quorum == 0.75

    def test_threshold_config_minimum_values(self):
        """Threshold config accepts minimum values (0.0)."""
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.LOW,
            threshold=0.0,
            quorum=0.0,
        )
        assert config.threshold == 0.0
        assert config.quorum == 0.0

    def test_threshold_config_maximum_values(self):
        """Threshold config accepts maximum values (1.0)."""
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.HIGH,
            threshold=1.0,
            quorum=1.0,
        )
        assert config.threshold == 1.0
        assert config.quorum == 1.0

    def test_threshold_config_invalid_threshold_too_low(self):
        """Threshold config rejects threshold < 0.0."""
        with pytest.raises(ValueError, match="Threshold must be between"):
            ThresholdConfig(
                domain="test",
                risk_level=RiskLevel.LOW,
                threshold=-0.1,
                quorum=0.5,
            )

    def test_threshold_config_invalid_threshold_too_high(self):
        """Threshold config rejects threshold > 1.0."""
        with pytest.raises(ValueError, match="Threshold must be between"):
            ThresholdConfig(
                domain="test",
                risk_level=RiskLevel.LOW,
                threshold=1.1,
                quorum=0.5,
            )

    def test_threshold_config_invalid_quorum_too_low(self):
        """Threshold config rejects quorum < 0.0."""
        with pytest.raises(ValueError, match="Quorum must be between"):
            ThresholdConfig(
                domain="test",
                risk_level=RiskLevel.LOW,
                threshold=0.5,
                quorum=-0.1,
            )

    def test_threshold_config_invalid_quorum_too_high(self):
        """Threshold config rejects quorum > 1.0."""
        with pytest.raises(ValueError, match="Quorum must be between"):
            ThresholdConfig(
                domain="test",
                risk_level=RiskLevel.LOW,
                threshold=0.5,
                quorum=1.5,
            )


class TestDomainThresholds:
    """Tests for DomainThresholds class."""

    def test_create_domain_thresholds_with_defaults(self):
        """Create DomainThresholds with default values."""
        dt = DomainThresholds()
        assert dt.default_quorum == 0.66
        assert dt.default_threshold == 0.66
        assert dt.high_risk_quorum == 0.80
        assert dt.high_risk_threshold == 0.75
        assert "governo" in dt.domain_overrides
        assert "saude" in dt.domain_overrides
        assert "financeiro" in dt.domain_overrides

    def test_create_domain_thresholds_with_custom_defaults(self):
        """Create DomainThresholds with custom default values."""
        dt = DomainThresholds(
            default_quorum=0.70,
            default_threshold=0.75,
            high_risk_quorum=0.85,
            high_risk_threshold=0.80,
        )
        assert dt.default_quorum == 0.70
        assert dt.default_threshold == 0.75
        assert dt.high_risk_quorum == 0.85
        assert dt.high_risk_threshold == 0.80

    def test_domain_overrides_initialized(self):
        """Domain overrides are initialized with expected values."""
        dt = DomainThresholds()
        assert dt.domain_overrides["governo"]["threshold"] == 0.80
        assert dt.domain_overrides["saude"]["threshold"] == 0.85
        assert dt.domain_overrides["financeiro"]["threshold"] == 0.80

    def test_create_domain_thresholds_with_custom_overrides(self):
        """Create DomainThresholds with custom overrides."""
        custom_overrides = {
            "custom_domain": {"threshold": 0.90, "quorum": 0.85},
        }
        dt = DomainThresholds(domain_overrides=custom_overrides)
        assert "custom_domain" in dt.domain_overrides
        assert dt.domain_overrides["custom_domain"]["threshold"] == 0.90


class TestGetThreshold:
    """Tests for get_threshold method."""

    def test_get_threshold_low_risk_default_domain(self):
        """Get threshold for low risk with default domain."""
        dt = DomainThresholds()
        config = dt.get_threshold("unknown_domain", RiskLevel.LOW)
        assert config.domain == "unknown_domain"
        assert config.risk_level == RiskLevel.LOW
        assert config.threshold == 0.66  # default
        assert config.quorum == 0.66  # default

    def test_get_threshold_medium_risk_default_domain(self):
        """Get threshold for medium risk with default domain."""
        dt = DomainThresholds()
        config = dt.get_threshold("unknown_domain", RiskLevel.MEDIUM)
        assert config.domain == "unknown_domain"
        assert config.risk_level == RiskLevel.MEDIUM
        assert config.threshold == 0.66  # default
        assert config.quorum == 0.66  # default

    def test_get_threshold_high_risk_default_domain(self):
        """Get threshold for high risk with default domain."""
        dt = DomainThresholds()
        config = dt.get_threshold("unknown_domain", RiskLevel.HIGH)
        assert config.domain == "unknown_domain"
        assert config.risk_level == RiskLevel.HIGH
        assert config.threshold == 0.75  # high_risk_threshold
        assert config.quorum == 0.80  # high_risk_quorum

    def test_get_threshold_governo_low_risk(self):
        """Get threshold for governo domain with low risk."""
        dt = DomainThresholds()
        config = dt.get_threshold("governo", RiskLevel.LOW)
        assert config.domain == "governo"
        assert config.risk_level == RiskLevel.LOW
        assert config.threshold == 0.80  # governo override
        assert config.quorum == 0.66  # default (no override)

    def test_get_threshold_governo_high_risk(self):
        """Get threshold for governo domain with high risk."""
        dt = DomainThresholds()
        config = dt.get_threshold("governo", RiskLevel.HIGH)
        assert config.domain == "governo"
        assert config.risk_level == RiskLevel.HIGH
        assert config.threshold == 0.80  # governo override (same as default high)
        assert config.quorum == 0.80  # high_risk_quorum

    def test_get_threshold_saude_low_risk(self):
        """Get threshold for saude domain with low risk."""
        dt = DomainThresholds()
        config = dt.get_threshold("saude", RiskLevel.LOW)
        assert config.domain == "saude"
        assert config.risk_level == RiskLevel.LOW
        assert config.threshold == 0.85  # saude override
        assert config.quorum == 0.66  # default

    def test_get_threshold_saude_high_risk(self):
        """Get threshold for saude domain with high risk."""
        dt = DomainThresholds()
        config = dt.get_threshold("saude", RiskLevel.HIGH)
        assert config.domain == "saude"
        assert config.risk_level == RiskLevel.HIGH
        assert config.threshold == 0.85  # saude override
        assert config.quorum == 0.80  # high_risk_quorum

    def test_get_threshold_financeiro_low_risk(self):
        """Get threshold for financeiro domain with low risk."""
        dt = DomainThresholds()
        config = dt.get_threshold("financeiro", RiskLevel.LOW)
        assert config.domain == "financeiro"
        assert config.risk_level == RiskLevel.LOW
        assert config.threshold == 0.80  # financeiro override
        assert config.quorum == 0.66  # default

    def test_get_threshold_with_quorum_override(self):
        """Get threshold with both threshold and quorum override."""
        dt = DomainThresholds(
            domain_overrides={
                "test_domain": {"threshold": 0.90, "quorum": 0.85},
            }
        )
        config = dt.get_threshold("test_domain", RiskLevel.LOW)
        assert config.threshold == 0.90
        assert config.quorum == 0.85

    def test_get_threshold_with_partial_override(self):
        """Get threshold with only threshold override (quorum uses default)."""
        dt = DomainThresholds(
            domain_overrides={
                "partial_domain": {"threshold": 0.95},
            }
        )
        config = dt.get_threshold("partial_domain", RiskLevel.MEDIUM)
        assert config.threshold == 0.95
        assert config.quorum == 0.66  # default


class TestValidateQuorum:
    """Tests for validate_quorum method."""

    def test_validate_quorum_with_sufficient_votes(self):
        """Validate quorum with sufficient votes."""
        dt = DomainThresholds()
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.LOW,
            threshold=0.66,
            quorum=0.66,
        )
        assert dt.validate_quorum(5, config) is True

    def test_validate_quorum_with_one_vote(self):
        """Validate quorum with one vote."""
        dt = DomainThresholds()
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.LOW,
            threshold=0.66,
            quorum=0.66,
        )
        assert dt.validate_quorum(1, config) is True

    def test_validate_quorum_with_zero_votes(self):
        """Validate quorum with zero votes fails."""
        dt = DomainThresholds()
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.LOW,
            threshold=0.66,
            quorum=0.66,
        )
        assert dt.validate_quorum(0, config) is False

    def test_validate_quorum_with_negative_votes(self):
        """Validate quorum with negative votes fails."""
        dt = DomainThresholds()
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.LOW,
            threshold=0.66,
            quorum=0.66,
        )
        assert dt.validate_quorum(-1, config) is False

    def test_validate_quorum_with_high_vote_count(self):
        """Validate quorum with high vote count."""
        dt = DomainThresholds()
        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.HIGH,
            threshold=0.80,
            quorum=0.80,
        )
        assert dt.validate_quorum(100, config) is True


class TestGlobalThresholds:
    """Tests for global threshold functions."""

    def test_get_global_thresholds_creates_instance(self):
        """get_global_thresholds creates instance on first call."""
        # Reset global state
        set_global_thresholds(None)

        dt = get_global_thresholds()
        assert dt is not None
        assert isinstance(dt, DomainThresholds)
        assert dt.default_quorum == 0.66

    def test_get_global_thresholds_returns_same_instance(self):
        """get_global_thresholds returns same instance on subsequent calls."""
        # Reset global state
        set_global_thresholds(None)

        dt1 = get_global_thresholds()
        dt2 = get_global_thresholds()
        assert dt1 is dt2

    def test_set_global_thresholds(self):
        """set_global_thresholds sets custom instance."""
        custom_dt = DomainThresholds(
            default_quorum=0.70,
            default_threshold=0.75,
        )
        set_global_thresholds(custom_dt)

        dt = get_global_thresholds()
        assert dt is custom_dt
        assert dt.default_quorum == 0.70
        assert dt.default_threshold == 0.75

    def test_get_threshold_convenience_function(self):
        """get_threshold convenience function uses global instance."""
        # Reset to defaults
        set_global_thresholds(DomainThresholds())

        config = get_threshold("governo", RiskLevel.HIGH)
        assert config.domain == "governo"
        assert config.risk_level == RiskLevel.HIGH
        assert config.threshold == 0.80

    def test_validate_quorum_convenience_function(self):
        """validate_quorum convenience function uses global instance."""
        # Reset to defaults
        set_global_thresholds(DomainThresholds())

        config = ThresholdConfig(
            domain="test",
            risk_level=RiskLevel.LOW,
            threshold=0.66,
            quorum=0.66,
        )
        assert validate_quorum(5, config) is True
        assert validate_quorum(0, config) is False


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_domain_name(self):
        """Handle empty domain name gracefully."""
        dt = DomainThresholds()
        config = dt.get_threshold("", RiskLevel.LOW)
        assert config.domain == ""
        assert config.threshold == 0.66  # uses default

    def test_none_like_domain_name(self):
        """Handle None-like domain name gracefully."""
        dt = DomainThresholds()
        config = dt.get_threshold("None", RiskLevel.MEDIUM)
        assert config.domain == "None"
        assert config.threshold == 0.66  # uses default

    def test_case_sensitive_domain_matching(self):
        """Domain matching is case-sensitive."""
        dt = DomainThresholds()
        config_lower = dt.get_threshold("governo", RiskLevel.LOW)
        config_upper = dt.get_threshold("GOVERNO", RiskLevel.LOW)

        assert config_lower.threshold == 0.80  # has override
        assert config_upper.threshold == 0.66  # no override (case-sensitive)

    def test_all_risk_levels_with_all_domains(self):
        """Test all combinations of risk levels and domains."""
        dt = DomainThresholds()
        domains = ["governo", "saude", "financeiro", "unknown"]
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]

        for domain in domains:
            for risk_level in risk_levels:
                config = dt.get_threshold(domain, risk_level)
                assert config.domain == domain
                assert config.risk_level == risk_level
                assert 0.0 <= config.threshold <= 1.0
                assert 0.0 <= config.quorum <= 1.0

    def test_override_with_empty_dict(self):
        """Override with empty dict falls back to base values."""
        dt = DomainThresholds(
            domain_overrides={
                "empty_override": {},
            }
        )
        config = dt.get_threshold("empty_override", RiskLevel.LOW)
        assert config.threshold == 0.66  # default
        assert config.quorum == 0.66  # default

    def test_custom_defaults_affect_all_domains(self):
        """Custom defaults affect all non-overridden domains."""
        dt = DomainThresholds(
            default_quorum=0.75,
            default_threshold=0.80,
            domain_overrides={},  # No overrides
        )
        config = dt.get_threshold("any_domain", RiskLevel.LOW)
        assert config.threshold == 0.80
        assert config.quorum == 0.75

    def test_high_risk_defaults_affect_high_risk_only(self):
        """High risk defaults only affect HIGH risk level."""
        dt = DomainThresholds(
            default_quorum=0.50,
            default_threshold=0.50,
            high_risk_quorum=0.90,
            high_risk_threshold=0.95,
            domain_overrides={},
        )

        low_config = dt.get_threshold("test", RiskLevel.LOW)
        assert low_config.threshold == 0.50
        assert low_config.quorum == 0.50

        high_config = dt.get_threshold("test", RiskLevel.HIGH)
        assert high_config.threshold == 0.95
        assert high_config.quorum == 0.90
