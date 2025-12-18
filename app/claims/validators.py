"""
Sprint 40: Validadores fail-closed para Claims.

Task: S40-BE-002
Invariantes implementados:
- INV-CLAIM-01: Claim sem prior ou evidence_trail[] é inválida
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


# Estados válidos para claims
VALID_CLAIM_STATES = frozenset([
    "UNKNOWN",
    "CLAIMED",
    "UNDER_REVIEW",
    "PROVISIONAL",
    "ESTABLISHED_FACT",
    "UNDER_DISPUTE",
    "RETRACTED",
])

# Tipos válidos de evidência
VALID_EVIDENCE_TYPES = frozenset([
    "source",
    "fact_check",
    "expert_opinion",
    "official_data",
    "user_report",
    "contradiction",
    "support",
])

# Stances válidos para evidência
VALID_EVIDENCE_STANCES = frozenset([
    "supports",
    "refutes",
    "neutral",
    "unclear",
])

# Fontes válidas de prior
VALID_PRIOR_SOURCES = frozenset([
    "model",
    "expert",
    "crowd",
    "official",
    "hybrid",
])


class ClaimValidationErrorCode(str, Enum):
    """Códigos de erro de validação de claim."""

    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    MISSING_PRIOR = "MISSING_PRIOR"
    MISSING_EVIDENCE_TRAIL = "MISSING_EVIDENCE_TRAIL"
    INVALID_PRIOR = "INVALID_PRIOR"
    INVALID_EVIDENCE = "INVALID_EVIDENCE"
    INVALID_STATE = "INVALID_STATE"
    INVALID_TYPE = "INVALID_TYPE"
    OUT_OF_RANGE = "OUT_OF_RANGE"


@dataclass
class ClaimValidationError(Exception):
    """Erro de validação de claim fail-closed."""

    code: ClaimValidationErrorCode
    field: str
    message: str
    invariant: str | None = None

    def __str__(self) -> str:
        inv = f" [{self.invariant}]" if self.invariant else ""
        return f"{self.code.value}: {self.field} - {self.message}{inv}"


@dataclass
class ClaimValidationResult:
    """Resultado da validação de claim."""

    valid: bool
    errors: list[ClaimValidationError]

    @property
    def error_messages(self) -> list[str]:
        """Retorna lista de mensagens de erro."""
        return [str(e) for e in self.errors]


def validate_prior(prior: dict[str, Any], field_prefix: str = "prior") -> list[ClaimValidationError]:
    """
    Valida objeto prior de um claim.

    Args:
        prior: Dict com dados do prior
        field_prefix: Prefixo do campo para mensagens de erro

    Returns:
        Lista de erros encontrados
    """
    errors: list[ClaimValidationError] = []

    if not isinstance(prior, dict):
        errors.append(
            ClaimValidationError(
                code=ClaimValidationErrorCode.INVALID_TYPE,
                field=field_prefix,
                message="prior deve ser um objeto",
                invariant="INV-CLAIM-01",
            )
        )
        return errors

    # Campos obrigatórios do prior
    required_prior_fields = ["probability", "confidence", "source"]
    for field in required_prior_fields:
        if field not in prior or prior[field] is None:
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field=f"{field_prefix}.{field}",
                    message=f"Campo '{field}' é obrigatório no prior",
                    invariant="INV-CLAIM-01",
                )
            )

    # Validar probability (0-1)
    prob = prior.get("probability")
    if prob is not None:
        if not isinstance(prob, (int, float)):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.INVALID_TYPE,
                    field=f"{field_prefix}.probability",
                    message="probability deve ser um número",
                    invariant="INV-CLAIM-01",
                )
            )
        elif not 0 <= prob <= 1:
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.OUT_OF_RANGE,
                    field=f"{field_prefix}.probability",
                    message="probability deve estar entre 0 e 1",
                    invariant="INV-CLAIM-01",
                )
            )

    # Validar confidence (0-1)
    conf = prior.get("confidence")
    if conf is not None:
        if not isinstance(conf, (int, float)):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.INVALID_TYPE,
                    field=f"{field_prefix}.confidence",
                    message="confidence deve ser um número",
                    invariant="INV-CLAIM-01",
                )
            )
        elif not 0 <= conf <= 1:
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.OUT_OF_RANGE,
                    field=f"{field_prefix}.confidence",
                    message="confidence deve estar entre 0 e 1",
                    invariant="INV-CLAIM-01",
                )
            )

    # Validar source
    source = prior.get("source")
    if source is not None and source not in VALID_PRIOR_SOURCES:
        errors.append(
            ClaimValidationError(
                code=ClaimValidationErrorCode.INVALID_PRIOR,
                field=f"{field_prefix}.source",
                message=f"source inválido: {source}. Válidos: {VALID_PRIOR_SOURCES}",
                invariant="INV-CLAIM-01",
            )
        )

    return errors


def validate_evidence_trail(
    evidence_trail: list[dict[str, Any]], field_prefix: str = "evidence_trail"
) -> list[ClaimValidationError]:
    """
    Valida evidence_trail de um claim.

    Args:
        evidence_trail: Lista de evidências
        field_prefix: Prefixo do campo para mensagens de erro

    Returns:
        Lista de erros encontrados
    """
    errors: list[ClaimValidationError] = []

    if not isinstance(evidence_trail, list):
        errors.append(
            ClaimValidationError(
                code=ClaimValidationErrorCode.INVALID_TYPE,
                field=field_prefix,
                message="evidence_trail deve ser uma lista",
                invariant="INV-CLAIM-01",
            )
        )
        return errors

    # evidence_trail pode ser vazio, mas se tiver itens, devem ser válidos
    for i, evidence in enumerate(evidence_trail):
        if not isinstance(evidence, dict):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.INVALID_TYPE,
                    field=f"{field_prefix}[{i}]",
                    message="Cada evidência deve ser um objeto",
                    invariant="INV-CLAIM-01",
                )
            )
            continue

        # Campos obrigatórios
        if not evidence.get("evidence_id"):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field=f"{field_prefix}[{i}].evidence_id",
                    message="evidence_id é obrigatório",
                    invariant="INV-CLAIM-01",
                )
            )

        if not evidence.get("type"):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field=f"{field_prefix}[{i}].type",
                    message="type é obrigatório",
                    invariant="INV-CLAIM-01",
                )
            )
        elif evidence.get("type") not in VALID_EVIDENCE_TYPES:
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.INVALID_EVIDENCE,
                    field=f"{field_prefix}[{i}].type",
                    message=f"type inválido: {evidence.get('type')}",
                    invariant="INV-CLAIM-01",
                )
            )

        if not evidence.get("stance"):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field=f"{field_prefix}[{i}].stance",
                    message="stance é obrigatório",
                    invariant="INV-CLAIM-01",
                )
            )
        elif evidence.get("stance") not in VALID_EVIDENCE_STANCES:
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.INVALID_EVIDENCE,
                    field=f"{field_prefix}[{i}].stance",
                    message=f"stance inválido: {evidence.get('stance')}",
                    invariant="INV-CLAIM-01",
                )
            )

        # Validar weight se presente
        weight = evidence.get("weight")
        if weight is not None:
            if not isinstance(weight, (int, float)):
                errors.append(
                    ClaimValidationError(
                        code=ClaimValidationErrorCode.INVALID_TYPE,
                        field=f"{field_prefix}[{i}].weight",
                        message="weight deve ser um número",
                        invariant="INV-CLAIM-01",
                    )
                )
            elif not 0 <= weight <= 1:
                errors.append(
                    ClaimValidationError(
                        code=ClaimValidationErrorCode.OUT_OF_RANGE,
                        field=f"{field_prefix}[{i}].weight",
                        message="weight deve estar entre 0 e 1",
                        invariant="INV-CLAIM-01",
                    )
                )

    return errors


def validate_claim(data: dict[str, Any]) -> ClaimValidationResult:
    """
    Valida um Claim conforme invariantes S40.

    Validação fail-closed para claims que serão exportados para P3.

    Args:
        data: Dict com dados do claim

    Returns:
        ClaimValidationResult com status e erros
    """
    errors: list[ClaimValidationError] = []

    # Campos obrigatórios básicos
    required_fields = ["claim_id", "text", "current_state"]
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field=field,
                    message=f"Campo obrigatório '{field}' ausente",
                )
            )

    # Validar current_state
    current_state = data.get("current_state")
    if current_state and current_state not in VALID_CLAIM_STATES:
        errors.append(
            ClaimValidationError(
                code=ClaimValidationErrorCode.INVALID_STATE,
                field="current_state",
                message=f"Estado inválido: {current_state}",
            )
        )

    # INV-CLAIM-01: prior é obrigatório
    prior = data.get("prior")
    if prior is None:
        errors.append(
            ClaimValidationError(
                code=ClaimValidationErrorCode.MISSING_PRIOR,
                field="prior",
                message="prior é obrigatório para claims exportáveis",
                invariant="INV-CLAIM-01",
            )
        )
    else:
        errors.extend(validate_prior(prior))

    # INV-CLAIM-01: evidence_trail é obrigatório (pode ser lista vazia)
    evidence_trail = data.get("evidence_trail")
    if evidence_trail is None:
        errors.append(
            ClaimValidationError(
                code=ClaimValidationErrorCode.MISSING_EVIDENCE_TRAIL,
                field="evidence_trail",
                message="evidence_trail é obrigatório para claims exportáveis",
                invariant="INV-CLAIM-01",
            )
        )
    else:
        errors.extend(validate_evidence_trail(evidence_trail))

    return ClaimValidationResult(valid=len(errors) == 0, errors=errors)


def validate_claim_strict(data: dict[str, Any]) -> None:
    """
    Valida Claim em modo strict (raise on error).

    Args:
        data: Dict com dados do claim

    Raises:
        ClaimValidationError: Se qualquer invariante for violado
    """
    result = validate_claim(data)
    if not result.valid:
        raise result.errors[0]


def is_valid_claim(data: dict[str, Any]) -> bool:
    """
    Verifica se Claim é válido (modo boolean).

    Args:
        data: Dict com dados do claim

    Returns:
        True se válido, False caso contrário
    """
    return validate_claim(data).valid


def validate_claim_for_export(data: dict[str, Any]) -> ClaimValidationResult:
    """
    Valida claim especificamente para export P2→P3.

    Aplica validações adicionais para garantir que o claim
    pode ser ingerido pelo Truth-DB sem adaptação manual.

    Args:
        data: Dict com dados do claim

    Returns:
        ClaimValidationResult com status e erros
    """
    # Primeiro, validação básica
    result = validate_claim(data)
    errors = list(result.errors)

    # Validações adicionais para export
    if result.valid:
        # Verificar que prior tem computed_at
        prior = data.get("prior", {})
        if not prior.get("computed_at"):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field="prior.computed_at",
                    message="prior.computed_at é recomendado para export",
                )
            )

        # Verificar created_at
        if not data.get("created_at"):
            errors.append(
                ClaimValidationError(
                    code=ClaimValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field="created_at",
                    message="created_at é obrigatório para export",
                )
            )

    return ClaimValidationResult(valid=len(errors) == 0, errors=errors)
