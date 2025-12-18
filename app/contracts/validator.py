"""
S39-BE-023: Strict Contract Validator

Validates API requests and responses against contract schemas.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from app.contracts.v1 import ErrorContract


class ValidationSeverity(str, Enum):
    """Severity level for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationErrorCode(str, Enum):
    """Validation error codes."""
    MISSING_REQUIRED = "MISSING_REQUIRED"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_PATTERN = "INVALID_PATTERN"
    VALUE_TOO_SMALL = "VALUE_TOO_SMALL"
    VALUE_TOO_LARGE = "VALUE_TOO_LARGE"
    STRING_TOO_SHORT = "STRING_TOO_SHORT"
    STRING_TOO_LONG = "STRING_TOO_LONG"
    ARRAY_TOO_FEW = "ARRAY_TOO_FEW"
    ARRAY_TOO_MANY = "ARRAY_TOO_MANY"
    INVALID_ENUM = "INVALID_ENUM"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    VERSION_MISMATCH = "VERSION_MISMATCH"


@dataclass
class ValidationIssue:
    """A single validation issue."""
    code: ValidationErrorCode
    message: str
    field: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    expected: Optional[Any] = None
    actual: Optional[Any] = None

    def to_error_contract(self) -> ErrorContract:
        """Convert to ErrorContract."""
        return ErrorContract(
            code=self.code.value,
            message=self.message,
            field=self.field,
            details={
                "severity": self.severity.value,
                "expected": str(self.expected) if self.expected else None,
                "actual": str(self.actual) if self.actual else None,
            },
        )


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        """Get error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        if issue.severity == ValidationSeverity.ERROR:
            self.valid = False
            self.issues.append(issue)
        else:
            self.warnings.append(issue)

    def merge(self, other: "ValidationResult") -> None:
        """Merge another result into this one."""
        if not other.valid:
            self.valid = False
        self.issues.extend(other.issues)
        self.warnings.extend(other.warnings)

    def to_error_contracts(self) -> List[ErrorContract]:
        """Convert all issues to ErrorContracts."""
        return [i.to_error_contract() for i in self.issues]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "valid": self.valid,
            "issues": [
                {
                    "code": i.code.value,
                    "message": i.message,
                    "field": i.field,
                    "severity": i.severity.value,
                }
                for i in self.issues
            ],
            "warnings": [
                {
                    "code": w.code.value,
                    "message": w.message,
                    "field": w.field,
                    "severity": w.severity.value,
                }
                for w in self.warnings
            ],
        }


@dataclass
class FieldSchema:
    """Schema definition for a field."""
    name: str
    field_type: Union[Type, str]
    required: bool = False
    nullable: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum_values: Optional[List[Any]] = None
    item_schema: Optional["FieldSchema"] = None
    nested_schema: Optional["ContractSchema"] = None
    validator: Optional[Callable[[Any], bool]] = None
    deprecated: bool = False
    deprecation_message: Optional[str] = None


@dataclass
class ContractSchema:
    """Schema definition for a contract."""
    name: str
    version: str
    fields: Dict[str, FieldSchema] = field(default_factory=dict)
    allow_extra_fields: bool = False
    strict_mode: bool = True

    def add_field(self, schema: FieldSchema) -> "ContractSchema":
        """Add a field to the schema."""
        self.fields[schema.name] = schema
        return self


class StrictContractValidator:
    """
    Validates data against contract schemas with strict enforcement.
    """

    # Common patterns
    PATTERNS = {
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://[^\s/$.?#].[^\s]*$",
        "semver": r"^\d+\.\d+\.\d+$",
        "claim_id": r"^clm_[a-zA-Z0-9]{26}$",
        "source_id": r"^src_[a-zA-Z0-9]{26}$",
        "policy_id": r"^pol_[a-zA-Z0-9]{26}$",
        "verdict_id": r"^vrd_[a-zA-Z0-9]{26}$",
        "explanation_id": r"^exp_[a-zA-Z0-9]{26}$",
        "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        "sha256": r"^[a-f0-9]{64}$",
    }

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self._schemas: Dict[str, ContractSchema] = {}
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._register_default_schemas()

    def _register_default_schemas(self) -> None:
        """Register default contract schemas."""
        # Claim schema
        claim_schema = ContractSchema(
            name="Claim",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        claim_schema.add_field(FieldSchema(
            name="id",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["claim_id"],
        ))
        claim_schema.add_field(FieldSchema(
            name="text",
            field_type=str,
            required=True,
            min_length=10,
            max_length=5000,
        ))
        claim_schema.add_field(FieldSchema(
            name="source_id",
            field_type=str,
            nullable=True,
            pattern=self.PATTERNS["source_id"],
        ))
        claim_schema.add_field(FieldSchema(
            name="verdict",
            field_type=str,
            nullable=True,
            enum_values=["true", "false", "unverified", "inconclusive", "misleading", "out_of_scope"],
        ))
        claim_schema.add_field(FieldSchema(
            name="confidence",
            field_type=float,
            nullable=True,
            min_value=0.0,
            max_value=1.0,
        ))
        claim_schema.add_field(FieldSchema(
            name="created_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        claim_schema.add_field(FieldSchema(
            name="updated_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        claim_schema.add_field(FieldSchema(
            name="entities",
            field_type=list,
            max_length=50,
        ))
        claim_schema.add_field(FieldSchema(
            name="topics",
            field_type=list,
            max_length=20,
        ))
        claim_schema.add_field(FieldSchema(
            name="evidence_count",
            field_type=int,
            min_value=0,
        ))
        claim_schema.add_field(FieldSchema(
            name="metadata",
            field_type=dict,
        ))
        self._schemas["Claim"] = claim_schema

        # Source schema
        source_schema = ContractSchema(
            name="Source",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        source_schema.add_field(FieldSchema(
            name="id",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["source_id"],
        ))
        source_schema.add_field(FieldSchema(
            name="name",
            field_type=str,
            required=True,
            min_length=1,
            max_length=255,
        ))
        source_schema.add_field(FieldSchema(
            name="slug",
            field_type=str,
            required=True,
            pattern=r"^[a-z0-9-]+$",
            max_length=100,
        ))
        source_schema.add_field(FieldSchema(
            name="source_type",
            field_type=str,
            required=True,
            enum_values=["rss", "api", "website", "social", "official", "factcheck"],
        ))
        source_schema.add_field(FieldSchema(
            name="url",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["url"],
        ))
        source_schema.add_field(FieldSchema(
            name="enabled",
            field_type=bool,
            required=True,
        ))
        source_schema.add_field(FieldSchema(
            name="state",
            field_type=str,
            required=True,
            enum_values=["active", "paused", "error", "disabled", "pending_approval"],
        ))
        source_schema.add_field(FieldSchema(
            name="health_status",
            field_type=str,
            required=True,
            enum_values=["healthy", "degraded", "unhealthy", "unknown"],
        ))
        source_schema.add_field(FieldSchema(
            name="credibility_score",
            field_type=float,
            nullable=True,
            min_value=0.0,
            max_value=1.0,
        ))
        source_schema.add_field(FieldSchema(
            name="created_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        source_schema.add_field(FieldSchema(
            name="last_ingestion_at",
            field_type=str,
            nullable=True,
            pattern=self.PATTERNS["datetime"],
        ))
        self._schemas["Source"] = source_schema

        # Signal schema
        signal_schema = ContractSchema(
            name="Signal",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        signal_schema.add_field(FieldSchema(
            name="type",
            field_type=str,
            required=True,
            enum_values=["mentiras", "batalha", "silencio", "fragilidade", "credibility", "velocity", "contradiction"],
        ))
        signal_schema.add_field(FieldSchema(
            name="scope",
            field_type=str,
            required=True,
            enum_values=["global", "source", "topic", "entity", "claim"],
        ))
        signal_schema.add_field(FieldSchema(
            name="scope_id",
            field_type=str,
            nullable=True,
        ))
        signal_schema.add_field(FieldSchema(
            name="value",
            field_type=float,
            required=True,
            min_value=0.0,
            max_value=1.0,
        ))
        signal_schema.add_field(FieldSchema(
            name="confidence",
            field_type=float,
            required=True,
            min_value=0.0,
            max_value=1.0,
        ))
        signal_schema.add_field(FieldSchema(
            name="level",
            field_type=str,
            required=True,
            enum_values=["none", "low", "medium", "high", "critical"],
        ))
        signal_schema.add_field(FieldSchema(
            name="calculated_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        signal_schema.add_field(FieldSchema(
            name="expires_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        self._schemas["Signal"] = signal_schema

        # Policy schema
        policy_schema = ContractSchema(
            name="Policy",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        policy_schema.add_field(FieldSchema(
            name="id",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["policy_id"],
        ))
        policy_schema.add_field(FieldSchema(
            name="name",
            field_type=str,
            required=True,
            min_length=1,
            max_length=255,
        ))
        policy_schema.add_field(FieldSchema(
            name="domain",
            field_type=str,
            required=True,
            enum_values=["health", "politics", "science", "economy", "general", "environment", "security"],
        ))
        policy_schema.add_field(FieldSchema(
            name="version",
            field_type=int,
            required=True,
            min_value=1,
        ))
        policy_schema.add_field(FieldSchema(
            name="status",
            field_type=str,
            required=True,
            enum_values=["draft", "active", "deprecated", "archived"],
        ))
        policy_schema.add_field(FieldSchema(
            name="min_confidence",
            field_type=float,
            required=True,
            min_value=0.0,
            max_value=1.0,
        ))
        policy_schema.add_field(FieldSchema(
            name="min_sources",
            field_type=int,
            required=True,
            min_value=1,
            max_value=100,
        ))
        policy_schema.add_field(FieldSchema(
            name="sensitive",
            field_type=bool,
        ))
        policy_schema.add_field(FieldSchema(
            name="created_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        policy_schema.add_field(FieldSchema(
            name="activated_at",
            field_type=str,
            nullable=True,
            pattern=self.PATTERNS["datetime"],
        ))
        self._schemas["Policy"] = policy_schema

        # Verdict schema
        verdict_schema = ContractSchema(
            name="Verdict",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        verdict_schema.add_field(FieldSchema(
            name="id",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["verdict_id"],
        ))
        verdict_schema.add_field(FieldSchema(
            name="claim_id",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["claim_id"],
        ))
        verdict_schema.add_field(FieldSchema(
            name="verdict",
            field_type=str,
            required=True,
            enum_values=["true", "false", "unverified", "inconclusive", "misleading", "out_of_scope"],
        ))
        verdict_schema.add_field(FieldSchema(
            name="confidence",
            field_type=float,
            required=True,
            min_value=0.0,
            max_value=1.0,
        ))
        verdict_schema.add_field(FieldSchema(
            name="reasoning",
            field_type=str,
            required=True,
            max_length=10000,
        ))
        verdict_schema.add_field(FieldSchema(
            name="evidence_ids",
            field_type=list,
        ))
        verdict_schema.add_field(FieldSchema(
            name="sources_count",
            field_type=int,
            min_value=0,
        ))
        verdict_schema.add_field(FieldSchema(
            name="decided_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        verdict_schema.add_field(FieldSchema(
            name="decided_by",
            field_type=str,
            required=True,
            enum_values=["system", "human", "llm", "policy"],
        ))
        verdict_schema.add_field(FieldSchema(
            name="policy_id",
            field_type=str,
            nullable=True,
            pattern=self.PATTERNS["policy_id"],
        ))
        self._schemas["Verdict"] = verdict_schema

        # Memory Entry schema
        memory_schema = ContractSchema(
            name="MemoryEntry",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        memory_schema.add_field(FieldSchema(
            name="scope",
            field_type=str,
            required=True,
            enum_values=["session", "flow", "agent", "global"],
        ))
        memory_schema.add_field(FieldSchema(
            name="scope_id",
            field_type=str,
            required=True,
            max_length=255,
        ))
        memory_schema.add_field(FieldSchema(
            name="key",
            field_type=str,
            required=True,
            max_length=255,
        ))
        memory_schema.add_field(FieldSchema(
            name="value",
            field_type=dict,
            required=True,
        ))
        memory_schema.add_field(FieldSchema(
            name="importance",
            field_type=float,
            required=True,
            min_value=0.0,
            max_value=1.0,
        ))
        memory_schema.add_field(FieldSchema(
            name="created_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        memory_schema.add_field(FieldSchema(
            name="expires_at",
            field_type=str,
            required=True,
            pattern=self.PATTERNS["datetime"],
        ))
        self._schemas["MemoryEntry"] = memory_schema

        # Response envelope schema
        envelope_schema = ContractSchema(
            name="ResponseEnvelope",
            version="2.0.0",
            strict_mode=self.strict_mode,
        )
        envelope_schema.add_field(FieldSchema(
            name="status",
            field_type=str,
            required=True,
            enum_values=["success", "error", "partial"],
        ))
        envelope_schema.add_field(FieldSchema(
            name="meta",
            field_type=dict,
            required=True,
        ))
        envelope_schema.add_field(FieldSchema(
            name="data",
            field_type=object,
            nullable=True,
        ))
        envelope_schema.add_field(FieldSchema(
            name="errors",
            field_type=list,
        ))
        envelope_schema.add_field(FieldSchema(
            name="pagination",
            field_type=dict,
            nullable=True,
        ))
        self._schemas["ResponseEnvelope"] = envelope_schema

    def register_schema(self, schema: ContractSchema) -> None:
        """Register a custom schema."""
        self._schemas[schema.name] = schema

    def get_schema(self, name: str) -> Optional[ContractSchema]:
        """Get a registered schema by name."""
        return self._schemas.get(name)

    def list_schemas(self) -> List[str]:
        """List all registered schema names."""
        return list(self._schemas.keys())

    def _get_pattern(self, pattern: str) -> re.Pattern:
        """Get or compile a regex pattern."""
        if pattern not in self._compiled_patterns:
            self._compiled_patterns[pattern] = re.compile(pattern)
        return self._compiled_patterns[pattern]

    def validate(
        self,
        data: Dict[str, Any],
        schema_name: str,
        partial: bool = False,
    ) -> ValidationResult:
        """
        Validate data against a named schema.

        Args:
            data: Data to validate
            schema_name: Name of the schema
            partial: Allow partial data (skip required field checks)

        Returns:
            ValidationResult with issues
        """
        schema = self._schemas.get(schema_name)
        if not schema:
            result = ValidationResult(valid=False)
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.CONTRACT_VIOLATION,
                message=f"Unknown schema: {schema_name}",
                field="$schema",
            ))
            return result

        return self.validate_against_schema(data, schema, partial=partial)

    def validate_against_schema(
        self,
        data: Dict[str, Any],
        schema: ContractSchema,
        partial: bool = False,
        path: str = "",
    ) -> ValidationResult:
        """
        Validate data against a schema.

        Args:
            data: Data to validate
            schema: Schema to validate against
            partial: Allow partial data
            path: Current path for nested validation

        Returns:
            ValidationResult
        """
        result = ValidationResult(valid=True)

        if not isinstance(data, dict):
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.INVALID_TYPE,
                message=f"Expected object, got {type(data).__name__}",
                field=path or "$root",
                expected="object",
                actual=type(data).__name__,
            ))
            return result

        # Check required fields
        if not partial:
            for field_name, field_schema in schema.fields.items():
                if field_schema.required and field_name not in data:
                    result.add_issue(ValidationIssue(
                        code=ValidationErrorCode.MISSING_REQUIRED,
                        message=f"Missing required field: {field_name}",
                        field=f"{path}.{field_name}" if path else field_name,
                    ))

        # Check unknown fields in strict mode
        if schema.strict_mode and not schema.allow_extra_fields:
            known_fields = set(schema.fields.keys())
            for field_name in data.keys():
                if field_name not in known_fields:
                    result.add_issue(ValidationIssue(
                        code=ValidationErrorCode.UNKNOWN_FIELD,
                        message=f"Unknown field: {field_name}",
                        field=f"{path}.{field_name}" if path else field_name,
                        severity=ValidationSeverity.WARNING if not self.strict_mode else ValidationSeverity.ERROR,
                    ))

        # Validate each field
        for field_name, value in data.items():
            field_schema = schema.fields.get(field_name)
            if field_schema:
                field_path = f"{path}.{field_name}" if path else field_name
                field_result = self._validate_field(value, field_schema, field_path)
                result.merge(field_result)

                # Check for deprecated fields
                if field_schema.deprecated:
                    result.add_issue(ValidationIssue(
                        code=ValidationErrorCode.CONTRACT_VIOLATION,
                        message=field_schema.deprecation_message or f"Field {field_name} is deprecated",
                        field=field_path,
                        severity=ValidationSeverity.WARNING,
                    ))

        return result

    def _validate_field(
        self,
        value: Any,
        schema: FieldSchema,
        path: str,
    ) -> ValidationResult:
        """Validate a single field."""
        result = ValidationResult(valid=True)

        # Handle null values
        if value is None:
            if not schema.nullable and schema.required:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.INVALID_TYPE,
                    message=f"Field '{path}' cannot be null",
                    field=path,
                ))
            return result

        # Type check
        expected_type = schema.field_type
        if expected_type == object:
            pass  # Accept any type
        elif isinstance(expected_type, str):
            # Named type reference
            if expected_type == "string" and not isinstance(value, str):
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.INVALID_TYPE,
                    message=f"Expected string, got {type(value).__name__}",
                    field=path,
                    expected="string",
                    actual=type(value).__name__,
                ))
                return result
        elif expected_type == float:
            if not isinstance(value, (int, float)):
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.INVALID_TYPE,
                    message=f"Expected number, got {type(value).__name__}",
                    field=path,
                    expected="number",
                    actual=type(value).__name__,
                ))
                return result
        elif expected_type == int:
            if not isinstance(value, int) or isinstance(value, bool):
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.INVALID_TYPE,
                    message=f"Expected integer, got {type(value).__name__}",
                    field=path,
                    expected="integer",
                    actual=type(value).__name__,
                ))
                return result
        elif not isinstance(value, expected_type):
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.INVALID_TYPE,
                message=f"Expected {expected_type.__name__}, got {type(value).__name__}",
                field=path,
                expected=expected_type.__name__,
                actual=type(value).__name__,
            ))
            return result

        # String validations
        if isinstance(value, str):
            if schema.min_length is not None and len(value) < schema.min_length:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.STRING_TOO_SHORT,
                    message=f"String too short (min: {schema.min_length})",
                    field=path,
                    expected=schema.min_length,
                    actual=len(value),
                ))

            if schema.max_length is not None and len(value) > schema.max_length:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.STRING_TOO_LONG,
                    message=f"String too long (max: {schema.max_length})",
                    field=path,
                    expected=schema.max_length,
                    actual=len(value),
                ))

            if schema.pattern:
                pattern = self._get_pattern(schema.pattern)
                if not pattern.match(value):
                    result.add_issue(ValidationIssue(
                        code=ValidationErrorCode.INVALID_PATTERN,
                        message=f"Value does not match pattern: {schema.pattern}",
                        field=path,
                        expected=schema.pattern,
                        actual=value,
                    ))

        # Numeric validations
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if schema.min_value is not None and value < schema.min_value:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.VALUE_TOO_SMALL,
                    message=f"Value too small (min: {schema.min_value})",
                    field=path,
                    expected=schema.min_value,
                    actual=value,
                ))

            if schema.max_value is not None and value > schema.max_value:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.VALUE_TOO_LARGE,
                    message=f"Value too large (max: {schema.max_value})",
                    field=path,
                    expected=schema.max_value,
                    actual=value,
                ))

        # Enum validation
        if schema.enum_values is not None and value not in schema.enum_values:
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.INVALID_ENUM,
                message=f"Value not in allowed values: {schema.enum_values}",
                field=path,
                expected=schema.enum_values,
                actual=value,
            ))

        # Array validations
        if isinstance(value, list):
            if schema.min_length is not None and len(value) < schema.min_length:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.ARRAY_TOO_FEW,
                    message=f"Array too short (min: {schema.min_length})",
                    field=path,
                    expected=schema.min_length,
                    actual=len(value),
                ))

            if schema.max_length is not None and len(value) > schema.max_length:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.ARRAY_TOO_MANY,
                    message=f"Array too long (max: {schema.max_length})",
                    field=path,
                    expected=schema.max_length,
                    actual=len(value),
                ))

            # Validate array items
            if schema.item_schema:
                for i, item in enumerate(value):
                    item_result = self._validate_field(
                        item,
                        schema.item_schema,
                        f"{path}[{i}]",
                    )
                    result.merge(item_result)

        # Nested object validation
        if isinstance(value, dict) and schema.nested_schema:
            nested_result = self.validate_against_schema(
                value,
                schema.nested_schema,
                path=path,
            )
            result.merge(nested_result)

        # Custom validator
        if schema.validator and not schema.validator(value):
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.CONTRACT_VIOLATION,
                message=f"Custom validation failed",
                field=path,
                actual=value,
            ))

        return result

    def validate_response_envelope(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a response envelope structure."""
        result = self.validate(data, "ResponseEnvelope")

        # Additional envelope validations
        if result.valid and "meta" in data:
            meta = data["meta"]
            if "version" not in meta:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.MISSING_REQUIRED,
                    message="meta.version is required",
                    field="meta.version",
                ))
            if "timestamp" not in meta:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.MISSING_REQUIRED,
                    message="meta.timestamp is required",
                    field="meta.timestamp",
                ))

        return result

    def validate_version_compatibility(
        self,
        request_version: str,
        min_supported: str = "2.0.0",
    ) -> ValidationResult:
        """Validate API version compatibility."""
        result = ValidationResult(valid=True)

        # Parse versions
        try:
            req_parts = [int(p) for p in request_version.split(".")]
            min_parts = [int(p) for p in min_supported.split(".")]
        except (ValueError, AttributeError):
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.VERSION_MISMATCH,
                message=f"Invalid version format: {request_version}",
                field="version",
            ))
            return result

        # Compare major version
        if req_parts[0] < min_parts[0]:
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.VERSION_MISMATCH,
                message=f"Version {request_version} is not supported. Minimum: {min_supported}",
                field="version",
                expected=min_supported,
                actual=request_version,
            ))

        return result
