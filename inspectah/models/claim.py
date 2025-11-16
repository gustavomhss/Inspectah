"""Claim model aligned with schemas/inspectah_claim_v0_1.json."""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional, Union

ClaimValue = Union[str, float, int]


@dataclass(slots=True)
class Claim:
    """Dataclass que representa um claim do Inspectah."""

    CLAIM_TYPES: ClassVar[tuple[str, ...]] = (
        "resultado_binario",
        "resultado_numerico",
        "estado_evento",
        "data_evento",
        "classificacao",
    )
    POLARITY: ClassVar[tuple[str, ...]] = (
        "afirma_que_e_verdade",
        "afirma_que_e_falso",
        "informa_sem_julgar",
        "indeterminado",
    )
    LOCAL_VERDICT: ClassVar[tuple[str, ...]] = (
        "segundo_esta_fonte_este_e_o_valor",
        "segundo_esta_fonte_isto_ocorreu",
        "segundo_esta_fonte_isto_nao_ocorreu",
        "segundo_esta_fonte_ainda_esta_pendente",
        "nao_ha_veredito_claro",
    )

    claim_id: str
    claim_type: str
    declared_metric: str
    declared_value: ClaimValue
    declared_subject: Optional[str] = None
    declared_unit: Optional[str] = None
    polarity: str = "informa_sem_julgar"
    local_verdict: str = "nao_ha_veredito_claro"
    confidence_claim: float = 0.0

    def __post_init__(self) -> None:
        self._validate_enum("claim_type", self.claim_type, self.CLAIM_TYPES)
        self._validate_enum("polarity", self.polarity, self.POLARITY)
        self._validate_enum("local_verdict", self.local_verdict, self.LOCAL_VERDICT)
        if not 0.0 <= float(self.confidence_claim) <= 1.0:
            raise ValueError("confidence_claim deve estar entre 0 e 1")
        if not self.claim_id:
            raise ValueError("claim_id obrigatório")
        if not self.declared_metric:
            raise ValueError("declared_metric obrigatório")

    @staticmethod
    def _validate_enum(field: str, value: str, allowed: tuple[str, ...]) -> None:
        if value not in allowed:
            raise ValueError(f"{field} inválido: {value}")

    def to_dict(self) -> dict:
        """Representação serializável do claim."""
        return {
            "claim_id": self.claim_id,
            "claim_type": self.claim_type,
            "declared_metric": self.declared_metric,
            "declared_subject": self.declared_subject,
            "declared_value": self.declared_value,
            "declared_unit": self.declared_unit,
            "polarity": self.polarity,
            "local_verdict": self.local_verdict,
            "confidence_claim": float(self.confidence_claim),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Claim":
        """Cria um Claim a partir de um dicionário validado."""
        return cls(
            claim_id=data["claim_id"],
            claim_type=data["claim_type"],
            declared_metric=data["declared_metric"],
            declared_subject=data.get("declared_subject"),
            declared_value=data["declared_value"],
            declared_unit=data.get("declared_unit"),
            polarity=data.get("polarity", "informa_sem_julgar"),
            local_verdict=data.get("local_verdict", "nao_ha_veredito_claro"),
            confidence_claim=float(data.get("confidence_claim", 0.0)),
        )
