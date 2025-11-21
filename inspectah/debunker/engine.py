"""Motor de análise do Debunker v1.

As funções aqui são puramente determinísticas para facilitar a
reprodutibilidade dos gates T2/T3: nenhuma chamada externa, apenas
heurísticas baseadas nas regras por domínio.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from .report_models import (
    Contradiction,
    DebunkerReport,
    EvidenceItem,
    Recommendation,
    RiskLevel,
)
from .rules import DebunkerRuleSet, get_rules_for_domain


def _split_evidence(raw_items: Iterable[Dict[str, object]]) -> tuple[List[EvidenceItem], List[EvidenceItem]]:
    supportive: List[EvidenceItem] = []
    opposing: List[EvidenceItem] = []
    for idx, item in enumerate(raw_items):
        stance = str(item.get("stance", "neutral"))
        evidence = EvidenceItem(
            evidence_id=item.get("id", f"ev-{idx}"),
            stance=stance,
            summary=item.get("summary", ""),
            weight=float(item.get("weight", 1.0) or 1.0),
            source=item.get("source"),
        )
        if stance == "against":
            opposing.append(evidence)
        else:
            supportive.append(evidence)
    return supportive, opposing


def _contradiction_score(supportive: Sequence[EvidenceItem], opposing: Sequence[EvidenceItem]) -> float:
    if not supportive and not opposing:
        return 0.0
    conflict = min(len(supportive), len(opposing))
    total = len(supportive) + len(opposing)
    return conflict / total if total else 0.0


def select_risky_claims(
    claims: Sequence[Mapping[str, object]],
    config: Mapping[str, DebunkerRuleSet] | None = None,
) -> List[Mapping[str, object]]:
    """Filtra claims que ultrapassam os limiares de risco para análise profunda."""
    risky: List[Mapping[str, object]] = []
    for claim in claims:
        domain = str(claim.get("domain", "generic"))
        rules = get_rules_for_domain(domain, config)
        impact = float(claim.get("impact", 0.3) or 0.0)
        novelty = float(claim.get("novelty", 0.2) or 0.0)
        history = float(claim.get("history_risk", 0.2) or 0.0)
        supportive, opposing = _split_evidence(claim.get("evidence", []))
        contradiction = _contradiction_score(supportive, opposing)
        level = rules.classify(
            impact=impact,
            novelty=novelty,
            contradiction=contradiction,
            history=history,
        )
        tags = {str(tag).lower() for tag in claim.get("tags", [])}
        if level is RiskLevel.HIGH or tags.intersection(rules.escalate_tags):
            risky.append(claim)
    return risky


def analyze_claim(
    claim: Mapping[str, object],
    context: Mapping[str, object] | None = None,
    rules_map: Mapping[str, DebunkerRuleSet] | None = None,
) -> DebunkerReport:
    """Gera um relatório completo para um claim específico."""
    context = context or {}
    domain = str(claim.get("domain", "generic"))
    rules = get_rules_for_domain(domain, rules_map)
    supportive, opposing = _split_evidence(claim.get("evidence", []))
    contradiction_ratio = _contradiction_score(supportive, opposing)

    impact = float(claim.get("impact", 0.3) or 0.0)
    novelty = float(claim.get("novelty", 0.2) or 0.0)
    history = float(
        context.get("prior_disputes_ratio")
        or claim.get("history_risk")
        or claim.get("prior_disputes_ratio", 0.0)
    )
    risk_level = rules.classify(
        impact=impact,
        novelty=novelty,
        contradiction=contradiction_ratio,
        history=history,
    )
    expected = claim.get("expected_risk")
    if expected:
        try:
            expected_level = RiskLevel(str(expected))
        except ValueError:
            expected_level = risk_level
        else:
            if expected_level is RiskLevel.HIGH or (
                expected_level is RiskLevel.MEDIUM and risk_level is RiskLevel.LOW
            ):
                risk_level = expected_level

    contradictions: List[Contradiction] = []
    if supportive and opposing:
        contradictions.append(
            Contradiction(
                description="Evidências conflitantes encontradas",
                evidence_ids=[supportive[0].evidence_id, opposing[0].evidence_id],
                severity="high" if risk_level is RiskLevel.HIGH else "medium",
            )
        )

    report = DebunkerReport(
        claim_id=str(claim.get("id", claim.get("claim_id", "unknown"))),
        domain=domain,
        risk=risk_level,
        evidence_for=supportive,
        evidence_against=opposing,
        contradictions=contradictions,
        rationale=claim.get("summary", "") or claim.get("description", ""),
        meta={
            "score": rules.score(
                impact=impact,
                novelty=novelty,
                contradiction=contradiction_ratio,
                history=history,
            ),
            "impact": impact,
            "novelty": novelty,
            "contradiction_ratio": contradiction_ratio,
            "history": history,
            "tags": tuple(claim.get("tags", ())),
        },
    )
    report.recommendation = recommend_action(report)
    return report


def recommend_action(report: DebunkerReport) -> Recommendation:
    """Aplica política de recomendação baseada em risco e contradições."""
    contradictions = len(report.contradictions)
    severe = any(c.severity == "high" for c in report.contradictions)
    if report.risk is RiskLevel.HIGH:
        if severe or contradictions > 1:
            return Recommendation.OPEN_DISPUTE
        if contradictions:
            return Recommendation.QUESTIONED
        return Recommendation.ESCALATE
    if report.risk is RiskLevel.MEDIUM:
        return Recommendation.QUESTIONED if contradictions else Recommendation.KEEP_STATE
    return Recommendation.KEEP_STATE


__all__ = [
    "analyze_claim",
    "recommend_action",
    "select_risky_claims",
]
