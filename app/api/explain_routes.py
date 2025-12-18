"""
S39: Explainability API Routes

Endpoints for generating and managing explanations for verdicts, signals, and decisions.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

from app.explain.service import (
    ExplainabilityService,
    ExplanationType,
    Explanation,
    ReasoningStep,
    ExplanationFactor,
    FactorDirection,
    DecisionComparison,
    Counterfactual,
    get_service,
)
from app.explain.drilldown import (
    DrilldownService,
    DrilldownResult,
    EvidenceDetail,
    StepDetail,
    get_drilldown_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/explain", tags=["explainability"])


# Request/Response models

class GenerateExplanationRequest(BaseModel):
    """Request to generate an explanation."""
    type: str = Field(description="Type: verdict, signal, relation, policy, flow")
    target_id: str = Field(description="ID of the entity to explain")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context data")
    include_counterfactuals: bool = Field(default=False, description="Generate what-if scenarios")


class ReasoningStepResponse(BaseModel):
    """Response model for a reasoning step."""
    step_number: int
    description: str
    inputs: List[str]
    output: str
    confidence: Optional[float] = None
    evidence_refs: List[str] = Field(default_factory=list)


class FactorResponse(BaseModel):
    """Response model for an explanation factor."""
    name: str
    value: str
    weight: float
    direction: str
    description: Optional[str] = None


class CounterfactualResponse(BaseModel):
    """Response model for a counterfactual."""
    condition: str
    outcome: str
    likelihood: Optional[float] = None
    variables: Optional[Dict[str, Any]] = None


class ExplanationResponse(BaseModel):
    """Response model for an explanation."""
    id: str
    type: str
    target_id: str
    summary: str
    reasoning_path: List[ReasoningStepResponse]
    factors: List[FactorResponse]
    counterfactuals: Optional[List[CounterfactualResponse]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class CompareDecisionsRequest(BaseModel):
    """Request to compare two decisions."""
    explanation_a_id: str = Field(description="ID of first explanation")
    explanation_b_id: str = Field(description="ID of second explanation")


class DifferenceResponse(BaseModel):
    """Response for a single difference."""
    aspect: str
    value_a: str
    value_b: str
    impact: str
    explanation: str


class ComparisonResponse(BaseModel):
    """Response model for decision comparison."""
    decision_a_id: str
    decision_b_id: str
    similarity_score: float
    differences: List[DifferenceResponse]


class DrilldownStepRequest(BaseModel):
    """Request for step drilldown."""
    explanation_id: str
    step_number: int
    depth: int = Field(default=1, ge=1, le=3)


class DrilldownFactorRequest(BaseModel):
    """Request for factor drilldown."""
    explanation_id: str
    factor_name: str


class DrilldownEvidenceRequest(BaseModel):
    """Request for evidence drilldown."""
    explanation_id: str
    evidence_ref: str


class EvidenceDetailResponse(BaseModel):
    """Response for evidence detail."""
    evidence_id: str
    source_id: Optional[str]
    content_summary: str
    relevance_score: float
    extracted_at: str
    metadata: Optional[Dict[str, Any]] = None


class StepDetailResponse(BaseModel):
    """Response for step detail."""
    step: ReasoningStepResponse
    evidence_details: List[EvidenceDetailResponse]
    input_details: Dict[str, Any]
    computation_trace: List[str]
    alternatives_considered: List[str]


class DrilldownResultResponse(BaseModel):
    """Response for drilldown result."""
    explanation_id: str
    step_number: Optional[int] = None
    step_detail: Optional[StepDetailResponse] = None
    related_factors: List[FactorResponse]
    evidence: List[EvidenceDetailResponse]
    depth: int


# Helper functions

def _parse_explanation_type(type_str: str) -> ExplanationType:
    """Parse string to ExplanationType."""
    try:
        return ExplanationType(type_str)
    except ValueError:
        raise HTTPException(400, f"Invalid explanation type: {type_str}")


def _to_step_response(step: ReasoningStep) -> ReasoningStepResponse:
    """Convert ReasoningStep to response model."""
    return ReasoningStepResponse(
        step_number=step.step_number,
        description=step.description,
        inputs=step.inputs,
        output=step.output,
        confidence=step.confidence,
        evidence_refs=step.evidence_refs or [],
    )


def _to_factor_response(factor: ExplanationFactor) -> FactorResponse:
    """Convert ExplanationFactor to response model."""
    return FactorResponse(
        name=factor.name,
        value=factor.value,
        weight=factor.weight,
        direction=factor.direction.value,
        description=factor.description,
    )


def _to_counterfactual_response(cf: Counterfactual) -> CounterfactualResponse:
    """Convert Counterfactual to response model."""
    return CounterfactualResponse(
        condition=cf.condition,
        outcome=cf.outcome,
        likelihood=cf.likelihood,
        variables=cf.variables,
    )


def _to_explanation_response(exp: Explanation) -> ExplanationResponse:
    """Convert Explanation to response model."""
    counterfactuals = None
    if exp.counterfactuals:
        counterfactuals = [_to_counterfactual_response(cf) for cf in exp.counterfactuals]

    return ExplanationResponse(
        id=exp.id,
        type=exp.type.value,
        target_id=exp.target_id,
        summary=exp.summary,
        reasoning_path=[_to_step_response(s) for s in exp.reasoning_path],
        factors=[_to_factor_response(f) for f in (exp.factors or [])],
        counterfactuals=counterfactuals,
        metadata=exp.metadata,
        created_at=exp.created_at.isoformat() if exp.created_at else None,
    )


def _to_evidence_detail_response(detail: EvidenceDetail) -> EvidenceDetailResponse:
    """Convert EvidenceDetail to response model."""
    return EvidenceDetailResponse(
        evidence_id=detail.evidence_id,
        source_id=detail.source_id,
        content_summary=detail.content_summary,
        relevance_score=detail.relevance_score,
        extracted_at=detail.extracted_at.isoformat() if detail.extracted_at else "",
        metadata=detail.metadata,
    )


def _to_step_detail_response(detail: StepDetail) -> StepDetailResponse:
    """Convert StepDetail to response model."""
    return StepDetailResponse(
        step=_to_step_response(detail.step),
        evidence_details=[_to_evidence_detail_response(e) for e in detail.evidence_details],
        input_details=detail.input_details,
        computation_trace=detail.computation_trace,
        alternatives_considered=detail.alternatives_considered,
    )


# Endpoints

@router.post("/generate", response_model=ExplanationResponse)
async def generate_explanation(body: GenerateExplanationRequest):
    """
    Generate an explanation for a verdict, signal, or decision.

    Types:
    - verdict: Explain why a claim was rated true/false
    - signal: Explain how a signal value was calculated
    - relation: Explain why two claims are related
    - policy: Explain why a policy decision was made
    - flow: Explain what happened in a flow execution
    """
    service = get_service()

    explanation = service.generate_explanation(
        exp_type=_parse_explanation_type(body.type),
        target_id=body.target_id,
        context=body.context,
        include_counterfactuals=body.include_counterfactuals,
    )

    return _to_explanation_response(explanation)


@router.get("/", response_model=List[ExplanationResponse])
async def list_explanations(
    type: Optional[str] = Query(None, description="Filter by type"),
    target_id: Optional[str] = Query(None, description="Filter by target"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    """List generated explanations."""
    service = get_service()

    exp_type = _parse_explanation_type(type) if type else None
    explanations = service.list_explanations(
        exp_type=exp_type,
        target_id=target_id,
        limit=limit,
        offset=offset,
    )

    return [_to_explanation_response(e) for e in explanations]


# Utility endpoints - MUST be before parameterized routes

@router.get("/types")
async def list_explanation_types():
    """List available explanation types."""
    return {
        "types": [
            {"type": t.value, "description": _get_type_description(t)}
            for t in ExplanationType
        ],
    }


@router.get("/stats")
async def get_stats():
    """Get explainability service statistics."""
    service = get_service()
    return service.get_stats()


@router.post("/clear-cache")
async def clear_cache():
    """Clear drilldown cache."""
    drilldown = get_drilldown_service()
    drilldown.clear_cache()
    return {"success": True, "message": "Cache cleared"}


# Parameterized routes

@router.get("/{explanation_id}", response_model=ExplanationResponse)
async def get_explanation(
    explanation_id: str = Path(description="Explanation ID"),
):
    """Get a specific explanation by ID."""
    service = get_service()

    explanation = service.get_explanation(explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {explanation_id}")

    return _to_explanation_response(explanation)


@router.delete("/{explanation_id}")
async def delete_explanation(
    explanation_id: str = Path(description="Explanation ID"),
):
    """Delete an explanation."""
    service = get_service()

    success = service.delete_explanation(explanation_id)
    if not success:
        raise HTTPException(404, f"Explanation not found: {explanation_id}")

    return {"success": True, "deleted_id": explanation_id}


@router.post("/compare", response_model=ComparisonResponse)
async def compare_decisions(body: CompareDecisionsRequest):
    """
    Compare two decisions/explanations.

    Returns differences, similarity score, and recommendation.
    """
    service = get_service()

    exp_a = service.get_explanation(body.explanation_a_id)
    exp_b = service.get_explanation(body.explanation_b_id)

    if not exp_a:
        raise HTTPException(404, f"Explanation not found: {body.explanation_a_id}")
    if not exp_b:
        raise HTTPException(404, f"Explanation not found: {body.explanation_b_id}")

    comparison = service.compare_decisions(exp_a, exp_b)

    return ComparisonResponse(
        decision_a_id=body.explanation_a_id,
        decision_b_id=body.explanation_b_id,
        similarity_score=comparison.similarity_score,
        differences=[
            DifferenceResponse(
                aspect=d.aspect,
                value_a=d.value_a,
                value_b=d.value_b,
                impact=d.impact.value,
                explanation=d.explanation,
            )
            for d in comparison.differences
        ],
    )


@router.post("/counterfactuals/{explanation_id}", response_model=List[CounterfactualResponse])
async def generate_counterfactuals(
    explanation_id: str = Path(description="Explanation ID"),
    num_counterfactuals: int = Query(3, ge=1, le=5),
):
    """Generate counterfactual scenarios for an explanation."""
    service = get_service()

    explanation = service.get_explanation(explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {explanation_id}")

    counterfactuals = service.generate_counterfactuals(
        explanation,
        num_counterfactuals=num_counterfactuals,
    )

    return [_to_counterfactual_response(cf) for cf in counterfactuals]


# Drilldown endpoints

@router.post("/drilldown/step", response_model=DrilldownResultResponse)
async def drilldown_step(body: DrilldownStepRequest):
    """
    Drill down into a specific reasoning step.

    Returns detailed information about the step including:
    - Evidence details
    - Input resolution
    - Computation trace
    - Alternatives considered
    """
    service = get_service()
    drilldown = get_drilldown_service()

    explanation = service.get_explanation(body.explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {body.explanation_id}")

    result = drilldown.drilldown_step(explanation, body.step_number, body.depth)
    if not result:
        raise HTTPException(404, f"Step {body.step_number} not found")

    return DrilldownResultResponse(
        explanation_id=result.explanation_id,
        step_number=result.step_number,
        step_detail=_to_step_detail_response(result.step_detail) if result.step_detail else None,
        related_factors=[_to_factor_response(f) for f in result.related_factors],
        evidence=[_to_evidence_detail_response(e) for e in result.evidence],
        depth=result.depth,
    )


@router.post("/drilldown/factor")
async def drilldown_factor(body: DrilldownFactorRequest):
    """
    Drill down into a specific factor.

    Returns detailed information about how the factor contributed to the decision.
    """
    service = get_service()
    drilldown = get_drilldown_service()

    explanation = service.get_explanation(body.explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {body.explanation_id}")

    result = drilldown.drilldown_factor(explanation, body.factor_name)
    if not result:
        raise HTTPException(404, f"Factor not found: {body.factor_name}")

    return {
        "explanation_id": result.explanation_id,
        "factor_name": body.factor_name,
        "related_factors": [_to_factor_response(f) for f in result.related_factors],
        "evidence": [_to_evidence_detail_response(e) for e in result.evidence],
    }


@router.post("/drilldown/evidence")
async def drilldown_evidence(body: DrilldownEvidenceRequest):
    """
    Drill down into a specific evidence reference.

    Returns detailed information about the evidence.
    """
    service = get_service()
    drilldown = get_drilldown_service()

    explanation = service.get_explanation(body.explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {body.explanation_id}")

    detail = drilldown.drilldown_evidence(explanation, body.evidence_ref)
    if not detail:
        raise HTTPException(404, f"Evidence not found: {body.evidence_ref}")

    return _to_evidence_detail_response(detail)


@router.get("/trace/{explanation_id}")
async def get_full_trace(
    explanation_id: str = Path(description="Explanation ID"),
):
    """Get the complete reasoning trace for an explanation."""
    service = get_service()
    drilldown = get_drilldown_service()

    explanation = service.get_explanation(explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {explanation_id}")

    trace = drilldown.get_full_trace(explanation)

    return {
        "explanation_id": explanation_id,
        "trace": [_to_step_detail_response(s) for s in trace],
        "total_steps": len(trace),
    }


@router.get("/evidence-chain/{explanation_id}")
async def get_evidence_chain(
    explanation_id: str = Path(description="Explanation ID"),
):
    """Get all evidence referenced in an explanation."""
    service = get_service()
    drilldown = get_drilldown_service()

    explanation = service.get_explanation(explanation_id)
    if not explanation:
        raise HTTPException(404, f"Explanation not found: {explanation_id}")

    evidence = drilldown.get_evidence_chain(explanation)

    return {
        "explanation_id": explanation_id,
        "evidence": [_to_evidence_detail_response(e) for e in evidence],
        "total_evidence": len(evidence),
    }


# Helper functions

def _get_type_description(exp_type: ExplanationType) -> str:
    """Get description for explanation type."""
    descriptions = {
        ExplanationType.VERDICT: "Explains why a claim was rated true/false/unverified",
        ExplanationType.SIGNAL: "Explains how a signal value was calculated",
        ExplanationType.RELATION: "Explains why two claims are related",
        ExplanationType.POLICY: "Explains why a policy decision was made",
        ExplanationType.FLOW: "Explains what happened during flow execution",
    }
    return descriptions.get(exp_type, "")
