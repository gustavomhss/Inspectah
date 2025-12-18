"""
S38-BE-051: API Contracts v1 + S39-BE-023/024: Contracts v2

Definicoes de contratos de API do sistema Inspectah.
"""

from app.contracts.v1 import (
    ClaimContract,
    SourceContract,
    SignalContract,
    PolicyContract,
    VerdictContract,
    RelationContract,
    ErrorContract,
    PaginationContract,
    ResponseEnvelope,
    ContractStatus,
    ContractValidator,
    CONTRACT_VERSION,
    success_response,
    error_response,
    partial_response,
)

# S39 - Strict Contract Validator
from app.contracts.validator import (
    StrictContractValidator,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    ValidationErrorCode,
    FieldSchema,
    ContractSchema,
)

# S39 - Contract Middleware
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

# S39 - Semver Enforcement
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

__all__ = [
    # V1 Contracts
    "ClaimContract",
    "SourceContract",
    "SignalContract",
    "PolicyContract",
    "VerdictContract",
    "RelationContract",
    "ErrorContract",
    "PaginationContract",
    "ResponseEnvelope",
    "ContractStatus",
    "ContractValidator",
    "CONTRACT_VERSION",
    "success_response",
    "error_response",
    "partial_response",
    # Strict Validator
    "StrictContractValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ValidationErrorCode",
    "FieldSchema",
    "ContractSchema",
    # Middleware
    "ContractMiddleware",
    "ContractValidationError",
    "VersionNegotiator",
    "validate_request_contract",
    "validate_response_contract",
    "get_validator",
    "get_middleware",
    "get_negotiator",
    # Semver
    "SemVer",
    "VersionRange",
    "VersionedContract",
    "SemverEnforcer",
    "VersionChangeType",
    "CompatibilityLevel",
    "parse_version",
    "is_compatible",
    "get_enforcer",
]
