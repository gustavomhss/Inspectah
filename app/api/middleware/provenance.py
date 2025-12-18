"""
S40-BE-025: Provenance Middleware.

Validates that P4 endpoints return responses with valid provenance.
Responses without provenance are marked as invalid.

Thread-safe implementation with defensive programming.
"""

from __future__ import annotations

import copy
import json
import logging
import re
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
except ImportError:
    Request = None  # type: ignore
    Response = None  # type: ignore
    BaseHTTPMiddleware = object  # type: ignore

logger = logging.getLogger(__name__)

# Thread lock for stats
_provenance_stats_lock = threading.Lock()

# Endpoints that require provenance validation
PROVENANCE_REQUIRED_PATHS: FrozenSet[str] = frozenset({
    "/api/truth/",  # All truth endpoints
})

# Specific patterns that require provenance
PROVENANCE_PATTERNS: Tuple[str, ...] = (
    "/twin",
    "/inspect",
    "/timeline",
)

# Required fields in provenance
PROVENANCE_REQUIRED_FIELDS: FrozenSet[str] = frozenset({
    "source",
    "timestamp",
})

# ISO 8601 timestamp pattern for validation
_ISO8601_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
)


def _is_valid_timestamp(timestamp: Any) -> bool:
    """
    Validate timestamp format.

    Args:
        timestamp: Timestamp value to validate

    Returns:
        True if timestamp is valid ISO 8601 format
    """
    if not timestamp:
        return False
    if not isinstance(timestamp, str):
        return False
    return bool(_ISO8601_PATTERN.match(timestamp))


def check_provenance(data: Any) -> bool:
    """
    Check if response data has valid provenance.

    Args:
        data: Response data (should be dict)

    Returns:
        True if provenance is valid, False otherwise
    """
    if data is None:
        return False

    if not isinstance(data, dict):
        return False

    # Check for provenance field
    provenance = data.get("provenance")
    if provenance is None:
        return False

    # Check provenance has required fields
    if not isinstance(provenance, dict):
        return False

    # Validate source (allow string or number for backwards compat)
    source = provenance.get("source")
    if not source:
        return False
    # Accept strings or numbers that are truthy
    if not isinstance(source, (str, int, float)):
        return False

    # Validate timestamp
    timestamp = provenance.get("timestamp")
    if not _is_valid_timestamp(timestamp):
        # Allow non-ISO timestamps if they're non-empty strings (backwards compat)
        if not timestamp or not isinstance(timestamp, str):
            return False

    return True


def check_provenance_detailed(data: Any) -> Tuple[bool, List[str]]:
    """
    Check provenance with detailed validation messages.

    Args:
        data: Response data (should be dict)

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues: List[str] = []

    if data is None:
        issues.append("Data is None")
        return False, issues

    if not isinstance(data, dict):
        issues.append(f"Data is not a dict (got {type(data).__name__})")
        return False, issues

    provenance = data.get("provenance")
    if provenance is None:
        issues.append("Missing 'provenance' field")
        return False, issues

    if not isinstance(provenance, dict):
        issues.append(f"'provenance' is not a dict (got {type(provenance).__name__})")
        return False, issues

    # Check each required field
    for field in PROVENANCE_REQUIRED_FIELDS:
        value = provenance.get(field)
        if not value:
            issues.append(f"Missing or empty required field: {field}")
        elif field == "source":
            # Source can be string or number
            if not isinstance(value, (str, int, float)):
                issues.append(f"Field '{field}' is not a string or number (got {type(value).__name__})")
        elif not isinstance(value, str):
            issues.append(f"Field '{field}' is not a string (got {type(value).__name__})")

    # Validate timestamp format
    timestamp = provenance.get("timestamp")
    if timestamp and isinstance(timestamp, str):
        if not _is_valid_timestamp(timestamp):
            issues.append(f"Timestamp format is not ISO 8601: {timestamp[:50]}")

    return len(issues) == 0, issues


def mark_invalid_provenance(
    data: Dict[str, Any],
    *,
    issues: Optional[List[str]] = None,
    copy_data: bool = False,
) -> Dict[str, Any]:
    """
    Mark response as having invalid provenance.

    Args:
        data: Response data dict
        issues: Optional list of validation issues
        copy_data: If True, create a copy instead of modifying in place

    Returns:
        Updated data with _provenance_valid field
    """
    if data is None:
        data = {}

    result = copy.copy(data) if copy_data else data
    result["_provenance_valid"] = False
    result["_provenance_warning"] = "Response lacks valid provenance"

    if issues:
        result["_provenance_issues"] = list(issues)  # Defensive copy

    return result


def validate_provenance_response(
    data: Any,
    *,
    detailed: bool = False,
) -> Dict[str, Any]:
    """
    Validate and annotate response with provenance status.

    Args:
        data: Response data (should be dict)
        detailed: If True, include detailed validation issues

    Returns:
        Updated data with provenance validation status
    """
    # Handle None/non-dict input
    if data is None:
        return mark_invalid_provenance({}, issues=["Data is None"])

    if not isinstance(data, dict):
        return mark_invalid_provenance(
            {"_original_type": type(data).__name__},
            issues=[f"Data is not a dict (got {type(data).__name__})"],
        )

    if detailed:
        is_valid, issues = check_provenance_detailed(data)
        if is_valid:
            data["_provenance_valid"] = True
        else:
            data = mark_invalid_provenance(data, issues=issues)
    else:
        if check_provenance(data):
            data["_provenance_valid"] = True
        else:
            data = mark_invalid_provenance(data)

    return data


class ProvenanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate provenance on P4 responses (S40-BE-025).

    Responses from truth/inspection endpoints without valid provenance
    are marked with _provenance_valid=False.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate provenance on response."""
        start_time = time.time()
        path = request.url.path

        # Check if this path requires provenance validation
        requires_provenance = self._requires_provenance(path)

        # Call the endpoint
        response = await call_next(request)

        # Only validate JSON responses for provenance-required paths
        if requires_provenance and response.status_code == 200:
            # Try to validate provenance in response
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    response = await self._validate_response(response)
                except Exception as e:
                    logger.warning(f"[provenance] Failed to validate response: {e}")

        # Record latency
        latency_ms = int((time.time() - start_time) * 1000)
        response.headers["X-Provenance-Check-Latency-Ms"] = str(latency_ms)

        return response

    def _requires_provenance(self, path: str) -> bool:
        """Check if path requires provenance validation."""
        # Check base paths
        for base in PROVENANCE_REQUIRED_PATHS:
            if path.startswith(base):
                # Check specific patterns
                for pattern in PROVENANCE_PATTERNS:
                    if pattern in path:
                        return True
        return False

    async def _validate_response(self, response: Response) -> Response:
        """Validate response and add provenance status."""
        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            data = json.loads(body)
            if isinstance(data, dict):
                data = validate_provenance_response(data)
                body = json.dumps(data).encode()
        except json.JSONDecodeError:
            pass

        # Create new response with validated body
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


# Convenience function for direct validation
def validate_provenance_dict(data: Dict[str, Any], path: str) -> Dict[str, Any]:
    """
    Validate provenance for a dict response.

    Use this in endpoint code if middleware is not enabled.

    Args:
        data: Response data dict
        path: Request path

    Returns:
        Validated data with provenance status
    """
    # Check if path requires provenance
    for base in PROVENANCE_REQUIRED_PATHS:
        if path.startswith(base):
            for pattern in PROVENANCE_PATTERNS:
                if pattern in path:
                    return validate_provenance_response(data)
    return data


# Metrics tracking (thread-safe)
_provenance_checks: int = 0
_provenance_valid: int = 0
_provenance_invalid: int = 0


def record_provenance_check(valid: bool) -> None:
    """Record a provenance check result. Thread-safe."""
    global _provenance_checks, _provenance_valid, _provenance_invalid
    with _provenance_stats_lock:
        _provenance_checks += 1
        if valid:
            _provenance_valid += 1
        else:
            _provenance_invalid += 1


def get_provenance_stats() -> Dict[str, Any]:
    """Get provenance validation statistics. Thread-safe."""
    with _provenance_stats_lock:
        total = _provenance_checks
        valid = _provenance_valid
        invalid = _provenance_invalid

    # Calculate derived metrics outside the lock
    rate = (valid / total * 100) if total > 0 else 0.0

    return {
        "total_checks": total,
        "valid": valid,
        "invalid": invalid,
        "valid_rate_percent": round(rate, 2),
    }


def reset_provenance_stats() -> None:
    """Reset provenance statistics (for testing). Thread-safe."""
    global _provenance_checks, _provenance_valid, _provenance_invalid
    with _provenance_stats_lock:
        _provenance_checks = 0
        _provenance_valid = 0
        _provenance_invalid = 0


def create_provenance(
    source: str,
    *,
    timestamp: Optional[str] = None,
    policy_version: Optional[str] = None,
    policy_name: Optional[str] = None,
    actor: Optional[str] = None,
    evidence_refs: Optional[List[str]] = None,
    references: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a valid provenance dict.

    Helper function for creating properly structured provenance.

    Args:
        source: Source identifier (required)
        timestamp: ISO 8601 timestamp (defaults to current time)
        policy_version: Optional policy version
        policy_name: Optional policy name
        actor: Optional actor identifier
        evidence_refs: Optional list of evidence references
        references: Optional additional references

    Returns:
        Dict with valid provenance structure
    """
    if not source:
        raise ValueError("source is required for provenance")

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    provenance: Dict[str, Any] = {
        "source": source,
        "timestamp": timestamp,
    }

    if policy_version:
        provenance["policy_version"] = policy_version
    if policy_name:
        provenance["policy_name"] = policy_name
    if actor:
        provenance["actor"] = actor
    if evidence_refs:
        provenance["evidence_refs"] = list(evidence_refs)  # Defensive copy
    if references:
        provenance["references"] = copy.copy(references)  # Defensive copy

    return provenance
