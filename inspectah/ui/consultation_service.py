from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence, Tuple

from inspectah.anchors.chain_client import ChainClient
from inspectah.anchors.merkle import build_merkle_root
from inspectah.committees.common import CommitteeDecision, DecisionStatus
from inspectah.committees.v1_validator import validate_submission
from inspectah.committees.v2_multibrain import run_v2_panel
from inspectah.committees.v3_coherence import check_coherence
from inspectah.debunker.engine import analyze_claim
from inspectah.debunker.report_models import DebunkerReport, RiskLevel as DebunkerRisk
from inspectah.debunker.rules import DebunkerRuleSet, load_default_rules
from inspectah.metrics import record_run_latency

from .consultation_models import (
    ConsultationEvidence,
    ConsultationInternalError,
    ConsultationRequest,
    ConsultationResult,
    RiskLevel,
)
from .consultation_observability import (
    log_consultation_failed,
    log_consultation_started,
    log_consultation_succeeded,
)


_DOMAINS = {
    "politica": ("política", "eleição", "mandato", "prefeito", "presidente", "corrupção", "governo"),
    "fofoca": ("fofoca", "celebridade", "namoro", "reality", "influencer", "rumor"),
    "esporte": ("gol", "campeonato", "time", "jogo", "liga", "torneio", "esporte"),
    "clima": ("chuva", "frio", "calor", "temperatura", "clima", "previsão", "furacão"),
    "mandatos": ("mandato", "cassação", "cassacao", "impeachment", "reeleição"),
    "projetos": ("projeto", "obra", "licitação", "licitacao", "cronograma", "entrega"),
    "ciencia": ("estudo", "pesquisa", "ciência", "ciencia", "laboratório", "laboratorio", "ensaio"),
}


@dataclass(slots=True)
class ConsultationContext:
    request_id: str
    domain: str
    rules: Mapping[str, DebunkerRuleSet]
    raw_fixture_claim: Mapping[str, object] | None = None


class ConsultationService:
    def __init__(
        self,
        *,
        chain_client: Optional[ChainClient] = None,
        rules: Optional[Mapping[str, DebunkerRuleSet]] = None,
    ) -> None:
        self.chain_client = chain_client or ChainClient()
        self.rules = rules or load_default_rules()

    def run_consultation(self, request: ConsultationRequest) -> ConsultationResult:
        start = time.perf_counter()
        request_id = str(uuid.uuid4())
        log_consultation_started(request_id, request.question)
        try:
            context = self._build_context(request, request_id)
            claim, evidence_payload = self._build_claim(request, context)
            report = analyze_claim(claim, context={"prior_disputes_ratio": claim.get("history_risk", 0.0)})
            submission = self._build_submission(request, claim, report)
            v1 = validate_submission(submission)
            v2 = run_v2_panel(submission, report)
            v3 = check_coherence(submission, submission.get("related", []))
            risk_level, flags, insufficient = self._consolidate_risk(
                report,
                v1,
                v2,
                v3,
                evidence_payload,
                unknown_domain=context.domain == "unknown",
            )
            evidences = self._map_evidences(report)
            anchored = self._anchor_result(request_id, request.question, report, evidences)
            result = ConsultationResult(
                request_id=request_id,
                answer=self._build_answer(report, v1, v2, v3, insufficient),
                risk_level=risk_level,
                risk_score=float(report.meta.get("score")) if "score" in report.meta else None,
                risk_flags=flags,
                evidences=evidences,
                notes=anchored,
                insufficient_data=insufficient,
            )
            duration_ms = (time.perf_counter() - start) * 1000.0
            record_run_latency(duration_ms)
            log_consultation_succeeded(
                request_id,
                risk_level,
                duration_ms=duration_ms,
                evidence_count=len(evidences),
                risk_flags=flags,
            )
            return result
        except ConsultationInternalError as exc:
            duration_ms = (time.perf_counter() - start) * 1000.0
            log_consultation_failed(request_id, exc.code, exc.message, duration_ms=duration_ms)
            raise
        except Exception as exc:  # pragma: no cover - defesa extra
            duration_ms = (time.perf_counter() - start) * 1000.0
            log_consultation_failed(
                request_id,
                "unexpected_error",
                str(exc),
                duration_ms=duration_ms,
                extra_fields={"exception": exc.__class__.__name__},
            )
            raise ConsultationInternalError("Erro interno ao processar a consulta.") from exc

    def _build_context(self, request: ConsultationRequest, request_id: str) -> ConsultationContext:
        domain = self._detect_domain(request.question, request.context)
        fixture_claim = self._load_fixture_claim(domain)
        return ConsultationContext(request_id=request_id, domain=domain, rules=self.rules, raw_fixture_claim=fixture_claim)

    def _detect_domain(self, question: str, context: Optional[str]) -> str:
        text = f"{question} {context or ''}".lower()
        for domain, keywords in _DOMAINS.items():
            if any(term in text for term in keywords):
                return domain
        return "unknown"

    def _load_fixture_claim(self, domain: str) -> Mapping[str, object] | None:
        fixture_path = Path(__file__).resolve().parent.parent / "debunker" / "fixtures" / f"{domain}.json"
        if not fixture_path.exists():
            return None
        try:
            data = json.loads(fixture_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        claims = data.get("claims") or []
        return claims[0] if claims else None

    def _build_claim(self, request: ConsultationRequest, ctx: ConsultationContext) -> Tuple[MutableMapping[str, object], Mapping[str, object]]:
        claim: MutableMapping[str, object] = {
            "id": f"claim-{ctx.request_id}",
            "domain": ctx.domain,
            "summary": request.question,
            "impact": 0.55 if ctx.domain in {"politica", "fofoca"} else 0.4,
            "novelty": 0.35,
            "history_risk": 0.35 if ctx.domain in {"politica", "mandatos"} else 0.2,
            "evidence": [],
        }
        if request.expected_risk:
            claim["expected_risk"] = request.expected_risk.value
        evidence_payload = ctx.raw_fixture_claim.get("evidence", []) if ctx.raw_fixture_claim else []
        if evidence_payload:
            claim["evidence"] = evidence_payload
            claim["summary"] = ctx.raw_fixture_claim.get("summary") or request.question
            claim["impact"] = ctx.raw_fixture_claim.get("impact", claim["impact"])
            claim["novelty"] = ctx.raw_fixture_claim.get("novelty", claim["novelty"])
            claim["history_risk"] = ctx.raw_fixture_claim.get("history_risk", claim["history_risk"])
        else:
            # Sem evidência confiável: manter lista vazia para evitar usar a pergunta como "evidência"
            claim["evidence"] = []
        return claim, claim["evidence"]

    def _build_submission(
        self,
        request: ConsultationRequest,
        claim: Mapping[str, object],
        report: DebunkerReport,
    ) -> MutableMapping[str, object]:
        evidence_count = len(claim.get("evidence", []) or [])
        proposed_state = "confirmado" if report.risk in {DebunkerRisk.LOW, DebunkerRisk.MEDIUM} else "em_disputa"
        submission: MutableMapping[str, object] = {
            "case_id": claim.get("id"),
            "fact_id": f"fact-{claim.get('id')}",
            "domain": claim.get("domain"),
            "current_state": "incerto",
            "proposed_state": proposed_state,
            "evidence_count": evidence_count,
            "claim": claim,
            "related": [],
            "summary": request.question[:200],
        }
        if request.context:
            submission["context"] = request.context
        return submission

    def _map_evidences(self, report: DebunkerReport) -> Tuple[ConsultationEvidence, ...]:
        evidences: list[ConsultationEvidence] = []
        for item in tuple(report.evidence_for) + tuple(report.evidence_against):
            stance = getattr(item, "stance", "neutral")
            evidences.append(
                ConsultationEvidence(
                    id=item.evidence_id,
                    source_name=report.domain,
                    source_type="debunker",
                    description=item.summary or "Evidência analisada",
                    credibility="alta" if item.weight >= 1.0 else "moderada",
                    stance=stance,
                    score=item.weight,
                )
            )
        return tuple(evidences)

    def _consolidate_risk(
        self,
        report: DebunkerReport,
        v1: CommitteeDecision,
        v2: CommitteeDecision,
        v3: CommitteeDecision,
        evidence_payload: Sequence[Mapping[str, object]],
        unknown_domain: bool = False,
    ) -> Tuple[RiskLevel, Tuple[str, ...], bool]:
        flags = tuple(report.meta.get("risk_flags", ()))
        insufficient = len(evidence_payload) == 0 or unknown_domain
        risk_level = _map_risk(report.risk) if not unknown_domain else RiskLevel.UNKNOWN
        decisions = (v1, v2, v3)
        for decision in decisions:
            if decision.status is DecisionStatus.REJECTED:
                insufficient = True
            if decision.status in {DecisionStatus.REJECTED, DecisionStatus.NEED_MORE_EVIDENCE} and risk_level is not RiskLevel.HIGH:
                risk_level = RiskLevel.UNKNOWN
        if v2.status in {DecisionStatus.ESCALATE, DecisionStatus.BLOCKED} or v3.status in {
            DecisionStatus.BLOCKED,
            DecisionStatus.ESCALATE,
        }:
            risk_level = RiskLevel.HIGH
        if insufficient and risk_level is RiskLevel.LOW:
            risk_level = RiskLevel.UNKNOWN
        aggregated_flags = list(flags)
        aggregated_flags.append(f"committee_v1:{v1.status.value}")
        aggregated_flags.append(f"committee_v2:{v2.status.value}")
        aggregated_flags.append(f"committee_v3:{v3.status.value}")
        if unknown_domain:
            aggregated_flags.append("domain:unknown")
        return risk_level, tuple(aggregated_flags), insufficient

    def _build_answer(
        self,
        report: DebunkerReport,
        v1: CommitteeDecision,
        v2: CommitteeDecision,
        v3: CommitteeDecision,
        insufficient: bool,
    ) -> str:
        if insufficient:
            return "Não há evidências suficientes para uma resposta conclusiva neste momento."
        blocks = [
            f"Risco consolidado: {report.risk.value}",
            f"Recomendação do Debunker: {report.recommendation.value}",
            f"Comitês V1/V2/V3: {v1.status.value} / {v2.status.value} / {v3.status.value}",
        ]
        if report.rationale:
            blocks.append(report.rationale)
        return " | ".join(blocks)

    def _anchor_result(
        self,
        request_id: str,
        question: str,
        report: DebunkerReport,
        evidences: Sequence[ConsultationEvidence],
    ) -> str:
        payload = json.dumps(
            {
                "request_id": request_id,
                "question": question,
                "risk": report.risk.value,
                "evidences": [e.dict() for e in evidences],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        merkle = build_merkle_root([payload])
        receipt = self.chain_client.submit_anchor(merkle)
        return f"anchor:{receipt.tx_hash}"


def _map_risk(level: DebunkerRisk) -> RiskLevel:
    if level is DebunkerRisk.LOW:
        return RiskLevel.LOW
    if level is DebunkerRisk.MEDIUM:
        return RiskLevel.MEDIUM
    if level is DebunkerRisk.HIGH:
        return RiskLevel.HIGH
    return RiskLevel.UNKNOWN


__all__ = ["ConsultationService"]
