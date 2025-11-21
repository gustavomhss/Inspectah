"""Regras de risco por domínio para o Debunker v1."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple

from .report_models import RiskLevel


@dataclass(slots=True)
class DebunkerRuleSet:
    domain: str
    medium_threshold: float = 0.45
    high_threshold: float = 0.7
    weightings: Mapping[str, float] = field(
        default_factory=lambda: {"impact": 0.4, "novelty": 0.2, "contradiction": 0.25, "history": 0.15}
    )
    escalate_tags: Tuple[str, ...] = ()

    def score(self, *, impact: float, novelty: float, contradiction: float, history: float) -> float:
        weights = self.weightings
        return (
            impact * weights.get("impact", 0.0)
            + novelty * weights.get("novelty", 0.0)
            + contradiction * weights.get("contradiction", 0.0)
            + history * weights.get("history", 0.0)
        )

    def classify(self, *, impact: float, novelty: float, contradiction: float, history: float) -> RiskLevel:
        score = self.score(impact=impact, novelty=novelty, contradiction=contradiction, history=history)
        if score >= self.high_threshold:
            return RiskLevel.HIGH
        if score >= self.medium_threshold:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


def load_default_rules() -> Dict[str, DebunkerRuleSet]:
    return {
        "politica": DebunkerRuleSet(
            domain="politica",
            medium_threshold=0.4,
            high_threshold=0.65,
            weightings={"impact": 0.45, "novelty": 0.15, "contradiction": 0.25, "history": 0.15},
            escalate_tags=("eleicao", "mandato"),
        ),
        "esporte": DebunkerRuleSet(
            domain="esporte",
            medium_threshold=0.35,
            high_threshold=0.6,
            weightings={"impact": 0.3, "novelty": 0.25, "contradiction": 0.3, "history": 0.15},
            escalate_tags=("final", "titulo"),
        ),
        "clima": DebunkerRuleSet(
            domain="clima",
            medium_threshold=0.35,
            high_threshold=0.55,
            weightings={"impact": 0.25, "novelty": 0.15, "contradiction": 0.35, "history": 0.25},
            escalate_tags=("alerta", "emergencia"),
        ),
        "fofoca": DebunkerRuleSet(
            domain="fofoca",
            medium_threshold=0.5,
            high_threshold=0.75,
            weightings={"impact": 0.3, "novelty": 0.25, "contradiction": 0.35, "history": 0.1},
        ),
        "mandatos": DebunkerRuleSet(
            domain="mandatos",
            medium_threshold=0.45,
            high_threshold=0.7,
            weightings={"impact": 0.4, "novelty": 0.1, "contradiction": 0.35, "history": 0.15},
            escalate_tags=("cassacao", "impedimento"),
        ),
        "projetos": DebunkerRuleSet(
            domain="projetos",
            medium_threshold=0.4,
            high_threshold=0.65,
            weightings={"impact": 0.35, "novelty": 0.2, "contradiction": 0.25, "history": 0.2},
        ),
        "ciencia": DebunkerRuleSet(
            domain="ciencia",
            medium_threshold=0.45,
            high_threshold=0.7,
            weightings={"impact": 0.25, "novelty": 0.25, "contradiction": 0.35, "history": 0.15},
            escalate_tags=("saude", "publicacao_retratada"),
        ),
    }


def get_rules_for_domain(domain: str, rules: Mapping[str, DebunkerRuleSet] | None = None) -> DebunkerRuleSet:
    rule_set = (rules or load_default_rules()).get(domain)
    if rule_set:
        return rule_set
    return DebunkerRuleSet(domain=domain)


__all__ = ["DebunkerRuleSet", "load_default_rules", "get_rules_for_domain"]
