"""
S39-BE-024: Semantic Versioning Enforcement

Implements semver parsing, comparison, and contract versioning policies.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class VersionChangeType(str, Enum):
    """Type of version change."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


class CompatibilityLevel(str, Enum):
    """Compatibility level between versions."""
    COMPATIBLE = "compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True)
class SemVer:
    """
    Semantic version representation.

    Format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
    """
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    # Regex pattern for parsing
    PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)"
        r"\.(?P<minor>0|[1-9]\d*)"
        r"\.(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    @classmethod
    def parse(cls, version_string: str) -> "SemVer":
        """
        Parse a version string into SemVer.

        Args:
            version_string: Version string to parse

        Returns:
            SemVer instance

        Raises:
            ValueError if the string is not valid semver
        """
        match = cls.PATTERN.match(version_string.strip())
        if not match:
            raise ValueError(f"Invalid semver format: {version_string}")

        groups = match.groupdict()
        return cls(
            major=int(groups["major"]),
            minor=int(groups["minor"]),
            patch=int(groups["patch"]),
            prerelease=groups.get("prerelease"),
            build=groups.get("build"),
        )

    @classmethod
    def try_parse(cls, version_string: str) -> Optional["SemVer"]:
        """
        Try to parse a version string, returning None on failure.

        Args:
            version_string: Version string to parse

        Returns:
            SemVer instance or None
        """
        try:
            return cls.parse(version_string)
        except (ValueError, AttributeError):
            return None

    def __str__(self) -> str:
        """Convert to string representation."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def __lt__(self, other: "SemVer") -> bool:
        """Less than comparison."""
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._compare(other) < 0

    def __le__(self, other: "SemVer") -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._compare(other) <= 0

    def __gt__(self, other: "SemVer") -> bool:
        """Greater than comparison."""
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._compare(other) > 0

    def __ge__(self, other: "SemVer") -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._compare(other) >= 0

    def _compare(self, other: "SemVer") -> int:
        """
        Compare two versions.

        Returns:
            -1 if self < other, 0 if equal, 1 if self > other
        """
        # Compare major.minor.patch
        for a, b in [(self.major, other.major), (self.minor, other.minor), (self.patch, other.patch)]:
            if a < b:
                return -1
            if a > b:
                return 1

        # Prerelease versions have lower precedence
        if self.prerelease and not other.prerelease:
            return -1
        if not self.prerelease and other.prerelease:
            return 1
        if self.prerelease and other.prerelease:
            return self._compare_prerelease(self.prerelease, other.prerelease)

        return 0

    @staticmethod
    def _compare_prerelease(a: str, b: str) -> int:
        """Compare prerelease identifiers."""
        a_parts = a.split(".")
        b_parts = b.split(".")

        for i in range(max(len(a_parts), len(b_parts))):
            if i >= len(a_parts):
                return -1
            if i >= len(b_parts):
                return 1

            a_part = a_parts[i]
            b_part = b_parts[i]

            # Numeric identifiers have lower precedence than alphanumeric
            a_is_num = a_part.isdigit()
            b_is_num = b_part.isdigit()

            if a_is_num and b_is_num:
                a_num = int(a_part)
                b_num = int(b_part)
                if a_num < b_num:
                    return -1
                if a_num > b_num:
                    return 1
            elif a_is_num:
                return -1
            elif b_is_num:
                return 1
            else:
                if a_part < b_part:
                    return -1
                if a_part > b_part:
                    return 1

        return 0

    def bump_major(self) -> "SemVer":
        """Return a new version with bumped major."""
        return SemVer(self.major + 1, 0, 0)

    def bump_minor(self) -> "SemVer":
        """Return a new version with bumped minor."""
        return SemVer(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "SemVer":
        """Return a new version with bumped patch."""
        return SemVer(self.major, self.minor, self.patch + 1)

    def with_prerelease(self, prerelease: str) -> "SemVer":
        """Return a new version with prerelease tag."""
        return SemVer(self.major, self.minor, self.patch, prerelease, self.build)

    def with_build(self, build: str) -> "SemVer":
        """Return a new version with build metadata."""
        return SemVer(self.major, self.minor, self.patch, self.prerelease, build)

    def is_stable(self) -> bool:
        """Check if this is a stable release (no prerelease)."""
        return self.prerelease is None

    def is_compatible_with(self, other: "SemVer") -> bool:
        """Check if this version is API-compatible with another."""
        return self.major == other.major

    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to tuple (major, minor, patch)."""
        return (self.major, self.minor, self.patch)


@dataclass
class VersionRange:
    """
    Represents a range of acceptable versions.

    Supports common range operators:
    - ^1.2.3: Compatible with 1.2.3 (>=1.2.3 <2.0.0)
    - ~1.2.3: Approximately 1.2.3 (>=1.2.3 <1.3.0)
    - >=1.2.3: Greater than or equal
    - >1.2.3: Greater than
    - <=1.2.3: Less than or equal
    - <1.2.3: Less than
    - =1.2.3: Exactly 1.2.3
    - 1.2.3 - 2.0.0: Range
    """
    min_version: Optional[SemVer] = None
    max_version: Optional[SemVer] = None
    min_inclusive: bool = True
    max_inclusive: bool = False

    @classmethod
    def parse(cls, range_string: str) -> "VersionRange":
        """
        Parse a version range string.

        Args:
            range_string: Range string to parse

        Returns:
            VersionRange instance
        """
        range_string = range_string.strip()

        # Caret range: ^1.2.3
        if range_string.startswith("^"):
            version = SemVer.parse(range_string[1:])
            if version.major == 0:
                # For 0.x.y, only patch changes are compatible
                max_ver = SemVer(version.major, version.minor + 1, 0)
            else:
                max_ver = SemVer(version.major + 1, 0, 0)
            return cls(
                min_version=version,
                max_version=max_ver,
                min_inclusive=True,
                max_inclusive=False,
            )

        # Tilde range: ~1.2.3
        if range_string.startswith("~"):
            version = SemVer.parse(range_string[1:])
            max_ver = SemVer(version.major, version.minor + 1, 0)
            return cls(
                min_version=version,
                max_version=max_ver,
                min_inclusive=True,
                max_inclusive=False,
            )

        # Hyphen range: 1.2.3 - 2.0.0
        if " - " in range_string:
            parts = range_string.split(" - ")
            if len(parts) == 2:
                return cls(
                    min_version=SemVer.parse(parts[0]),
                    max_version=SemVer.parse(parts[1]),
                    min_inclusive=True,
                    max_inclusive=True,
                )

        # Comparison operators
        if range_string.startswith(">="):
            return cls(min_version=SemVer.parse(range_string[2:]), min_inclusive=True)
        if range_string.startswith("<="):
            return cls(max_version=SemVer.parse(range_string[2:]), max_inclusive=True)
        if range_string.startswith(">"):
            return cls(min_version=SemVer.parse(range_string[1:]), min_inclusive=False)
        if range_string.startswith("<"):
            return cls(max_version=SemVer.parse(range_string[1:]), max_inclusive=False)
        if range_string.startswith("="):
            version = SemVer.parse(range_string[1:])
            return cls(
                min_version=version,
                max_version=version,
                min_inclusive=True,
                max_inclusive=True,
            )

        # Exact version
        version = SemVer.parse(range_string)
        return cls(
            min_version=version,
            max_version=version,
            min_inclusive=True,
            max_inclusive=True,
        )

    def contains(self, version: SemVer) -> bool:
        """Check if a version is within this range."""
        if self.min_version:
            if self.min_inclusive:
                if version < self.min_version:
                    return False
            else:
                if version <= self.min_version:
                    return False

        if self.max_version:
            if self.max_inclusive:
                if version > self.max_version:
                    return False
            else:
                if version >= self.max_version:
                    return False

        return True

    def __str__(self) -> str:
        """String representation."""
        if self.min_version == self.max_version and self.min_version:
            return f"={self.min_version}"

        parts = []
        if self.min_version:
            op = ">=" if self.min_inclusive else ">"
            parts.append(f"{op}{self.min_version}")
        if self.max_version:
            op = "<=" if self.max_inclusive else "<"
            parts.append(f"{op}{self.max_version}")

        return " ".join(parts) if parts else "*"


@dataclass
class VersionedContract:
    """A contract with version information."""
    name: str
    version: SemVer
    deprecated: bool = False
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    successor_version: Optional[SemVer] = None
    changelog: List[str] = field(default_factory=list)

    def is_active(self) -> bool:
        """Check if this contract version is still active."""
        if self.sunset_at:
            return datetime.now(timezone.utc).replace(tzinfo=None) < self.sunset_at
        return True


class SemverEnforcer:
    """
    Enforces semantic versioning policies for API contracts.
    """

    def __init__(
        self,
        current_version: str = "2.0.0",
        min_supported_version: str = "2.0.0",
        deprecation_period_days: int = 90,
    ):
        self.current_version = SemVer.parse(current_version)
        self.min_supported = SemVer.parse(min_supported_version)
        self.deprecation_period_days = deprecation_period_days
        self._contracts: Dict[str, Dict[str, VersionedContract]] = {}
        self._breaking_changes: List[Dict[str, Any]] = []

    def register_contract(
        self,
        name: str,
        version: str,
        changelog: Optional[List[str]] = None,
    ) -> VersionedContract:
        """Register a contract version."""
        semver = SemVer.parse(version)
        contract = VersionedContract(
            name=name,
            version=semver,
            changelog=changelog or [],
        )

        if name not in self._contracts:
            self._contracts[name] = {}
        self._contracts[name][version] = contract

        return contract

    def deprecate_contract(
        self,
        name: str,
        version: str,
        successor_version: Optional[str] = None,
        sunset_days: Optional[int] = None,
    ) -> Optional[VersionedContract]:
        """Mark a contract version as deprecated."""
        if name not in self._contracts or version not in self._contracts[name]:
            return None

        contract = self._contracts[name][version]
        contract.deprecated = True
        contract.deprecated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        if successor_version:
            contract.successor_version = SemVer.parse(successor_version)

        days = sunset_days or self.deprecation_period_days
        contract.sunset_at = contract.deprecated_at + timedelta(days=days)

        return contract

    def get_contract(self, name: str, version: str) -> Optional[VersionedContract]:
        """Get a specific contract version."""
        return self._contracts.get(name, {}).get(version)

    def get_latest_contract(self, name: str) -> Optional[VersionedContract]:
        """Get the latest version of a contract."""
        if name not in self._contracts:
            return None

        versions = list(self._contracts[name].values())
        if not versions:
            return None

        return max(versions, key=lambda c: c.version)

    def get_compatible_versions(self, name: str, version: str) -> List[VersionedContract]:
        """Get all compatible versions of a contract."""
        if name not in self._contracts:
            return []

        target = SemVer.parse(version)
        return [
            c for c in self._contracts[name].values()
            if c.version.is_compatible_with(target) and c.is_active()
        ]

    def check_compatibility(
        self,
        from_version: str,
        to_version: str,
    ) -> CompatibilityLevel:
        """
        Check compatibility between two versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            CompatibilityLevel
        """
        from_ver = SemVer.parse(from_version)
        to_ver = SemVer.parse(to_version)

        # Same version is compatible
        if from_ver == to_ver:
            return CompatibilityLevel.COMPATIBLE

        # Different major versions are incompatible
        if from_ver.major != to_ver.major:
            return CompatibilityLevel.INCOMPATIBLE

        # Minor version increases are backward compatible
        if to_ver.minor > from_ver.minor:
            return CompatibilityLevel.BACKWARD_COMPATIBLE

        # Patch increases are compatible
        if to_ver.minor == from_ver.minor and to_ver.patch >= from_ver.patch:
            return CompatibilityLevel.COMPATIBLE

        # Going backward is not compatible
        return CompatibilityLevel.INCOMPATIBLE

    def detect_change_type(
        self,
        from_version: str,
        to_version: str,
    ) -> VersionChangeType:
        """
        Detect the type of change between versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            VersionChangeType
        """
        from_ver = SemVer.parse(from_version)
        to_ver = SemVer.parse(to_version)

        if from_ver == to_ver:
            return VersionChangeType.NONE

        if from_ver.major != to_ver.major:
            return VersionChangeType.MAJOR

        if from_ver.minor != to_ver.minor:
            return VersionChangeType.MINOR

        return VersionChangeType.PATCH

    def record_breaking_change(
        self,
        version: str,
        description: str,
        affected_endpoints: Optional[List[str]] = None,
        migration_guide: Optional[str] = None,
    ) -> None:
        """Record a breaking change."""
        self._breaking_changes.append({
            "version": version,
            "description": description,
            "affected_endpoints": affected_endpoints or [],
            "migration_guide": migration_guide,
            "recorded_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        })

    def get_breaking_changes(
        self,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get breaking changes, optionally filtered by version range."""
        changes = self._breaking_changes

        if from_version:
            from_ver = SemVer.parse(from_version)
            changes = [
                c for c in changes
                if SemVer.parse(c["version"]) > from_ver
            ]

        if to_version:
            to_ver = SemVer.parse(to_version)
            changes = [
                c for c in changes
                if SemVer.parse(c["version"]) <= to_ver
            ]

        return changes

    def suggest_next_version(
        self,
        change_type: VersionChangeType,
        current: Optional[str] = None,
    ) -> SemVer:
        """
        Suggest the next version based on change type.

        Args:
            change_type: Type of change
            current: Current version (uses self.current_version if None)

        Returns:
            Suggested next version
        """
        base = SemVer.parse(current) if current else self.current_version

        if change_type == VersionChangeType.MAJOR:
            return base.bump_major()
        if change_type == VersionChangeType.MINOR:
            return base.bump_minor()
        if change_type == VersionChangeType.PATCH:
            return base.bump_patch()

        return base

    def is_version_supported(self, version: str) -> bool:
        """Check if a version is supported."""
        ver = SemVer.parse(version)
        return ver >= self.min_supported and ver.major == self.current_version.major

    def get_deprecation_warning(self, version: str) -> Optional[str]:
        """Get deprecation warning if applicable."""
        ver = SemVer.parse(version)

        if ver < self.min_supported:
            return f"Version {version} is no longer supported. Please upgrade to {self.current_version}"

        if ver < self.current_version:
            return f"Version {version} is deprecated. Please upgrade to {self.current_version}"

        return None

    def get_version_info(self) -> Dict[str, Any]:
        """Get version information summary."""
        return {
            "current": str(self.current_version),
            "min_supported": str(self.min_supported),
            "is_stable": self.current_version.is_stable(),
            "contracts": {
                name: {
                    "versions": [str(c.version) for c in contracts.values()],
                    "latest": str(max(contracts.values(), key=lambda c: c.version).version)
                    if contracts else None,
                }
                for name, contracts in self._contracts.items()
            },
            "breaking_changes_count": len(self._breaking_changes),
        }


# Global enforcer instance
_default_enforcer = SemverEnforcer()


def get_enforcer() -> SemverEnforcer:
    """Get the default semver enforcer instance."""
    return _default_enforcer


def parse_version(version_string: str) -> SemVer:
    """Parse a version string."""
    return SemVer.parse(version_string)


def is_compatible(from_version: str, to_version: str) -> bool:
    """Check if two versions are compatible."""
    return _default_enforcer.check_compatibility(from_version, to_version) != CompatibilityLevel.INCOMPATIBLE
