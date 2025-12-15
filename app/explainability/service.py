"""
S38-BE-052: Explainability Service

Servico para explicar decisoes do sistema de forma compreensivel.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ExplanationType(str, Enum):
    """Tipos de explicacao."""
    VERDICT = "verdict"           # Explicacao de veredicto
    SIGNAL = "signal"             # Explicacao de sinal
    RELATION = "relation"         # Explicacao de relacao
    POLICY = "policy"             # Explicacao de policy
    RECOMMENDATION = "recommendation"  # Explicacao de recomendacao
    ALERT = "alert"               # Explicacao de alerta


class ExplanationLevel(str, Enum):
    """Nivel de detalhe da explicacao."""
    SIMPLE = "simple"       # Para usuarios finais
    DETAILED = "detailed"   # Para analistas
    TECHNICAL = "technical"  # Para desenvolvedores


class FactorType(str, Enum):
    """Tipos de fatores que influenciam decisoes."""
    EVIDENCE = "evidence"       # Evidencias encontradas
    SOURCE = "source"           # Credibilidade de fontes
    CONFIDENCE = "confidence"   # Nivel de confianca
    POLICY = "policy"           # Regras de policy
    RELATION = "relation"       # Relacoes entre claims
    SIGNAL = "signal"           # Sinais de mercado
    TEMPORAL = "temporal"       # Fatores temporais
    ENTITY = "entity"           # Entidades envolvidas
    CONTRADICTION = "contradiction"  # Contradicoes
    SUPPORT = "support"         # Suportes


class ImpactDirection(str, Enum):
    """Direcao do impacto de um fator."""
    POSITIVE = "positive"   # Aumenta confianca
    NEGATIVE = "negative"   # Diminui confianca
    NEUTRAL = "neutral"     # Sem impacto direto


@dataclass
class Factor:
    """Fator que influencia uma decisao."""
    factor_id: str
    factor_type: FactorType
    name: str
    description: str
    weight: float  # 0.0 a 1.0
    value: float   # Valor do fator
    impact: ImpactDirection
    evidence: Optional[str] = None
    source_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "type": self.factor_type.value,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "value": self.value,
            "impact": self.impact.value,
            "evidence": self.evidence,
            "source_ref": self.source_ref,
        }

    def contribution_score(self) -> float:
        """Calcula contribuicao do fator."""
        multiplier = 1.0 if self.impact == ImpactDirection.POSITIVE else -1.0
        if self.impact == ImpactDirection.NEUTRAL:
            multiplier = 0.0
        return self.weight * self.value * multiplier


@dataclass
class DecisionExplanation:
    """Explicacao de uma decisao."""
    explanation_id: str
    explanation_type: ExplanationType
    target_id: str  # ID do objeto explicado
    decision: str   # Decisao tomada
    confidence: float
    summary: str    # Resumo em linguagem natural
    factors: List[Factor]
    level: ExplanationLevel
    generated_at: datetime
    reasoning_chain: List[str] = field(default_factory=list)
    alternatives_considered: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "type": self.explanation_type.value,
            "target_id": self.target_id,
            "decision": self.decision,
            "confidence": self.confidence,
            "summary": self.summary,
            "factors": [f.to_dict() for f in self.factors],
            "level": self.level.value,
            "generated_at": self.generated_at.isoformat(),
            "reasoning_chain": self.reasoning_chain,
            "alternatives_considered": self.alternatives_considered,
        }

    def get_top_factors(self, n: int = 5) -> List[Factor]:
        """Retorna os N fatores mais importantes."""
        sorted_factors = sorted(
            self.factors,
            key=lambda f: abs(f.contribution_score()),
            reverse=True,
        )
        return sorted_factors[:n]

    def get_positive_factors(self) -> List[Factor]:
        """Retorna fatores positivos."""
        return [f for f in self.factors if f.impact == ImpactDirection.POSITIVE]

    def get_negative_factors(self) -> List[Factor]:
        """Retorna fatores negativos."""
        return [f for f in self.factors if f.impact == ImpactDirection.NEGATIVE]


class ExplanationTemplate:
    """Template para geracao de explicacoes."""

    def __init__(
        self,
        explanation_type: ExplanationType,
        templates: Dict[ExplanationLevel, str],
    ):
        self.explanation_type = explanation_type
        self.templates = templates

    def render(
        self,
        level: ExplanationLevel,
        context: Dict[str, Any],
    ) -> str:
        """Renderiza template com contexto."""
        template = self.templates.get(level, self.templates.get(ExplanationLevel.SIMPLE, ""))
        try:
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing template key: {e}")
            return template


# Templates padrao
VERDICT_TEMPLATES = ExplanationTemplate(
    ExplanationType.VERDICT,
    {
        ExplanationLevel.SIMPLE: (
            "O claim '{claim_text}' foi classificado como {verdict} "
            "com {confidence:.0%} de confianca. "
            "{main_reason}"
        ),
        ExplanationLevel.DETAILED: (
            "Veredicto: {verdict} (confianca: {confidence:.1%})\n"
            "Claim: {claim_text}\n\n"
            "Fatores principais:\n{factors_summary}\n\n"
            "Fontes consultadas: {sources_count}\n"
            "Evidencias analisadas: {evidence_count}"
        ),
        ExplanationLevel.TECHNICAL: (
            "Decision ID: {explanation_id}\n"
            "Target: {target_id}\n"
            "Verdict: {verdict}\n"
            "Confidence: {confidence}\n\n"
            "Factor Analysis:\n{factors_detail}\n\n"
            "Reasoning Chain:\n{reasoning}\n\n"
            "Alternatives:\n{alternatives}"
        ),
    }
)


SIGNAL_TEMPLATES = ExplanationTemplate(
    ExplanationType.SIGNAL,
    {
        ExplanationLevel.SIMPLE: (
            "O sinal '{signal_type}' esta em nivel {level} ({value:.0%}). "
            "{main_reason}"
        ),
        ExplanationLevel.DETAILED: (
            "Sinal: {signal_type}\n"
            "Valor: {value:.2f} | Nivel: {level}\n"
            "Escopo: {scope}\n\n"
            "Componentes:\n{factors_summary}"
        ),
    }
)


class ExplainabilityService:
    """
    Servico de explicabilidade.

    Gera explicacoes compreensiveis para decisoes do sistema.

    Uso:
        service = ExplainabilityService()

        # Explicar veredicto
        explanation = service.explain_verdict(
            claim_id="claim_123",
            verdict="FALSO",
            confidence=0.85,
            factors=[...],
        )

        # Obter explicacao simples
        simple = service.get_explanation(
            explanation.explanation_id,
            level=ExplanationLevel.SIMPLE,
        )
    """

    def __init__(self):
        self._explanations: Dict[str, DecisionExplanation] = {}
        self._templates: Dict[ExplanationType, ExplanationTemplate] = {
            ExplanationType.VERDICT: VERDICT_TEMPLATES,
            ExplanationType.SIGNAL: SIGNAL_TEMPLATES,
        }
        self._factor_generators: Dict[str, Callable[..., List[Factor]]] = {}

    def register_template(
        self,
        explanation_type: ExplanationType,
        template: ExplanationTemplate,
    ) -> None:
        """Registra template customizado."""
        self._templates[explanation_type] = template

    def register_factor_generator(
        self,
        name: str,
        generator: Callable[..., List[Factor]],
    ) -> None:
        """Registra gerador de fatores."""
        self._factor_generators[name] = generator

    def explain_verdict(
        self,
        claim_id: str,
        claim_text: str,
        verdict: str,
        confidence: float,
        factors: List[Factor],
        sources_count: int = 0,
        evidence_count: int = 0,
        reasoning_chain: Optional[List[str]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> DecisionExplanation:
        """
        Gera explicacao para veredicto de claim.

        Args:
            claim_id: ID do claim
            claim_text: Texto do claim
            verdict: Veredicto (VERDADEIRO, FALSO, etc)
            confidence: Confianca na decisao
            factors: Lista de fatores que influenciaram
            sources_count: Numero de fontes consultadas
            evidence_count: Numero de evidencias
            reasoning_chain: Cadeia de raciocinio
            alternatives: Alternativas consideradas

        Returns:
            Explicacao completa
        """
        # Gerar resumo baseado em fatores
        top_factor = max(factors, key=lambda f: abs(f.contribution_score())) if factors else None
        main_reason = top_factor.description if top_factor else "Decisao baseada na analise de evidencias."

        # Criar explicacao
        explanation = DecisionExplanation(
            explanation_id=f"exp_{uuid4().hex[:12]}",
            explanation_type=ExplanationType.VERDICT,
            target_id=claim_id,
            decision=verdict,
            confidence=confidence,
            summary=self._render_summary(
                ExplanationType.VERDICT,
                ExplanationLevel.SIMPLE,
                {
                    "claim_text": claim_text[:100] + "..." if len(claim_text) > 100 else claim_text,
                    "verdict": verdict,
                    "confidence": confidence,
                    "main_reason": main_reason,
                }
            ),
            factors=factors,
            level=ExplanationLevel.DETAILED,
            generated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            reasoning_chain=reasoning_chain or [],
            alternatives_considered=alternatives or [],
            metadata={
                "claim_text": claim_text,
                "sources_count": sources_count,
                "evidence_count": evidence_count,
            }
        )

        self._explanations[explanation.explanation_id] = explanation
        return explanation

    def explain_signal(
        self,
        signal_type: str,
        value: float,
        level: str,
        scope: str,
        scope_id: Optional[str],
        factors: List[Factor],
    ) -> DecisionExplanation:
        """Gera explicacao para valor de sinal."""
        main_reason = self._summarize_signal_factors(factors)

        explanation = DecisionExplanation(
            explanation_id=f"exp_{uuid4().hex[:12]}",
            explanation_type=ExplanationType.SIGNAL,
            target_id=f"{signal_type}:{scope}:{scope_id or 'global'}",
            decision=level,
            confidence=value,
            summary=self._render_summary(
                ExplanationType.SIGNAL,
                ExplanationLevel.SIMPLE,
                {
                    "signal_type": signal_type,
                    "value": value,
                    "level": level,
                    "main_reason": main_reason,
                }
            ),
            factors=factors,
            level=ExplanationLevel.DETAILED,
            generated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            metadata={"scope": scope, "scope_id": scope_id},
        )

        self._explanations[explanation.explanation_id] = explanation
        return explanation

    def explain_relation(
        self,
        source_claim_id: str,
        target_claim_id: str,
        relation_type: str,
        confidence: float,
        factors: List[Factor],
    ) -> DecisionExplanation:
        """Gera explicacao para relacao entre claims."""
        explanation = DecisionExplanation(
            explanation_id=f"exp_{uuid4().hex[:12]}",
            explanation_type=ExplanationType.RELATION,
            target_id=f"{source_claim_id}:{target_claim_id}",
            decision=relation_type,
            confidence=confidence,
            summary=f"Relacao '{relation_type}' detectada com {confidence:.0%} de confianca.",
            factors=factors,
            level=ExplanationLevel.DETAILED,
            generated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            metadata={
                "source_claim_id": source_claim_id,
                "target_claim_id": target_claim_id,
            },
        )

        self._explanations[explanation.explanation_id] = explanation
        return explanation

    def get_explanation(
        self,
        explanation_id: str,
        level: Optional[ExplanationLevel] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Recupera explicacao por ID.

        Se level especificado, renderiza no nivel apropriado.
        """
        explanation = self._explanations.get(explanation_id)
        if not explanation:
            return None

        result = explanation.to_dict()

        if level:
            result["summary"] = self._render_for_level(explanation, level)

        return result

    def get_explanations_for_target(
        self,
        target_id: str,
    ) -> List[DecisionExplanation]:
        """Retorna explicacoes para um alvo."""
        return [
            exp for exp in self._explanations.values()
            if exp.target_id == target_id
        ]

    def generate_factors_from_evidence(
        self,
        evidence: List[Dict[str, Any]],
    ) -> List[Factor]:
        """Gera fatores a partir de evidencias."""
        factors = []

        for ev in evidence:
            factor = Factor(
                factor_id=f"fac_{uuid4().hex[:8]}",
                factor_type=FactorType.EVIDENCE,
                name=f"Evidence: {ev.get('type', 'unknown')}",
                description=ev.get('description', 'Evidencia encontrada'),
                weight=ev.get('weight', 0.5),
                value=ev.get('confidence', 0.5),
                impact=ImpactDirection(ev.get('impact', 'neutral')),
                evidence=ev.get('content'),
                source_ref=ev.get('source'),
            )
            factors.append(factor)

        return factors

    def generate_factors_from_sources(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[Factor]:
        """Gera fatores a partir de fontes."""
        factors = []

        for src in sources:
            credibility = src.get('credibility', 0.5)
            impact = ImpactDirection.POSITIVE if credibility > 0.7 else (
                ImpactDirection.NEGATIVE if credibility < 0.3 else ImpactDirection.NEUTRAL
            )

            factor = Factor(
                factor_id=f"fac_{uuid4().hex[:8]}",
                factor_type=FactorType.SOURCE,
                name=f"Source: {src.get('name', 'unknown')}",
                description=f"Fonte com credibilidade {credibility:.0%}",
                weight=0.3,
                value=credibility,
                impact=impact,
                source_ref=src.get('id'),
            )
            factors.append(factor)

        return factors

    def _render_summary(
        self,
        exp_type: ExplanationType,
        level: ExplanationLevel,
        context: Dict[str, Any],
    ) -> str:
        """Renderiza resumo usando template."""
        template = self._templates.get(exp_type)
        if template:
            return template.render(level, context)
        return context.get("main_reason", "")

    def _render_for_level(
        self,
        explanation: DecisionExplanation,
        level: ExplanationLevel,
    ) -> str:
        """Renderiza explicacao para um nivel especifico."""
        template = self._templates.get(explanation.explanation_type)
        if not template:
            return explanation.summary

        context = {
            "explanation_id": explanation.explanation_id,
            "target_id": explanation.target_id,
            "verdict": explanation.decision,
            "confidence": explanation.confidence,
            "factors_summary": self._format_factors(explanation.factors, level),
            "factors_detail": self._format_factors_detail(explanation.factors),
            "reasoning": "\n".join(f"- {r}" for r in explanation.reasoning_chain),
            "alternatives": self._format_alternatives(explanation.alternatives_considered),
            **explanation.metadata,
        }

        return template.render(level, context)

    def _format_factors(self, factors: List[Factor], level: ExplanationLevel) -> str:
        """Formata fatores para display."""
        if level == ExplanationLevel.SIMPLE:
            top = factors[:3] if len(factors) > 3 else factors
            return ", ".join(f.name for f in top)

        return "\n".join(
            f"- {f.name}: {f.description} (peso: {f.weight:.1%}, impacto: {f.impact.value})"
            for f in factors
        )

    def _format_factors_detail(self, factors: List[Factor]) -> str:
        """Formata fatores com detalhe tecnico."""
        lines = []
        for f in factors:
            lines.append(
                f"  [{f.factor_type.value}] {f.name}\n"
                f"    Weight: {f.weight}, Value: {f.value}, Impact: {f.impact.value}\n"
                f"    Contribution: {f.contribution_score():.4f}\n"
                f"    Description: {f.description}"
            )
        return "\n".join(lines)

    def _format_alternatives(self, alternatives: List[Dict[str, Any]]) -> str:
        """Formata alternativas consideradas."""
        if not alternatives:
            return "None"
        return "\n".join(
            f"- {alt.get('verdict', 'unknown')}: {alt.get('reason', 'N/A')}"
            for alt in alternatives
        )

    def _summarize_signal_factors(self, factors: List[Factor]) -> str:
        """Resume fatores de sinal."""
        positive = [f for f in factors if f.impact == ImpactDirection.POSITIVE]
        negative = [f for f in factors if f.impact == ImpactDirection.NEGATIVE]

        parts = []
        if positive:
            parts.append(f"{len(positive)} fatores positivos")
        if negative:
            parts.append(f"{len(negative)} fatores de alerta")

        return " e ".join(parts) if parts else "Analise de multiplos fatores."
