from __future__ import annotations

from typing import Optional

from app.debunk.models import RecommendedTruthAction
from app.context.service import build_case_dossier
from uuid import uuid4

from app.layers.models import LayerExecution, LayersTrace
from app.layers.storage import LayersTraceRepository
from app.truth.enums import TruthState
from app.truth.service import apply_transition_with_policy, get_or_create_truth_record_for_claim
from app.truth.repository import TruthRepository


def _record(trace: LayersTrace, name: str, input_data, output_data) -> None:
    trace.add_execution(LayerExecution(layer_name=name, input_snapshot=input_data, output_snapshot=output_data))


def run_standard_pipeline(
    claim_id: str,
    domain: str,
    case_id: Optional[str] = None,
    truth_repo: Optional[TruthRepository] = None,
    policies_dir: str = "configs/promotion_policies",
    trace_repo: Optional[LayersTraceRepository] = None,
) -> LayersTrace:
    repo = truth_repo or TruthRepository()
    traces_repo = trace_repo or LayersTraceRepository()
    trace = LayersTrace(claim_id=claim_id, pipeline="standard")
    dossier = build_case_dossier(case_id or domain, truth_repo=repo) if case_id else None

    # Camada: interpretação/classificação simples
    interpretation = {"summary": f"Claim {claim_id} interpretada", "confidence": 0.75}
    _record(trace, "interpretation", {"claim_id": claim_id}, interpretation)

    classification = {"domain": domain, "sensitivity": "LOW"}
    _record(trace, "classification", interpretation, classification)

    # Camada: corroboração básica
    sources_count = 1
    if dossier and dossier.claims:
        first = dossier.claims[0]
        sources_count = max(sources_count, len(first.sources))
    evidence = {"sources_count": sources_count}
    _record(trace, "auto_evidence", classification, evidence)

    # Recomendação
    recommendation = RecommendedTruthAction.SUGERE_PROMOVER.value if interpretation["confidence"] >= 0.7 else RecommendedTruthAction.MANTER_ESTADO_ATUAL.value
    decision_input = {
        "recommendation": recommendation,
        "confidence": interpretation["confidence"],
        "sources_count": sources_count,
    }
    _record(trace, "decision_prep", evidence, decision_input)

    record = get_or_create_truth_record_for_claim(claim_id=claim_id, domain=domain, repo=repo)
    apply_transition_with_policy(
        truth_record=record,
        target_state=TruthState.ESTABLISHED_FACT,
        reason="Pipeline standard",
        source="layers_standard",
        repo=repo,
        policies_dir=policies_dir,
        recommendation="PROMOTE" if recommendation == RecommendedTruthAction.SUGERE_PROMOVER.value else "HOLD",
        confidence=interpretation["confidence"],
        sources_count=sources_count,
        has_debunk=False,
        human_required=False,
    )
    trace_id = f"ltr_{uuid4().hex[:10]}"
    traces_repo.save_trace(trace, trace_id=trace_id, truth_record_id=record.id)
    return trace


def run_hardened_pipeline(
    claim_id: str,
    domain: str,
    case_id: Optional[str] = None,
    truth_repo: Optional[TruthRepository] = None,
    policies_dir: str = "configs/promotion_policies",
    trace_repo: Optional[LayersTraceRepository] = None,
) -> LayersTrace:
    repo = truth_repo or TruthRepository()
    traces_repo = trace_repo or LayersTraceRepository()
    trace = LayersTrace(claim_id=claim_id, pipeline="hardened")
    dossier = build_case_dossier(case_id or domain, truth_repo=repo) if case_id else None

    interpretation = {"summary": f"Claim {claim_id} interpretada (hardened)", "confidence": 0.8}
    _record(trace, "interpretation", {"claim_id": claim_id}, interpretation)

    classification = {"domain": domain, "sensitivity": "HIGH"}
    _record(trace, "classification", interpretation, classification)

    sources_count = 1
    if dossier and dossier.claims:
        first = dossier.claims[0]
        sources_count = max(sources_count, len(first.sources))
    evidence = {"sources_count": sources_count, "debunk": True}
    _record(trace, "auto_evidence", classification, evidence)

    recommendation = RecommendedTruthAction.MANTER_ESTADO_ATUAL.value
    decision_input = {
        "recommendation": recommendation,
        "confidence": interpretation["confidence"],
        "sources_count": sources_count,
    }
    _record(trace, "decision_prep", evidence, decision_input)

    record = get_or_create_truth_record_for_claim(claim_id=claim_id, domain=domain, repo=repo)
    apply_transition_with_policy(
        truth_record=record,
        target_state=TruthState.PROVISIONAL,
        reason="Pipeline hardened",
        source="layers_hardened",
        repo=repo,
        policies_dir=policies_dir,
        recommendation="PROMOTE" if recommendation == RecommendedTruthAction.SUGERE_PROMOVER.value else "HOLD",
        confidence=interpretation["confidence"],
        sources_count=sources_count,
        has_debunk=True,
        human_required=True,
    )
    trace_id = f"ltr_{uuid4().hex[:10]}"
    traces_repo.save_trace(trace, trace_id=trace_id, truth_record_id=record.id)
    return trace
