"""
Sprint 40: Validadores fail-closed para Truth-DB.

Task: S40-BE-001
Invariantes implementados:
- INV-DB-01: DecisionBlock sem references.guias[] é inválido
- INV-DB-02: DecisionBlock sem references.e40_5 é inválido
- INV-DB-03: DecisionBlock sem state_transition é inválido
- INV-DB-04: DecisionBlock sem references.pilares[] é inválido
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# Estados válidos para transições
VALID_STATES = frozenset([
    "UNKNOWN",
    "CLAIMED",
    "UNDER_REVIEW",
    "PROVISIONAL",
    "ESTABLISHED_FACT",
    "UNDER_DISPUTE",
    "RETRACTED",
    "BLOCKED",
    "DEGRADED",
])

# Status válidos para E40.5
VALID_E40_5_STATUS = frozenset(["PASS", "FAIL", "SKIP", "TIMEOUT", "DEGRADED"])


class ValidationErrorCode(str, Enum):
    """Códigos de erro de validação."""

    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    EMPTY_ARRAY = "EMPTY_ARRAY"
    INVALID_STATE = "INVALID_STATE"
    INVALID_E40_5_STATUS = "INVALID_E40_5_STATUS"
    MISSING_REASON = "MISSING_REASON"
    INVALID_TYPE = "INVALID_TYPE"


@dataclass
class ValidationError(Exception):
    """Erro de validação fail-closed."""

    code: ValidationErrorCode
    field: str
    message: str
    invariant: str | None = None

    def __str__(self) -> str:
        inv = f" [{self.invariant}]" if self.invariant else ""
        return f"{self.code.value}: {self.field} - {self.message}{inv}"


@dataclass
class ValidationResult:
    """Resultado da validação."""

    valid: bool
    errors: list[ValidationError]

    @property
    def error_messages(self) -> list[str]:
        """Retorna lista de mensagens de erro."""
        return [str(e) for e in self.errors]


def validate_decision_block(data: dict[str, Any]) -> ValidationResult:
    """
    Valida um DecisionBlock conforme invariantes S40.

    Validação fail-closed: qualquer violação retorna ValidationError.

    Args:
        data: Dict com dados do DecisionBlock

    Returns:
        ValidationResult com status e erros

    Raises:
        ValidationError: Se a validação falhar em modo strict
    """
    errors: list[ValidationError] = []

    # Campos obrigatórios de primeiro nível
    required_fields = [
        "claim_id",
        "domain",
        "gate",
        "state_transition",
        "references",
        "policy_version",
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field=field,
                    message=f"Campo obrigatório '{field}' ausente",
                )
            )

    # Se campos básicos faltam, retorna cedo
    if errors:
        return ValidationResult(valid=False, errors=errors)

    # INV-DB-03: Validar state_transition
    state_transition = data.get("state_transition", {})
    if not isinstance(state_transition, dict):
        errors.append(
            ValidationError(
                code=ValidationErrorCode.INVALID_TYPE,
                field="state_transition",
                message="state_transition deve ser um objeto",
                invariant="INV-DB-03",
            )
        )
    else:
        # Verificar from_state
        from_state = state_transition.get("from_state")
        if not from_state:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field="state_transition.from_state",
                    message="from_state é obrigatório",
                    invariant="INV-DB-03",
                )
            )
        elif from_state not in VALID_STATES:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.INVALID_STATE,
                    field="state_transition.from_state",
                    message=f"Estado inválido: {from_state}",
                    invariant="INV-DB-03",
                )
            )

        # Verificar to_state
        to_state = state_transition.get("to_state")
        if not to_state:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field="state_transition.to_state",
                    message="to_state é obrigatório",
                    invariant="INV-DB-03",
                )
            )
        elif to_state not in VALID_STATES:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.INVALID_STATE,
                    field="state_transition.to_state",
                    message=f"Estado inválido: {to_state}",
                    invariant="INV-DB-03",
                )
            )

        # Verificar reason
        reason = state_transition.get("reason")
        if not reason or not str(reason).strip():
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.MISSING_REASON,
                    field="state_transition.reason",
                    message="Razão da transição é obrigatória",
                    invariant="INV-DB-03",
                )
            )

    # Validar references
    references = data.get("references", {})
    if not isinstance(references, dict):
        errors.append(
            ValidationError(
                code=ValidationErrorCode.INVALID_TYPE,
                field="references",
                message="references deve ser um objeto",
            )
        )
    else:
        # INV-DB-01: references.guias[] não pode ser vazio
        guias = references.get("guias", [])
        if not isinstance(guias, list) or len(guias) == 0:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.EMPTY_ARRAY,
                    field="references.guias",
                    message="references.guias[] é obrigatório e não pode ser vazio",
                    invariant="INV-DB-01",
                )
            )
        else:
            # Validar cada guia tem campos mínimos
            for i, guia in enumerate(guias):
                if not isinstance(guia, dict):
                    errors.append(
                        ValidationError(
                            code=ValidationErrorCode.INVALID_TYPE,
                            field=f"references.guias[{i}]",
                            message="Cada guia deve ser um objeto",
                            invariant="INV-DB-01",
                        )
                    )
                elif not guia.get("guia") or not guia.get("documento"):
                    errors.append(
                        ValidationError(
                            code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                            field=f"references.guias[{i}]",
                            message="Cada guia deve ter 'guia' e 'documento'",
                            invariant="INV-DB-01",
                        )
                    )

        # INV-DB-04: references.pilares[] não pode ser vazio
        pilares = references.get("pilares", [])
        if not isinstance(pilares, list) or len(pilares) == 0:
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.EMPTY_ARRAY,
                    field="references.pilares",
                    message="references.pilares[] é obrigatório e não pode ser vazio",
                    invariant="INV-DB-04",
                )
            )
        else:
            # Validar cada pilar
            for i, pilar in enumerate(pilares):
                if not isinstance(pilar, dict):
                    errors.append(
                        ValidationError(
                            code=ValidationErrorCode.INVALID_TYPE,
                            field=f"references.pilares[{i}]",
                            message="Cada pilar deve ser um objeto",
                            invariant="INV-DB-04",
                        )
                    )
                elif not pilar.get("pilar") or not pilar.get("documento"):
                    errors.append(
                        ValidationError(
                            code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                            field=f"references.pilares[{i}]",
                            message="Cada pilar deve ter 'pilar' e 'documento'",
                            invariant="INV-DB-04",
                        )
                    )

        # INV-DB-02: references.e40_5 é obrigatório
        e40_5 = references.get("e40_5")
        if not e40_5 or not isinstance(e40_5, dict):
            errors.append(
                ValidationError(
                    code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                    field="references.e40_5",
                    message="references.e40_5 é obrigatório",
                    invariant="INV-DB-02",
                )
            )
        else:
            # Verificar status
            status = e40_5.get("status")
            if not status:
                errors.append(
                    ValidationError(
                        code=ValidationErrorCode.MISSING_REQUIRED_FIELD,
                        field="references.e40_5.status",
                        message="references.e40_5.status é obrigatório",
                        invariant="INV-DB-02",
                    )
                )
            elif status not in VALID_E40_5_STATUS:
                errors.append(
                    ValidationError(
                        code=ValidationErrorCode.INVALID_E40_5_STATUS,
                        field="references.e40_5.status",
                        message=f"Status E40.5 inválido: {status}",
                        invariant="INV-DB-02",
                    )
                )

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_decision_block_strict(data: dict[str, Any]) -> None:
    """
    Valida DecisionBlock em modo strict (raise on error).

    Args:
        data: Dict com dados do DecisionBlock

    Raises:
        ValidationError: Se qualquer invariante for violado
    """
    result = validate_decision_block(data)
    if not result.valid:
        # Retorna o primeiro erro
        raise result.errors[0]


def is_valid_decision_block(data: dict[str, Any]) -> bool:
    """
    Verifica se DecisionBlock é válido (modo boolean).

    Args:
        data: Dict com dados do DecisionBlock

    Returns:
        True se válido, False caso contrário
    """
    return validate_decision_block(data).valid
