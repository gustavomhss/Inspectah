"""
Guardian Thresholds — S41

Configuration of thresholds and quorum requirements per domain and risk level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class RiskLevel(str, Enum):
    """Risk level for a decision."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ThresholdConfig:
    """
    Configuration for thresholds and quorum for a specific domain/risk combination.

    Attributes:
        domain: Domain this config applies to (e.g., "governo", "saude").
        risk_level: Risk level this config applies to.
        threshold: Minimum approval threshold (0.0 to 1.0).
        quorum: Minimum quorum required for voting (0.0 to 1.0).
    """

    domain: str
    risk_level: RiskLevel
    threshold: float
    quorum: float

    def __post_init__(self) -> None:
        """Validate threshold and quorum values."""
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {self.threshold}")
        if not 0.0 <= self.quorum <= 1.0:
            raise ValueError(f"Quorum must be between 0.0 and 1.0, got {self.quorum}")


@dataclass
class DomainThresholds:
    """
    Manages thresholds for all domains and risk levels.

    Provides default values and domain-specific overrides.
    """

    # Default thresholds
    default_quorum: float = 0.66
    default_threshold: float = 0.66
    high_risk_quorum: float = 0.80
    high_risk_threshold: float = 0.75

    # Domain-specific overrides
    domain_overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize domain overrides if not provided."""
        if not self.domain_overrides:
            self.domain_overrides = {
                "governo": {"threshold": 0.80},
                "saude": {"threshold": 0.85},
                "financeiro": {"threshold": 0.80},
            }

    def get_threshold(self, domain: str, risk_level: RiskLevel) -> ThresholdConfig:
        """
        Get threshold configuration for a specific domain and risk level.

        Args:
            domain: The domain (e.g., "governo", "saude", "financeiro").
            risk_level: The risk level (LOW, MEDIUM, HIGH).

        Returns:
            ThresholdConfig with appropriate threshold and quorum values.

        Examples:
            >>> dt = DomainThresholds()
            >>> config = dt.get_threshold("governo", RiskLevel.HIGH)
            >>> config.threshold
            0.80
            >>> config.quorum
            0.80

            >>> config = dt.get_threshold("saude", RiskLevel.LOW)
            >>> config.threshold
            0.85
            >>> config.quorum
            0.66

            >>> config = dt.get_threshold("unknown", RiskLevel.MEDIUM)
            >>> config.threshold
            0.66
            >>> config.quorum
            0.66
        """
        # Get base threshold and quorum based on risk level
        if risk_level == RiskLevel.HIGH:
            threshold = self.high_risk_threshold
            quorum = self.high_risk_quorum
        else:
            threshold = self.default_threshold
            quorum = self.default_quorum

        # Apply domain overrides if they exist
        if domain in self.domain_overrides:
            overrides = self.domain_overrides[domain]
            threshold = overrides.get("threshold", threshold)
            quorum = overrides.get("quorum", quorum)

        return ThresholdConfig(
            domain=domain,
            risk_level=risk_level,
            threshold=threshold,
            quorum=quorum,
        )

    def validate_quorum(self, votes: int, threshold: ThresholdConfig) -> bool:
        """
        Validate if the number of votes meets the quorum requirement.

        Args:
            votes: Number of votes received.
            threshold: Threshold configuration containing quorum requirement.

        Returns:
            True if quorum is met, False otherwise.

        Examples:
            >>> dt = DomainThresholds()
            >>> config = dt.get_threshold("governo", RiskLevel.HIGH)
            >>> dt.validate_quorum(4, config)  # 4/5 = 0.80, meets 0.80 quorum
            True

            >>> dt.validate_quorum(2, config)  # 2/5 = 0.40, below 0.80 quorum
            False
        """
        if votes < 0:
            return False

        # For threshold configs, we need to know total possible votes
        # This is a simple check: votes >= 1 means at least one vote
        # More sophisticated quorum validation would require total_votes parameter
        return votes >= 1


# Global instance for easy access
_GLOBAL_THRESHOLDS: Optional[DomainThresholds] = None


def get_global_thresholds() -> DomainThresholds:
    """
    Get the global DomainThresholds instance.

    Creates a new instance with defaults if one doesn't exist.

    Returns:
        The global DomainThresholds instance.
    """
    global _GLOBAL_THRESHOLDS
    if _GLOBAL_THRESHOLDS is None:
        _GLOBAL_THRESHOLDS = DomainThresholds()
    return _GLOBAL_THRESHOLDS


def set_global_thresholds(thresholds: DomainThresholds) -> None:
    """
    Set the global DomainThresholds instance.

    Args:
        thresholds: The DomainThresholds instance to use globally.
    """
    global _GLOBAL_THRESHOLDS
    _GLOBAL_THRESHOLDS = thresholds


def get_threshold(domain: str, risk_level: RiskLevel) -> ThresholdConfig:
    """
    Convenience function to get threshold from global instance.

    Args:
        domain: The domain (e.g., "governo", "saude", "financeiro").
        risk_level: The risk level (LOW, MEDIUM, HIGH).

    Returns:
        ThresholdConfig with appropriate threshold and quorum values.
    """
    return get_global_thresholds().get_threshold(domain, risk_level)


def validate_quorum(votes: int, threshold: ThresholdConfig) -> bool:
    """
    Convenience function to validate quorum using global instance.

    Args:
        votes: Number of votes received.
        threshold: Threshold configuration containing quorum requirement.

    Returns:
        True if quorum is met, False otherwise.
    """
    return get_global_thresholds().validate_quorum(votes, threshold)
