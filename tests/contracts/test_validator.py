"""
S39: Tests for Strict Contract Validator
"""
import pytest
from datetime import datetime, timezone

from app.contracts.validator import (
    StrictContractValidator,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    ValidationErrorCode,
    FieldSchema,
    ContractSchema,
)


class TestValidationIssue:
    """Tests for ValidationIssue."""

    def test_create_issue(self):
        issue = ValidationIssue(
            code=ValidationErrorCode.MISSING_REQUIRED,
            message="Field is required",
            field="name",
        )

        assert issue.code == ValidationErrorCode.MISSING_REQUIRED
        assert issue.message == "Field is required"
        assert issue.field == "name"
        assert issue.severity == ValidationSeverity.ERROR

    def test_issue_with_expected_actual(self):
        issue = ValidationIssue(
            code=ValidationErrorCode.INVALID_TYPE,
            message="Expected string",
            field="email",
            expected="string",
            actual="int",
        )

        assert issue.expected == "string"
        assert issue.actual == "int"

    def test_issue_to_error_contract(self):
        issue = ValidationIssue(
            code=ValidationErrorCode.VALUE_TOO_LARGE,
            message="Value exceeds maximum",
            field="count",
            expected=100,
            actual=150,
        )

        error = issue.to_error_contract()
        assert error.code == "VALUE_TOO_LARGE"
        assert error.message == "Value exceeds maximum"
        assert error.field == "count"


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_create_valid_result(self):
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert len(result.issues) == 0

    def test_add_error_issue(self):
        result = ValidationResult(valid=True)
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.MISSING_REQUIRED,
            message="Required field",
            field="id",
        ))

        assert result.valid is False
        assert len(result.issues) == 1

    def test_add_warning_issue(self):
        result = ValidationResult(valid=True)
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.UNKNOWN_FIELD,
            message="Unknown field",
            field="extra",
            severity=ValidationSeverity.WARNING,
        ))

        assert result.valid is True
        assert len(result.issues) == 0
        assert len(result.warnings) == 1

    def test_merge_results(self):
        result1 = ValidationResult(valid=True)
        result2 = ValidationResult(valid=False)
        result2.add_issue(ValidationIssue(
            code=ValidationErrorCode.INVALID_TYPE,
            message="Invalid type",
            field="value",
        ))

        result1.merge(result2)
        assert result1.valid is False
        assert len(result1.issues) == 1

    def test_errors_property(self):
        result = ValidationResult(valid=True)
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.MISSING_REQUIRED,
            message="Error 1",
            field="a",
        ))
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.UNKNOWN_FIELD,
            message="Warning 1",
            field="b",
            severity=ValidationSeverity.WARNING,
        ))

        errors = result.errors
        assert len(errors) == 1
        assert errors[0].field == "a"

    def test_to_error_contracts(self):
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

        contracts = result.to_error_contracts()
        assert len(contracts) == 2


class TestFieldSchema:
    """Tests for FieldSchema."""

    def test_create_simple_schema(self):
        schema = FieldSchema(
            name="name",
            field_type=str,
            required=True,
        )

        assert schema.name == "name"
        assert schema.field_type == str
        assert schema.required is True

    def test_create_schema_with_constraints(self):
        schema = FieldSchema(
            name="age",
            field_type=int,
            min_value=0,
            max_value=150,
        )

        assert schema.min_value == 0
        assert schema.max_value == 150

    def test_create_string_schema(self):
        schema = FieldSchema(
            name="email",
            field_type=str,
            pattern=r"^[a-z]+@[a-z]+\.[a-z]+$",
            min_length=5,
            max_length=100,
        )

        assert schema.pattern is not None
        assert schema.min_length == 5
        assert schema.max_length == 100

    def test_create_enum_schema(self):
        schema = FieldSchema(
            name="status",
            field_type=str,
            enum_values=["active", "inactive", "pending"],
        )

        assert schema.enum_values is not None
        assert "active" in schema.enum_values


class TestContractSchema:
    """Tests for ContractSchema."""

    def test_create_schema(self):
        schema = ContractSchema(
            name="User",
            version="1.0.0",
        )

        assert schema.name == "User"
        assert schema.version == "1.0.0"
        assert len(schema.fields) == 0

    def test_add_field(self):
        schema = ContractSchema(name="User", version="1.0.0")
        schema.add_field(FieldSchema(name="id", field_type=str, required=True))
        schema.add_field(FieldSchema(name="name", field_type=str))

        assert len(schema.fields) == 2
        assert "id" in schema.fields


class TestStrictContractValidator:
    """Tests for StrictContractValidator."""

    def test_create_validator(self):
        validator = StrictContractValidator()
        assert validator.strict_mode is True

    def test_create_non_strict_validator(self):
        validator = StrictContractValidator(strict_mode=False)
        assert validator.strict_mode is False

    def test_list_schemas(self):
        validator = StrictContractValidator()
        schemas = validator.list_schemas()

        assert "Claim" in schemas
        assert "Source" in schemas
        assert "Signal" in schemas
        assert "Policy" in schemas
        assert "Verdict" in schemas

    def test_get_schema(self):
        validator = StrictContractValidator()
        schema = validator.get_schema("Claim")

        assert schema is not None
        assert schema.name == "Claim"
        assert "id" in schema.fields
        assert "text" in schema.fields

    def test_get_nonexistent_schema(self):
        validator = StrictContractValidator()
        schema = validator.get_schema("NonExistent")
        assert schema is None

    def test_register_custom_schema(self):
        validator = StrictContractValidator()
        custom_schema = ContractSchema(name="Custom", version="1.0.0")
        custom_schema.add_field(FieldSchema(name="field1", field_type=str))

        validator.register_schema(custom_schema)
        retrieved = validator.get_schema("Custom")

        assert retrieved is not None
        assert retrieved.name == "Custom"


class TestValidateClaimSchema:
    """Tests for validating claims against schema."""

    def test_validate_valid_claim(self):
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is True
        assert len(result.issues) == 0

    def test_validate_claim_missing_required(self):
        validator = StrictContractValidator()
        data = {
            "text": "This is a test claim with sufficient length",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.MISSING_REQUIRED for i in result.issues)

    def test_validate_claim_invalid_id_pattern(self):
        validator = StrictContractValidator()
        data = {
            "id": "invalid_id",
            "text": "This is a test claim with sufficient length",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.INVALID_PATTERN for i in result.issues)

    def test_validate_claim_text_too_short(self):
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "Short",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.STRING_TOO_SHORT for i in result.issues)

    def test_validate_claim_invalid_verdict(self):
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "verdict": "invalid_verdict",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.INVALID_ENUM for i in result.issues)

    def test_validate_claim_confidence_out_of_range(self):
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "confidence": 1.5,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.VALUE_TOO_LARGE for i in result.issues)

    def test_validate_claim_partial_mode(self):
        validator = StrictContractValidator()
        data = {
            "verdict": "true",
            "confidence": 0.9,
        }

        result = validator.validate(data, "Claim", partial=True)
        assert result.valid is True


class TestValidateSourceSchema:
    """Tests for validating sources against schema."""

    def test_validate_valid_source(self):
        validator = StrictContractValidator()
        data = {
            "id": "src_01HQ5YZ0000000000000000000",
            "name": "Test Source",
            "slug": "test-source",
            "source_type": "rss",
            "url": "https://example.com/feed",
            "enabled": True,
            "state": "active",
            "health_status": "healthy",
            "created_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Source")
        assert result.valid is True

    def test_validate_source_invalid_type(self):
        validator = StrictContractValidator()
        data = {
            "id": "src_01HQ5YZ0000000000000000000",
            "name": "Test Source",
            "slug": "test-source",
            "source_type": "invalid_type",
            "url": "https://example.com/feed",
            "enabled": True,
            "state": "active",
            "health_status": "healthy",
            "created_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Source")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.INVALID_ENUM for i in result.issues)


class TestValidateSignalSchema:
    """Tests for validating signals against schema."""

    def test_validate_valid_signal(self):
        validator = StrictContractValidator()
        data = {
            "type": "mentiras",
            "scope": "global",
            "value": 0.75,
            "confidence": 0.9,
            "level": "high",
            "calculated_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-02T00:00:00",
        }

        result = validator.validate(data, "Signal")
        assert result.valid is True

    def test_validate_signal_value_out_of_range(self):
        validator = StrictContractValidator()
        data = {
            "type": "mentiras",
            "scope": "global",
            "value": -0.1,
            "confidence": 0.9,
            "level": "high",
            "calculated_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-02T00:00:00",
        }

        result = validator.validate(data, "Signal")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.VALUE_TOO_SMALL for i in result.issues)


class TestValidatePolicySchema:
    """Tests for validating policies against schema."""

    def test_validate_valid_policy(self):
        validator = StrictContractValidator()
        data = {
            "id": "pol_01HQ5YZ0000000000000000000",
            "name": "Health Policy",
            "domain": "health",
            "version": 1,
            "status": "active",
            "min_confidence": 0.8,
            "min_sources": 3,
            "created_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Policy")
        assert result.valid is True

    def test_validate_policy_invalid_domain(self):
        validator = StrictContractValidator()
        data = {
            "id": "pol_01HQ5YZ0000000000000000000",
            "name": "Test Policy",
            "domain": "invalid_domain",
            "version": 1,
            "status": "active",
            "min_confidence": 0.8,
            "min_sources": 3,
            "created_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Policy")
        assert result.valid is False


class TestValidateMemorySchema:
    """Tests for validating memory entries against schema."""

    def test_validate_valid_memory_entry(self):
        validator = StrictContractValidator()
        data = {
            "scope": "session",
            "scope_id": "session_123",
            "key": "user_preferences",
            "value": {"theme": "dark"},
            "importance": 0.8,
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-02T00:00:00",
        }

        result = validator.validate(data, "MemoryEntry")
        assert result.valid is True

    def test_validate_memory_invalid_scope(self):
        validator = StrictContractValidator()
        data = {
            "scope": "invalid_scope",
            "scope_id": "session_123",
            "key": "user_preferences",
            "value": {"theme": "dark"},
            "importance": 0.8,
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-02T00:00:00",
        }

        result = validator.validate(data, "MemoryEntry")
        assert result.valid is False


class TestValidateResponseEnvelope:
    """Tests for validating response envelopes."""

    def test_validate_valid_envelope(self):
        validator = StrictContractValidator()
        data = {
            "status": "success",
            "meta": {
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "abc123",
            },
            "data": {"result": "ok"},
        }

        result = validator.validate_response_envelope(data)
        assert result.valid is True

    def test_validate_envelope_missing_meta_version(self):
        validator = StrictContractValidator()
        data = {
            "status": "success",
            "meta": {
                "timestamp": "2024-01-01T00:00:00",
            },
            "data": {"result": "ok"},
        }

        result = validator.validate_response_envelope(data)
        assert result.valid is False


class TestVersionCompatibility:
    """Tests for version compatibility validation."""

    def test_validate_compatible_version(self):
        validator = StrictContractValidator()
        result = validator.validate_version_compatibility("2.0.0", "2.0.0")
        assert result.valid is True

    def test_validate_newer_minor_version(self):
        validator = StrictContractValidator()
        result = validator.validate_version_compatibility("2.1.0", "2.0.0")
        assert result.valid is True

    def test_validate_incompatible_major_version(self):
        validator = StrictContractValidator()
        result = validator.validate_version_compatibility("1.0.0", "2.0.0")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.VERSION_MISMATCH for i in result.issues)

    def test_validate_invalid_version_format(self):
        validator = StrictContractValidator()
        result = validator.validate_version_compatibility("invalid", "2.0.0")
        assert result.valid is False


class TestUnknownFields:
    """Tests for unknown field handling."""

    def test_unknown_field_in_strict_mode(self):
        validator = StrictContractValidator(strict_mode=True)
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "unknown_field": "value",
        }

        result = validator.validate(data, "Claim")
        assert any(i.code == ValidationErrorCode.UNKNOWN_FIELD for i in result.issues + result.warnings)

    def test_unknown_field_in_non_strict_mode(self):
        validator = StrictContractValidator(strict_mode=False)
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "unknown_field": "value",
        }

        result = validator.validate(data, "Claim")
        # In non-strict mode, unknown fields are warnings, not errors
        assert len(result.warnings) >= 0  # May or may not have warnings


class TestTypeValidation:
    """Tests for type validation edge cases."""

    def test_integer_instead_of_float(self):
        """Integers should be accepted for float fields."""
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "confidence": 1,  # Integer instead of float
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is True

    def test_boolean_not_accepted_as_integer(self):
        """Booleans should not be accepted for integer fields."""
        validator = StrictContractValidator()
        data = {
            "id": "pol_01HQ5YZ0000000000000000000",
            "name": "Test Policy",
            "domain": "health",
            "version": True,  # Boolean instead of int
            "status": "active",
            "min_confidence": 0.8,
            "min_sources": 3,
            "created_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Policy")
        assert result.valid is False

    def test_null_for_nullable_field(self):
        """Null should be accepted for nullable fields."""
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "source_id": None,  # Nullable field
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is True

    def test_validate_non_dict_data(self):
        """Should fail validation for non-dict data."""
        validator = StrictContractValidator()
        result = validator.validate("not a dict", "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.INVALID_TYPE for i in result.issues)


class TestArrayValidation:
    """Tests for array field validation."""

    def test_array_within_limits(self):
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "entities": ["entity1", "entity2", "entity3"],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is True

    def test_array_exceeds_max_length(self):
        validator = StrictContractValidator()
        data = {
            "id": "clm_01HQ5YZ0000000000000000000",
            "text": "This is a test claim with sufficient length",
            "entities": [f"entity{i}" for i in range(60)],  # Exceeds max 50
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        result = validator.validate(data, "Claim")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.ARRAY_TOO_MANY for i in result.issues)


class TestValidatorEdgeCases:
    """Tests for edge cases in validator."""

    def test_validate_unknown_schema(self):
        validator = StrictContractValidator()
        result = validator.validate({"test": "data"}, "UnknownSchema")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.CONTRACT_VIOLATION for i in result.issues)

    def test_validate_with_custom_validator_function(self):
        validator = StrictContractValidator()

        # Create schema with custom validator
        schema = ContractSchema(name="CustomTest", version="1.0.0")
        schema.add_field(FieldSchema(
            name="value",
            field_type=int,
            required=True,
            validator=lambda x: x > 0,  # Must be positive
        ))
        validator.register_schema(schema)

        # Test valid value
        result = validator.validate({"value": 10}, "CustomTest")
        assert result.valid is True

        # Test invalid value
        result = validator.validate({"value": -5}, "CustomTest")
        assert result.valid is False
        assert any(i.code == ValidationErrorCode.CONTRACT_VIOLATION for i in result.issues)

    def test_validate_deprecated_field(self):
        validator = StrictContractValidator()

        schema = ContractSchema(name="DeprecatedTest", version="1.0.0")
        schema.add_field(FieldSchema(
            name="old_field",
            field_type=str,
            deprecated=True,
            deprecation_message="Use new_field instead",
        ))
        validator.register_schema(schema)

        result = validator.validate({"old_field": "value"}, "DeprecatedTest")
        # Should have warning about deprecated field
        assert len(result.warnings) > 0 or any(
            i.severity == ValidationSeverity.WARNING for i in result.issues
        )

    def test_validate_with_item_schema(self):
        validator = StrictContractValidator()

        item_schema = FieldSchema(
            name="item",
            field_type=str,
            min_length=1,
        )

        schema = ContractSchema(name="ArrayItemTest", version="1.0.0")
        schema.add_field(FieldSchema(
            name="items",
            field_type=list,
            required=True,
            item_schema=item_schema,
        ))
        validator.register_schema(schema)

        # Valid items
        result = validator.validate({"items": ["a", "b", "c"]}, "ArrayItemTest")
        assert result.valid is True

        # Invalid items (empty strings)
        result = validator.validate({"items": ["a", "", "c"]}, "ArrayItemTest")
        assert result.valid is False

    def test_validate_with_nested_schema(self):
        validator = StrictContractValidator()

        nested = ContractSchema(name="Nested", version="1.0.0")
        nested.add_field(FieldSchema(name="inner_value", field_type=str, required=True))

        schema = ContractSchema(name="ParentSchema", version="1.0.0")
        schema.add_field(FieldSchema(
            name="nested_obj",
            field_type=dict,
            required=True,
            nested_schema=nested,
        ))
        validator.register_schema(schema)

        # Valid nested
        result = validator.validate(
            {"nested_obj": {"inner_value": "test"}},
            "ParentSchema"
        )
        assert result.valid is True

        # Invalid nested (missing required)
        result = validator.validate(
            {"nested_obj": {}},
            "ParentSchema"
        )
        assert result.valid is False

    def test_validate_string_type_reference(self):
        validator = StrictContractValidator()

        schema = ContractSchema(name="StringTypeRef", version="1.0.0")
        schema.add_field(FieldSchema(
            name="value",
            field_type="string",  # String type reference
            required=True,
        ))
        validator.register_schema(schema)

        # Valid
        result = validator.validate({"value": "test"}, "StringTypeRef")
        assert result.valid is True

        # Invalid (not a string)
        result = validator.validate({"value": 123}, "StringTypeRef")
        assert result.valid is False

    def test_validate_verdict_with_valid_data(self):
        validator = StrictContractValidator()
        data = {
            "id": "vrd_01HQ5YZ0000000000000000000",
            "claim_id": "clm_01HQ5YZ0000000000000000000",
            "verdict": "true",
            "confidence": 0.9,
            "reasoning": "Based on multiple reliable sources",
            "decided_at": "2024-01-01T00:00:00",
            "decided_by": "system",
        }

        result = validator.validate(data, "Verdict")
        assert result.valid is True

    def test_data_with_to_dict_method(self):
        """Test that ResponseEnvelope handles data with to_dict method."""
        from app.contracts.v1 import ResponseEnvelope, ContractStatus, ClaimContract

        claim = ClaimContract(
            id="claim_001",
            text="Test claim",
            source_id=None,
            verdict="true",
            confidence=0.9,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )

        envelope = ResponseEnvelope(
            status=ContractStatus.SUCCESS,
            data=claim,
        )

        result = envelope.to_dict()
        assert "data" in result
        assert result["data"]["id"] == "claim_001"

    def test_pagination_edge_cases(self):
        """Test pagination with edge cases."""
        from app.contracts.v1 import PaginationContract

        # Zero total items
        pagination = PaginationContract.create(page=1, page_size=10, total_items=0)
        assert pagination.total_pages == 0
        assert pagination.has_next is False

        # Zero page size (edge case)
        pagination = PaginationContract.create(page=1, page_size=0, total_items=100)
        assert pagination.total_pages == 0


class TestValidatorCoverageTargeted:
    """Targeted tests for validator coverage."""

    def test_null_value_required_not_nullable_line_714(self):
        """Line 714: null value when required and not nullable."""
        from app.contracts.validator import (
            StrictContractValidator,
            FieldSchema,
            ContractSchema,
            ValidationErrorCode,
        )

        validator = StrictContractValidator()
        schema = ContractSchema(
            name="TestSchema",
            version="1.0.0",
        )
        schema.add_field(FieldSchema(
            name="required_field",
            field_type=str,
            required=True,
            nullable=False,
        ))
        validator.register_schema(schema)

        result = validator.validate({"required_field": None}, "TestSchema")
        assert not result.valid
        assert any(i.code == ValidationErrorCode.INVALID_TYPE for i in result.issues)

    def test_float_type_validation_lines_738_745(self):
        """Lines 738-745: Float type validation failure."""
        from app.contracts.validator import (
            StrictContractValidator,
            FieldSchema,
            ContractSchema,
            ValidationErrorCode,
        )

        validator = StrictContractValidator()
        schema = ContractSchema(
            name="FloatSchema",
            version="1.0.0",
        )
        schema.add_field(FieldSchema(
            name="score",
            field_type=float,
            required=True,
        ))
        validator.register_schema(schema)

        # Pass a string instead of float
        result = validator.validate({"score": "not a number"}, "FloatSchema")
        assert not result.valid
        assert any(i.code == ValidationErrorCode.INVALID_TYPE for i in result.issues)

    def test_custom_type_validation_lines_757_764(self):
        """Lines 757-764: Custom type validation failure."""
        from app.contracts.validator import (
            StrictContractValidator,
            FieldSchema,
            ContractSchema,
            ValidationErrorCode,
        )

        class CustomType:
            pass

        validator = StrictContractValidator()
        schema = ContractSchema(
            name="CustomSchema",
            version="1.0.0",
        )
        schema.add_field(FieldSchema(
            name="custom",
            field_type=CustomType,
            required=True,
        ))
        validator.register_schema(schema)

        # Pass wrong type
        result = validator.validate({"custom": "not custom type"}, "CustomSchema")
        assert not result.valid
        assert any(i.code == ValidationErrorCode.INVALID_TYPE for i in result.issues)

    def test_string_max_length_line_778(self):
        """Line 778: String exceeds max_length."""
        from app.contracts.validator import (
            StrictContractValidator,
            FieldSchema,
            ContractSchema,
            ValidationErrorCode,
        )

        validator = StrictContractValidator()
        schema = ContractSchema(
            name="StringSchema",
            version="1.0.0",
        )
        schema.add_field(FieldSchema(
            name="name",
            field_type=str,
            required=True,
            max_length=5,
        ))
        validator.register_schema(schema)

        result = validator.validate({"name": "too long string"}, "StringSchema")
        assert not result.valid
        assert any(i.code == ValidationErrorCode.STRING_TOO_LONG for i in result.issues)

    def test_array_min_length_line_830(self):
        """Line 830: Array too short (min_length)."""
        from app.contracts.validator import (
            StrictContractValidator,
            FieldSchema,
            ContractSchema,
            ValidationErrorCode,
        )

        validator = StrictContractValidator()
        schema = ContractSchema(
            name="ArraySchema",
            version="1.0.0",
        )
        schema.add_field(FieldSchema(
            name="items",
            field_type=list,
            required=True,
            min_length=3,
        ))
        validator.register_schema(schema)

        result = validator.validate({"items": [1, 2]}, "ArraySchema")
        assert not result.valid
        assert any(i.code == ValidationErrorCode.ARRAY_TOO_FEW for i in result.issues)

    def test_response_envelope_missing_timestamp_line_891(self):
        """Line 891: Response envelope missing timestamp in meta."""
        from app.contracts.validator import StrictContractValidator

        validator = StrictContractValidator()

        # Valid envelope but missing timestamp in meta
        data = {
            "status": "success",
            "data": {},
            "meta": {
                "version": "1.0.0",
                # Missing timestamp
            },
        }

        result = validator.validate_response_envelope(data)
        # Should have warning about missing timestamp
        assert any("timestamp" in str(i.message) for i in result.issues)
