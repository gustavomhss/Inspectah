"""
S39-BE-023: Contract Validation Middleware

FastAPI middleware for request/response contract validation.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from app.contracts.validator import (
    StrictContractValidator,
    ValidationResult,
    ValidationSeverity,
)
from app.contracts.v1 import (
    CONTRACT_VERSION,
    ContractStatus,
    ErrorContract,
    ResponseEnvelope,
    error_response,
)


class ContractValidationError(Exception):
    """Raised when contract validation fails."""

    def __init__(self, result: ValidationResult):
        self.result = result
        self.errors = result.to_error_contracts()
        super().__init__(f"Contract validation failed: {len(result.issues)} issues")


class ContractMiddleware:
    """
    Middleware for validating API contracts.

    Can be used as FastAPI middleware or as decorators.
    """

    def __init__(
        self,
        validator: Optional[StrictContractValidator] = None,
        strict_mode: bool = True,
        collect_metrics: bool = True,
    ):
        self.validator = validator or StrictContractValidator(strict_mode=strict_mode)
        self.strict_mode = strict_mode
        self.collect_metrics = collect_metrics
        self._validation_count = 0
        self._validation_failures = 0
        self._validation_time_ms = 0.0

    def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        return {
            "total_validations": self._validation_count,
            "failures": self._validation_failures,
            "failure_rate": (
                self._validation_failures / self._validation_count
                if self._validation_count > 0
                else 0.0
            ),
            "avg_validation_time_ms": (
                self._validation_time_ms / self._validation_count
                if self._validation_count > 0
                else 0.0
            ),
        }

    def reset_metrics(self) -> None:
        """Reset validation metrics."""
        self._validation_count = 0
        self._validation_failures = 0
        self._validation_time_ms = 0.0

    def validate_request(
        self,
        data: Dict[str, Any],
        schema_name: str,
        partial: bool = False,
    ) -> ValidationResult:
        """
        Validate request data against a schema.

        Args:
            data: Request data
            schema_name: Schema to validate against
            partial: Allow partial data (for PATCH requests)

        Returns:
            ValidationResult

        Raises:
            ContractValidationError if validation fails in strict mode
        """
        start = time.monotonic()
        result = self.validator.validate(data, schema_name, partial=partial)

        if self.collect_metrics:
            self._validation_count += 1
            self._validation_time_ms += (time.monotonic() - start) * 1000
            if not result.valid:
                self._validation_failures += 1

        if not result.valid and self.strict_mode:
            raise ContractValidationError(result)

        return result

    def validate_response(
        self,
        data: Dict[str, Any],
        schema_name: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate response data.

        Args:
            data: Response data
            schema_name: Optional schema for the data payload

        Returns:
            ValidationResult
        """
        start = time.monotonic()

        # Validate envelope structure
        result = self.validator.validate_response_envelope(data)

        # Validate data payload if schema provided
        if result.valid and schema_name and "data" in data:
            payload = data["data"]
            if isinstance(payload, list):
                for i, item in enumerate(payload):
                    item_result = self.validator.validate(item, schema_name)
                    if not item_result.valid:
                        for issue in item_result.issues:
                            issue.field = f"data[{i}].{issue.field}"
                        result.merge(item_result)
            elif isinstance(payload, dict):
                data_result = self.validator.validate(payload, schema_name)
                if not data_result.valid:
                    for issue in data_result.issues:
                        issue.field = f"data.{issue.field}"
                    result.merge(data_result)

        if self.collect_metrics:
            self._validation_count += 1
            self._validation_time_ms += (time.monotonic() - start) * 1000
            if not result.valid:
                self._validation_failures += 1

        return result

    def wrap_response(
        self,
        data: Any,
        request_id: Optional[str] = None,
        deprecation_warning: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Wrap data in a standard response envelope.

        Args:
            data: Response data
            request_id: Optional request ID
            deprecation_warning: Optional deprecation message

        Returns:
            Response envelope dict
        """
        meta = {
            "version": CONTRACT_VERSION,
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "request_id": request_id or str(uuid.uuid4()),
        }

        if deprecation_warning:
            meta["deprecation_warning"] = deprecation_warning

        envelope = ResponseEnvelope(
            status=ContractStatus.SUCCESS,
            data=data,
            meta=meta,
        )

        return envelope.to_dict()

    def wrap_error(
        self,
        errors: List[ErrorContract],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Wrap errors in a standard response envelope.

        Args:
            errors: List of errors
            request_id: Optional request ID

        Returns:
            Error response envelope dict
        """
        meta = {
            "request_id": request_id or str(uuid.uuid4()),
        }
        return error_response(errors, meta=meta)


def validate_request_contract(
    schema_name: str,
    partial: bool = False,
    middleware: Optional[ContractMiddleware] = None,
):
    """
    Decorator to validate request body against a contract.

    Usage:
        @validate_request_contract("ClaimCreate")
        async def create_claim(data: dict):
            ...
    """
    _middleware = middleware or ContractMiddleware()

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Find the data parameter
            data = kwargs.get("data") or kwargs.get("body")
            if data is None and args:
                data = args[0] if isinstance(args[0], dict) else None

            if data:
                _middleware.validate_request(data, schema_name, partial=partial)

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            data = kwargs.get("data") or kwargs.get("body")
            if data is None and args:
                data = args[0] if isinstance(args[0], dict) else None

            if data:
                _middleware.validate_request(data, schema_name, partial=partial)

            return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def validate_response_contract(
    schema_name: str,
    middleware: Optional[ContractMiddleware] = None,
):
    """
    Decorator to validate response data against a contract.

    Usage:
        @validate_response_contract("Claim")
        async def get_claim(claim_id: str):
            ...
    """
    _middleware = middleware or ContractMiddleware(strict_mode=False)

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            if isinstance(result, dict):
                validation = _middleware.validate_response(result, schema_name)
                if not validation.valid:
                    # Log warnings but don't fail
                    pass

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if isinstance(result, dict):
                validation = _middleware.validate_response(result, schema_name)
                if not validation.valid:
                    pass

            return result

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class VersionNegotiator:
    """
    Handles API version negotiation.
    """

    def __init__(
        self,
        current_version: str = "2.0.0",
        min_supported: str = "2.0.0",
        max_supported: str = "2.0.0",
    ):
        self.current_version = current_version
        self.min_supported = min_supported
        self.max_supported = max_supported
        self._deprecated_versions: Set[str] = set()

    def deprecate_version(self, version: str) -> None:
        """Mark a version as deprecated."""
        self._deprecated_versions.add(version)

    def is_deprecated(self, version: str) -> bool:
        """Check if a version is deprecated."""
        return version in self._deprecated_versions

    def negotiate(self, requested_version: Optional[str]) -> Dict[str, Any]:
        """
        Negotiate API version.

        Args:
            requested_version: Version requested by client

        Returns:
            Dict with negotiation result
        """
        if not requested_version:
            return {
                "version": self.current_version,
                "negotiated": True,
                "warning": None,
            }

        # Parse versions
        try:
            req_parts = [int(p) for p in requested_version.split(".")]
            min_parts = [int(p) for p in self.min_supported.split(".")]
            max_parts = [int(p) for p in self.max_supported.split(".")]
        except (ValueError, AttributeError):
            return {
                "version": self.current_version,
                "negotiated": False,
                "error": f"Invalid version format: {requested_version}",
            }

        # Check if version is supported
        if req_parts[0] < min_parts[0]:
            return {
                "version": self.current_version,
                "negotiated": False,
                "error": f"Version {requested_version} is no longer supported. Minimum: {self.min_supported}",
            }

        if req_parts[0] > max_parts[0]:
            return {
                "version": self.current_version,
                "negotiated": False,
                "error": f"Version {requested_version} is not yet supported. Maximum: {self.max_supported}",
            }

        # Check for deprecation
        warning = None
        if self.is_deprecated(requested_version):
            warning = f"Version {requested_version} is deprecated and will be removed in a future release"

        return {
            "version": requested_version,
            "negotiated": True,
            "warning": warning,
        }

    def get_version_info(self) -> Dict[str, Any]:
        """Get version information."""
        return {
            "current": self.current_version,
            "min_supported": self.min_supported,
            "max_supported": self.max_supported,
            "deprecated": list(self._deprecated_versions),
        }


# Global instances
_default_validator = StrictContractValidator()
_default_middleware = ContractMiddleware(validator=_default_validator)
_default_negotiator = VersionNegotiator()


def get_validator() -> StrictContractValidator:
    """Get the default validator instance."""
    return _default_validator


def get_middleware() -> ContractMiddleware:
    """Get the default middleware instance."""
    return _default_middleware


def get_negotiator() -> VersionNegotiator:
    """Get the default version negotiator instance."""
    return _default_negotiator
