"""
S39: Tests for Contract Validation Middleware
"""
import pytest
from datetime import datetime, timezone

from app.contracts.middleware import (
    ContractMiddleware,
    ContractValidationError,
    VersionNegotiator,
    validate_request_contract,
    validate_response_contract,
    get_validator,
    get_middleware,
    get_negotiator,
)
from app.contracts.validator import (
    StrictContractValidator,
    ValidationResult,
    ValidationErrorCode,
)


class TestContractMiddleware:
    """Tests for ContractMiddleware."""

    def test_create_middleware(self):
        middleware = ContractMiddleware()
        assert middleware.strict_mode is True
        assert middleware.collect_metrics is True

    def test_create_non_strict_middleware(self):
        middleware = ContractMiddleware(strict_mode=False)
        assert middleware.strict_mode is False

    def test_create_without_metrics(self):
        middleware = ContractMiddleware(collect_metrics=False)
        assert middleware.collect_metrics is False

    def test_validate_request_valid(self):
        middleware = ContractMiddleware()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a valid claim with enough text",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = middleware.validate_request(data, "Claim")
        assert result.valid is True

    def test_validate_request_invalid_raises(self):
        middleware = ContractMiddleware(strict_mode=True)
        data = {
            "text": "Missing required id",
        }

        with pytest.raises(ContractValidationError):
            middleware.validate_request(data, "Claim")

    def test_validate_request_invalid_non_strict(self):
        middleware = ContractMiddleware(strict_mode=False)
        data = {
            "text": "Missing required id",
        }

        result = middleware.validate_request(data, "Claim")
        assert result.valid is False

    def test_validate_request_partial(self):
        middleware = ContractMiddleware()
        data = {
            "verdict": "true",
        }

        result = middleware.validate_request(data, "Claim", partial=True)
        assert result.valid is True

    def test_validate_response_valid(self):
        middleware = ContractMiddleware()
        data = {
            "status": "success",
            "meta": {
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "abc123",
            },
            "data": {
                "id": "clm_01HQ5YZ0000000000000000000",
                "text": "Valid claim text for testing",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
        }

        result = middleware.validate_response(data, "Claim")
        assert result.valid is True

    def test_validate_response_list(self):
        middleware = ContractMiddleware()
        data = {
            "status": "success",
            "meta": {
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "abc123",
            },
            "data": [
                {
                    "id": "clm_01HQ5YZ0000000000000000000",
                    "text": "Valid claim text for testing",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                },
            ],
        }

        result = middleware.validate_response(data, "Claim")
        assert result.valid is True

    def test_validate_response_invalid_item_in_list(self):
        middleware = ContractMiddleware()
        data = {
            "status": "success",
            "meta": {
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "abc123",
            },
            "data": [
                {
                    "id": "invalid_id",  # Invalid pattern
                    "text": "Valid claim text for testing",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                },
            ],
        }

        result = middleware.validate_response(data, "Claim")
        assert result.valid is False


class TestMiddlewareMetrics:
    """Tests for middleware metrics collection."""

    def test_metrics_initial(self):
        middleware = ContractMiddleware()
        metrics = middleware.get_metrics()

        assert metrics["total_validations"] == 0
        assert metrics["failures"] == 0
        assert metrics["failure_rate"] == 0.0

    def test_metrics_after_validations(self):
        middleware = ContractMiddleware(strict_mode=False)

        # Valid request
        middleware.validate_request({
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "Valid claim with enough text",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }, "Claim")

        # Invalid request
        middleware.validate_request({"invalid": "data"}, "Claim")

        metrics = middleware.get_metrics()
        assert metrics["total_validations"] == 2
        assert metrics["failures"] == 1
        assert metrics["failure_rate"] == 0.5

    def test_reset_metrics(self):
        middleware = ContractMiddleware(strict_mode=False)
        middleware.validate_request({"invalid": "data"}, "Claim")

        middleware.reset_metrics()
        metrics = middleware.get_metrics()

        assert metrics["total_validations"] == 0
        assert metrics["failures"] == 0


class TestWrapResponse:
    """Tests for response wrapping."""

    def test_wrap_response_basic(self):
        middleware = ContractMiddleware()
        data = {"result": "ok"}

        response = middleware.wrap_response(data)

        assert response["status"] == "success"
        assert response["data"] == {"result": "ok"}
        assert "meta" in response
        assert "version" in response["meta"]
        assert "timestamp" in response["meta"]

    def test_wrap_response_with_request_id(self):
        middleware = ContractMiddleware()
        response = middleware.wrap_response(
            data={"result": "ok"},
            request_id="custom_id_123",
        )

        assert response["meta"]["request_id"] == "custom_id_123"

    def test_wrap_response_with_deprecation(self):
        middleware = ContractMiddleware()
        response = middleware.wrap_response(
            data={"result": "ok"},
            deprecation_warning="This endpoint is deprecated",
        )

        assert response["meta"]["deprecation_warning"] == "This endpoint is deprecated"

    def test_wrap_error(self):
        from app.contracts.v1 import ErrorContract

        middleware = ContractMiddleware()
        errors = [ErrorContract("ERR_001", "Something went wrong")]

        response = middleware.wrap_error(errors)

        assert response["status"] == "error"
        assert len(response["errors"]) == 1


class TestContractValidationError:
    """Tests for ContractValidationError exception."""

    def test_exception_has_result(self):
        result = ValidationResult(valid=False)
        from app.contracts.validator import ValidationIssue
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.MISSING_REQUIRED,
            message="Required field",
            field="id",
        ))

        error = ContractValidationError(result)

        assert error.result is result
        assert len(error.errors) == 1


class TestVersionNegotiator:
    """Tests for VersionNegotiator."""

    def test_create_negotiator(self):
        negotiator = VersionNegotiator()
        assert negotiator.current_version == "2.0.0"
        assert negotiator.min_supported == "2.0.0"
        assert negotiator.max_supported == "2.0.0"

    def test_create_custom_negotiator(self):
        negotiator = VersionNegotiator(
            current_version="3.0.0",
            min_supported="2.0.0",
            max_supported="3.0.0",
        )
        assert negotiator.current_version == "3.0.0"
        assert negotiator.min_supported == "2.0.0"

    def test_negotiate_no_version(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate(None)

        assert result["negotiated"] is True
        assert result["version"] == "2.0.0"
        assert result["warning"] is None

    def test_negotiate_current_version(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate("2.0.0")

        assert result["negotiated"] is True
        assert result["version"] == "2.0.0"

    def test_negotiate_old_version(self):
        negotiator = VersionNegotiator(
            current_version="2.0.0",
            min_supported="2.0.0",
        )
        result = negotiator.negotiate("1.0.0")

        assert result["negotiated"] is False
        assert "error" in result

    def test_negotiate_future_version(self):
        negotiator = VersionNegotiator(
            current_version="2.0.0",
            max_supported="2.0.0",
        )
        result = negotiator.negotiate("3.0.0")

        assert result["negotiated"] is False
        assert "error" in result

    def test_negotiate_invalid_format(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate("invalid")

        assert result["negotiated"] is False
        assert "error" in result

    def test_deprecate_version(self):
        negotiator = VersionNegotiator(
            current_version="2.1.0",
            min_supported="2.0.0",
            max_supported="2.1.0",
        )
        negotiator.deprecate_version("2.0.0")

        assert negotiator.is_deprecated("2.0.0") is True
        assert negotiator.is_deprecated("2.1.0") is False

    def test_negotiate_deprecated_version(self):
        negotiator = VersionNegotiator(
            current_version="2.1.0",
            min_supported="2.0.0",
            max_supported="2.1.0",
        )
        negotiator.deprecate_version("2.0.0")
        result = negotiator.negotiate("2.0.0")

        assert result["negotiated"] is True
        assert result["warning"] is not None
        assert "deprecated" in result["warning"].lower()

    def test_get_version_info(self):
        negotiator = VersionNegotiator()
        negotiator.deprecate_version("1.9.0")

        info = negotiator.get_version_info()

        assert info["current"] == "2.0.0"
        assert info["min_supported"] == "2.0.0"
        assert "1.9.0" in info["deprecated"]


class TestDecorators:
    """Tests for validation decorators."""

    def test_validate_request_decorator_sync(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_request_contract("Claim", middleware=middleware)
        def handler(data):
            return {"success": True}

        result = handler(data={
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "Valid claim with enough text",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        })

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_validate_request_decorator_async(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_request_contract("Claim", middleware=middleware)
        async def handler(data):
            return {"success": True}

        result = await handler(data={
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "Valid claim with enough text",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        })

        assert result["success"] is True

    def test_validate_response_decorator_sync(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_response_contract("Claim", middleware=middleware)
        def handler():
            return {
                "status": "success",
                "meta": {"version": "2.0.0", "timestamp": "2024-01-01T00:00:00"},
                "data": {
                    "id": "clm_01HQ5YZ0000000000000000000",
                    "text": "Valid claim",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                },
            }

        result = handler()
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_validate_response_decorator_async(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_response_contract("Claim", middleware=middleware)
        async def handler():
            return {
                "status": "success",
                "meta": {"version": "2.0.0", "timestamp": "2024-01-01T00:00:00"},
                "data": {
                    "id": "clm_01HQ5YZ0000000000000000000",
                    "text": "Valid claim",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                },
            }

        result = await handler()
        assert result["status"] == "success"


class TestGlobalInstances:
    """Tests for global instance getters."""

    def test_get_validator(self):
        validator = get_validator()
        assert isinstance(validator, StrictContractValidator)

    def test_get_middleware(self):
        middleware = get_middleware()
        assert isinstance(middleware, ContractMiddleware)

    def test_get_negotiator(self):
        negotiator = get_negotiator()
        assert isinstance(negotiator, VersionNegotiator)

    def test_global_instances_are_singletons(self):
        v1 = get_validator()
        v2 = get_validator()
        assert v1 is v2

        m1 = get_middleware()
        m2 = get_middleware()
        assert m1 is m2


class TestEdgeCases:
    """Tests for edge cases in middleware."""

    def test_validate_request_with_body_kwarg(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_request_contract("Claim", middleware=middleware)
        def handler(body):
            return {"received": True}

        result = handler(body={
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "Valid claim with enough text",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        })

        assert result["received"] is True

    def test_validate_request_with_positional_arg(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_request_contract("Claim", middleware=middleware)
        def handler(data):
            return {"received": True}

        result = handler({
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "Valid claim with enough text",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        })

        assert result["received"] is True

    def test_validate_response_non_dict_result(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_response_contract("Claim", middleware=middleware)
        def handler():
            return "not a dict"

        result = handler()
        assert result == "not a dict"

    def test_wrap_response_generates_request_id(self):
        middleware = ContractMiddleware()
        response = middleware.wrap_response(data={})

        assert "request_id" in response["meta"]
        assert len(response["meta"]["request_id"]) > 0

    def test_middleware_with_custom_validator(self):
        validator = StrictContractValidator(strict_mode=False)
        middleware = ContractMiddleware(validator=validator)

        assert middleware.validator is validator


class TestMiddlewareAdditionalCoverage:
    """Additional tests for better coverage."""

    def test_validate_request_no_data_found(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_request_contract("Claim", middleware=middleware)
        def handler(other_param):
            return {"received": True}

        # No data parameter, no args that are dict
        result = handler(other_param="something")
        assert result["received"] is True

    def test_validate_request_arg_not_dict(self):
        middleware = ContractMiddleware(strict_mode=False)

        @validate_request_contract("Claim", middleware=middleware)
        def handler(value):
            return {"received": True}

        # First arg is not a dict
        result = handler("not a dict")
        assert result["received"] is True

    def test_validate_response_invalid_logs_warning(self):
        """Response validation should log warnings but not fail."""
        middleware = ContractMiddleware(strict_mode=False)

        @validate_response_contract("Claim", middleware=middleware)
        def handler():
            return {
                "status": "success",
                "meta": {"version": "2.0.0", "timestamp": "2024-01-01T00:00:00"},
                "data": {
                    "id": "invalid_id",  # Invalid pattern
                    "text": "x",  # Too short
                },
            }

        # Should not raise, just log warnings
        result = handler()
        assert result["status"] == "success"

    def test_wrap_error_with_request_id(self):
        from app.contracts.v1 import ErrorContract

        middleware = ContractMiddleware()
        errors = [ErrorContract("ERR_001", "Error")]

        response = middleware.wrap_error(errors, request_id="custom_123")
        assert response["meta"]["request_id"] == "custom_123"

    def test_validate_response_without_schema(self):
        middleware = ContractMiddleware()
        data = {
            "status": "success",
            "meta": {
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "abc123",
            },
            "data": {"any": "data"},
        }

        result = middleware.validate_response(data)
        assert result.valid is True

    def test_contract_validation_error_message(self):
        from app.contracts.validator import ValidationResult, ValidationIssue, ValidationErrorCode

        result = ValidationResult(valid=False)
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.MISSING_REQUIRED,
            message="Error 1",
            field="field1",
        ))
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.INVALID_TYPE,
            message="Error 2",
            field="field2",
        ))

        error = ContractValidationError(result)
        assert "2 issues" in str(error)

    def test_metrics_avg_time(self):
        middleware = ContractMiddleware(strict_mode=False)

        # Do a few validations
        for _ in range(3):
            middleware.validate_request({
                "id": "clm_01HQ5YZ0000000000000000000",
                "text": "Valid claim with enough text",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }, "Claim")

        metrics = middleware.get_metrics()
        assert metrics["avg_validation_time_ms"] > 0

    def test_validate_response_invalid_data_in_list(self):
        middleware = ContractMiddleware(strict_mode=False)
        data = {
            "status": "success",
            "meta": {
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "abc123",
            },
            "data": [
                {"id": "invalid_id", "text": "short"},
            ],
        }

        result = middleware.validate_response(data, "Claim")
        assert result.valid is False
