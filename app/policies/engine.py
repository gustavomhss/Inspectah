from __future__ import annotations

from .context_builder import PolicyEvaluationContext
from .models import PolicyDecision, PromotionPolicyConfig
from app.truth.enums import TruthState


def evaluate_policy(policy: PromotionPolicyConfig, ctx: PolicyEvaluationContext) -> PolicyDecision:
    """
    Avaliação simples e declarativa.
    """
    flags = {}
    # Verifica contagem de fontes
    if ctx.sources_count < policy.min_sources:
        return PolicyDecision(
            decision="HOLD",
            reason=f"Fontes insuficientes ({ctx.sources_count}/{policy.min_sources})",
            policy_name=policy.name,
            flags={"missing_sources": policy.min_sources - ctx.sources_count},
            target_state=TruthState.PROVISIONAL if ctx.current_state != TruthState.PROVISIONAL else ctx.current_state,
        )

    # Domínios sensíveis endurecem
    if policy.sensitive:
        if policy.require_debunk and not ctx.has_debunk:
            return PolicyDecision(
                decision="BLOCK",
                reason="Domínio sensível exige debunker antes de promover",
                policy_name=policy.name,
                flags={"require_debunk": True},
                target_state=ctx.current_state,
            )
        if policy.require_human or ctx.human_required:
            return PolicyDecision(
                decision="HOLD",
                reason="Revisão humana obrigatória para domínio sensível",
                policy_name=policy.name,
                flags={"require_human": True},
                target_state=TruthState.PROVISIONAL if ctx.current_state != TruthState.PROVISIONAL else ctx.current_state,
            )

    # Confiança mínima
    if ctx.confidence is not None and ctx.confidence < policy.min_confidence:
        return PolicyDecision(
            decision="HOLD",
            reason=f"Confiança abaixo do mínimo ({ctx.confidence:.2f} < {policy.min_confidence:.2f})",
            policy_name=policy.name,
            flags={"low_confidence": True},
            target_state=TruthState.PROVISIONAL if ctx.current_state != TruthState.PROVISIONAL else ctx.current_state,
        )

    # Decisão padrão quando recomendação explícita sugere promover
    if (ctx.recommendation or "").upper() == "PROMOTE":
        return PolicyDecision(
            decision="PROMOTE",
            reason="Recomendação de promover aceita pela policy",
            policy_name=policy.name,
            flags={},
            target_state=TruthState.ESTABLISHED_FACT,
        )

    # Fallback: decisão padrão da policy
    return PolicyDecision(
        decision=policy.default_decision,
        reason="Decisão padrão da policy",
        policy_name=policy.name,
        flags={"default": True},
        target_state=ctx.current_state,
    )
