"""Comitê multi-cérebro (V2) que reavalia a proposta com diversidade de modelos."""
from __future__ import annotations

from typing import Iterable, Mapping

from inspectah.debunker.report_models import DebunkerReport, Recommendation, RiskLevel

from .common import CommitteeDecision, DecisionStatus, Reason, Vote, VoteOutcome


DEFAULT_BRAINS = ("guardian_extra", "devils_advocate", "consistency_bot")


def _brain_vote(brain: str, submission: Mapping[str, object], report: DebunkerReport) -> Vote:
    desired_state = str(submission.get("proposed_state", "")).lower()
    rationale_parts = []
    outcome = VoteOutcome.AGREE

    if brain == "devils_advocate":
        if report.risk is RiskLevel.HIGH or report.contradictions:
            outcome = VoteOutcome.DISAGREE
            rationale_parts.append("contradicoes_detectadas")
    elif brain == "consistency_bot":
        if report.recommendation in {Recommendation.OPEN_DISPUTE, Recommendation.ESCALATE}:
            outcome = VoteOutcome.DISAGREE
            rationale_parts.append("debunker_sugeriu_disputa")
    else:
        if desired_state in {"confirmado", "concluido"} and report.risk is RiskLevel.HIGH:
            outcome = VoteOutcome.DISAGREE
            rationale_parts.append("risco_alto_para_promocao")

    reason = Reason(
        code=rationale_parts[0] if rationale_parts else "ok",
        description=";".join(rationale_parts) if rationale_parts else "sem ressalvas",
    )
    weight = 1.0 if brain != "devils_advocate" else 1.2
    return Vote(voter=brain, outcome=outcome, reason=reason, weight=weight)


def run_v2_panel(
    submission: Mapping[str, object],
    report: DebunkerReport,
    brains: Iterable[str] | None = None,
) -> CommitteeDecision:
    panel = tuple(brains) if brains is not None else DEFAULT_BRAINS
    votes = [_brain_vote(brain, submission, report) for brain in panel]
    approve_ratio = sum(v.weight for v in votes if v.outcome is VoteOutcome.AGREE) / (sum(v.weight for v in votes) or 1.0)
    status = DecisionStatus.APPROVED
    rationale = "consenso mínimo atingido"
    evidence_count = int(submission.get("evidence_count", 0) or 0)
    high_risk = report.risk is RiskLevel.HIGH or "high_impact_no_support" in report.meta.get("risk_flags", [])
    if evidence_count <= 0 and high_risk:
        status = DecisionStatus.REJECTED
        rationale = "risco alto sem evidência mínima"
    elif approve_ratio < 0.5:
        status = DecisionStatus.REJECTED
        rationale = "maioria discordou da proposta"
    elif approve_ratio < 0.65:
        status = DecisionStatus.NEED_MORE_EVIDENCE
        rationale = "concordância baixa; pedir mais evidências"
    elif report.recommendation in {Recommendation.OPEN_DISPUTE, Recommendation.ESCALATE}:
        status = DecisionStatus.ESCALATE
        rationale = "Debunker sugeriu escalada"
    metadata = {
        "approve_ratio": approve_ratio,
        "evidence_count": evidence_count,
        "risk_flags": tuple(report.meta.get("risk_flags", ())),
    }
    return CommitteeDecision(layer="V2", status=status, rationale=rationale, votes=votes, metadata=metadata)


__all__ = ["run_v2_panel", "DEFAULT_BRAINS"]
