"""Módulo Debunker da Sprint 15.

Fornece o cérebro cético que identifica claims de risco, levanta
contradições e recomenda ações para o pipeline de disputas.
"""

from .engine import analyze_claim, recommend_action, select_risky_claims
from .report_models import Contradiction, DebunkerReport, EvidenceItem, Recommendation, RiskLevel
from .rules import DebunkerRuleSet, load_default_rules

__all__ = [
    "analyze_claim",
    "recommend_action",
    "select_risky_claims",
    "Contradiction",
    "DebunkerReport",
    "EvidenceItem",
    "Recommendation",
    "RiskLevel",
    "DebunkerRuleSet",
    "load_default_rules",
]
