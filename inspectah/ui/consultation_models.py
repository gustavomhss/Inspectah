from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional, Sequence

try:  # pragma: no cover
    from pydantic import BaseModel, Field, validator
except ModuleNotFoundError:  # pragma: no cover
    BaseModel = None  # type: ignore[misc]
    Field = None  # type: ignore[misc]
    validator = None  # type: ignore[misc]


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ConsultationRequest(BaseModel):  # type: ignore[misc]
    question: str = Field(..., min_length=3, max_length=2000, description="Pergunta em linguagem natural")
    locale: Optional[str] = Field(default=None, description="Locale preferido pelo cliente (ex: pt-BR)")
    context: Optional[str] = Field(default=None, description="Contexto adicional fornecido pelo chamador")
    expected_risk: Optional[RiskLevel] = Field(default=None, description="Risco esperado pelo chamador, quando existir")

    @validator("question")  # type: ignore[misc]
    def _strip_and_validate(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("question must not be empty")
        return trimmed

    class Config:
        anystr_strip_whitespace = True


class ConsultationEvidence(BaseModel):  # type: ignore[misc]
    id: str = Field(..., description="Identificador estável ou derivado do Debunker")
    source_name: str = Field(..., description="Fonte ou origem principal da evidência")
    source_type: str = Field(..., description="Tipo da fonte (documento, noticia, dado, etc.)")
    description: str = Field(..., description="Resumo amigável da evidência")
    link: Optional[str] = Field(default=None, description="URL para consulta adicional, quando existir")
    credibility: Optional[str] = Field(default=None, description="Indicador qualitativo da credibilidade")
    stance: Optional[str] = Field(default=None, description="Posição da evidência (for/against/neutral)")
    score: Optional[float] = Field(default=None, description="Peso ou relevância atribuída pelo motor")


class ConfidenceSnapshot(BaseModel):  # type: ignore[misc]
    level: Optional[str] = Field(default=None)
    score: Optional[float] = Field(default=None)
    reasons: List[str] = Field(default_factory=list)


class SummaryCard(BaseModel):  # type: ignore[misc]
    risk_level: Optional[str] = Field(default=None)
    confidence_level: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None)
    limitations: List[str] = Field(default_factory=list)


class EvidenceContainer(BaseModel):  # type: ignore[misc]
    items_preview: List[ConsultationEvidence] = Field(default_factory=list)
    sources: List[ConsultationEvidence] = Field(default_factory=list)


class ConsultationResponse(BaseModel):  # type: ignore[misc]
    request_id: str = Field(..., description="ID único da consulta")
    answer: str = Field(..., description="Resposta consolidada e legível pela UI")
    risk_level: RiskLevel = Field(..., description="Nível de risco consolidado")
    risk_score: Optional[float] = Field(default=None, description="Score numérico do Debunker")
    risk_flags: List[str] = Field(default_factory=list, description="Flags de risco levantadas durante a análise")
    evidences: List[ConsultationEvidence] = Field(default_factory=list)
    evidence: Optional[EvidenceContainer] = Field(default=None, description="Campo auxiliar compatível com UI S17")
    confidence: Optional[ConfidenceSnapshot] = Field(default=None)
    answer_text: Optional[str] = Field(default=None, description="Alias para compatibilidade retro com UI")
    generated_at: Optional[str] = Field(default=None, description="Timestamp ISO8601 da geração da resposta")
    summary_card: Optional[SummaryCard] = Field(default=None)
    notes: Optional[str] = Field(default=None, description="Notas adicionais para UX")
    insufficient_data: bool = Field(default=False, description="True quando não há evidência suficiente")

    class Config:
        anystr_strip_whitespace = True


class ConsultationErrorResponse(BaseModel):  # type: ignore[misc]
    code: str = Field(..., description="Código de erro estável para a UI")
    message: str = Field(..., description="Mensagem amigável para exibição")
    request_id: Optional[str] = Field(default=None, description="ID correlacionado quando disponível")


@dataclass(slots=True)
class ConsultationResult:
    request_id: str
    answer: str
    risk_level: RiskLevel
    evidences: Sequence[ConsultationEvidence] = field(default_factory=tuple)
    risk_score: Optional[float] = None
    risk_flags: Sequence[str] = field(default_factory=tuple)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: Optional[ConfidenceSnapshot] = None
    summary_card: Optional[SummaryCard] = None
    notes: Optional[str] = None
    insufficient_data: bool = False

    def to_response(self) -> ConsultationResponse:
        evidence_list = list(self.evidences)
        evidence_container = EvidenceContainer(items_preview=evidence_list, sources=[])
        generated_at = self.generated_at.isoformat().replace("+00:00", "Z")
        return ConsultationResponse(
            request_id=self.request_id,
            answer=self.answer,
            answer_text=self.answer,
            risk_level=self.risk_level,
            risk_score=self.risk_score,
            risk_flags=list(self.risk_flags),
            evidences=evidence_list,
            evidence=evidence_container,
            confidence=self.confidence,
            generated_at=generated_at,
            summary_card=self.summary_card,
            notes=self.notes,
            insufficient_data=self.insufficient_data,
        )


class ConsultationInternalError(RuntimeError):
    def __init__(self, message: str, *, code: str = "internal_error"):
        super().__init__(message)
        self.code = code
        self.message = message

    def to_error_response(self, request_id: Optional[str] = None) -> ConsultationErrorResponse:
        return ConsultationErrorResponse(code=self.code, message=self.message, request_id=request_id)
