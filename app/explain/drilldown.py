"""
S39-BE-025: Drilldown Service

Provides detailed drilldown capabilities for explanations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.explain.service import (
    Explanation,
    ReasoningStep,
    ExplanationFactor,
    ExplanationType,
)


def _utc_now() -> datetime:
    """Get current UTC datetime without timezone info."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass
class EvidenceDetail:
    """Detailed information about evidence."""
    evidence_id: str
    source_id: Optional[str]
    content_summary: str
    relevance_score: float
    extracted_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "content_summary": self.content_summary,
            "relevance_score": self.relevance_score,
            "extracted_at": self.extracted_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class StepDetail:
    """Detailed information about a reasoning step."""
    step: ReasoningStep
    evidence_details: List[EvidenceDetail]
    input_details: Dict[str, Any]
    computation_trace: List[str]
    alternatives_considered: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step.to_dict(),
            "evidence_details": [e.to_dict() for e in self.evidence_details],
            "input_details": self.input_details,
            "computation_trace": self.computation_trace,
            "alternatives_considered": self.alternatives_considered,
        }


@dataclass
class DrilldownResult:
    """Result of a drilldown query."""
    explanation_id: str
    step_number: Optional[int]
    step_detail: Optional[StepDetail]
    related_factors: List[ExplanationFactor]
    evidence: List[EvidenceDetail]
    depth: int
    queried_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "step_number": self.step_number,
            "step_detail": self.step_detail.to_dict() if self.step_detail else None,
            "related_factors": [f.to_dict() for f in self.related_factors],
            "evidence": [e.to_dict() for e in self.evidence],
            "depth": self.depth,
            "queried_at": self.queried_at.isoformat(),
        }


class DrilldownService:
    """
    Service for drilling down into explanation details.
    """

    # Maximum depth for drilldown queries (prevents excessive resource usage)
    MAX_DEPTH = 3
    MIN_DEPTH = 1

    def __init__(self, evidence_resolver: Optional[Any] = None):
        """
        Initialize the drilldown service.

        Args:
            evidence_resolver: Optional resolver for fetching evidence details
        """
        self._evidence_resolver = evidence_resolver

    def drilldown_step(
        self,
        explanation: Explanation,
        step_number: int,
        depth: int = 1,
    ) -> Optional[DrilldownResult]:
        """
        Drill down into a specific reasoning step.

        Args:
            explanation: The explanation to drill into
            step_number: The step number to examine
            depth: How deep to drill (1-3)

        Returns:
            DrilldownResult with detailed step information

        Raises:
            ValueError: If depth is out of valid range (1-3)
        """
        if not self.MIN_DEPTH <= depth <= self.MAX_DEPTH:
            raise ValueError(
                f"Depth must be between {self.MIN_DEPTH} and {self.MAX_DEPTH}, got {depth}"
            )

        step = explanation.get_step(step_number)
        if not step:
            return None

        # Get evidence details for this step
        evidence_details = self._resolve_evidence(step.evidence_refs, depth)

        # Build step detail
        step_detail = StepDetail(
            step=step,
            evidence_details=evidence_details,
            input_details=self._resolve_inputs(step.inputs, depth),
            computation_trace=self._generate_computation_trace(step),
            alternatives_considered=self._get_alternatives(explanation, step_number),
        )

        # Find related factors
        related_factors = self._find_related_factors(explanation, step)

        return DrilldownResult(
            explanation_id=explanation.id,
            step_number=step_number,
            step_detail=step_detail,
            related_factors=related_factors,
            evidence=evidence_details,
            depth=depth,
        )

    def drilldown_factor(
        self,
        explanation: Explanation,
        factor_name: str,
        depth: int = 1,
    ) -> Optional[DrilldownResult]:
        """
        Drill down into a specific factor.

        Args:
            explanation: The explanation to drill into
            factor_name: Name of the factor to examine
            depth: How deep to drill (1-3)

        Returns:
            DrilldownResult with factor information

        Raises:
            ValueError: If depth is out of valid range (1-3)
        """
        if not self.MIN_DEPTH <= depth <= self.MAX_DEPTH:
            raise ValueError(
                f"Depth must be between {self.MIN_DEPTH} and {self.MAX_DEPTH}, got {depth}"
            )

        factor = None
        for f in explanation.factors:
            if f.name == factor_name:
                factor = f
                break

        if not factor:
            return None

        # Find steps that mention this factor
        related_steps = []
        for step in explanation.reasoning_path:
            if factor_name.lower() in step.description.lower():
                related_steps.append(step)

        evidence = []
        for step in related_steps:
            evidence.extend(self._resolve_evidence(step.evidence_refs, depth))

        return DrilldownResult(
            explanation_id=explanation.id,
            step_number=None,
            step_detail=None,
            related_factors=[factor],
            evidence=evidence,
            depth=depth,
        )

    def drilldown_evidence(
        self,
        explanation: Explanation,
        evidence_id: str,
    ) -> Optional[EvidenceDetail]:
        """
        Get detailed information about a specific piece of evidence.

        Args:
            explanation: The explanation containing the evidence
            evidence_id: ID of the evidence to examine

        Returns:
            EvidenceDetail if found
        """
        # Check all steps for this evidence
        for step in explanation.reasoning_path:
            if evidence_id in step.evidence_refs:
                details = self._resolve_evidence([evidence_id], depth=3)
                if details:
                    return details[0]

        return None

    def get_full_trace(
        self,
        explanation: Explanation,
    ) -> List[StepDetail]:
        """
        Get the full trace of all steps with details.

        Args:
            explanation: The explanation to trace

        Returns:
            List of detailed step information
        """
        trace = []
        for step in explanation.reasoning_path:
            result = self.drilldown_step(explanation, step.step_number, depth=2)
            if result and result.step_detail:
                trace.append(result.step_detail)

        return trace

    def get_evidence_chain(
        self,
        explanation: Explanation,
    ) -> List[EvidenceDetail]:
        """
        Get all evidence referenced in an explanation.

        Args:
            explanation: The explanation to examine

        Returns:
            List of all evidence details
        """
        evidence_ids = set()
        for step in explanation.reasoning_path:
            evidence_ids.update(step.evidence_refs)

        return self._resolve_evidence(list(evidence_ids), depth=2)

    def _resolve_evidence(
        self,
        evidence_refs: List[str],
        depth: int,
    ) -> List[EvidenceDetail]:
        """Resolve evidence references to detailed objects."""
        details = []
        for ref in evidence_refs:
            # If we have a resolver, use it
            if self._evidence_resolver:
                resolved = self._evidence_resolver.resolve(ref)
                if resolved:
                    details.append(resolved)
                    continue

            # Otherwise create a basic detail
            details.append(EvidenceDetail(
                evidence_id=ref,
                source_id=None,
                content_summary=f"Evidence reference: {ref}",
                relevance_score=0.8 if depth > 1 else 0.5,
                extracted_at=_utc_now(),
                metadata={"depth": depth},
            ))

        return details

    def _resolve_inputs(
        self,
        inputs: List[str],
        depth: int,
    ) -> Dict[str, Any]:
        """Resolve input references to detailed information."""
        details = {}
        for inp in inputs:
            if ":" in inp:
                key, value = inp.split(":", 1)
                details[key] = {
                    "value": value,
                    "resolved": depth > 1,
                }
            else:
                details[inp] = {
                    "value": inp,
                    "resolved": False,
                }

        return details

    def _generate_computation_trace(
        self,
        step: ReasoningStep,
    ) -> List[str]:
        """Generate a computation trace for a step."""
        trace = [
            f"Step {step.step_number}: {step.description}",
            f"Inputs: {', '.join(step.inputs) if step.inputs else 'none'}",
            f"Output: {step.output}",
        ]

        if step.confidence is not None:
            trace.append(f"Confidence: {step.confidence:.2f}")

        if step.evidence_refs:
            trace.append(f"Evidence: {len(step.evidence_refs)} references")

        return trace

    def _get_alternatives(
        self,
        explanation: Explanation,
        step_number: int,
    ) -> List[str]:
        """Get alternatives that were considered at this step."""
        # This would be populated from actual decision logs
        # For now, generate plausible alternatives based on explanation type
        alternatives = []

        if explanation.type == ExplanationType.VERDICT:
            alternatives = [
                "Consider additional sources",
                "Apply stricter confidence threshold",
                "Weight official sources higher",
            ]
        elif explanation.type == ExplanationType.SIGNAL:
            alternatives = [
                "Use different aggregation method",
                "Apply temporal smoothing",
                "Exclude outliers",
            ]
        elif explanation.type == ExplanationType.RELATION:
            alternatives = [
                "Use embedding similarity instead",
                "Apply entity overlap method",
                "Consider temporal proximity",
            ]

        return alternatives[:2]  # Return max 2 alternatives

    def _find_related_factors(
        self,
        explanation: Explanation,
        step: ReasoningStep,
    ) -> List[ExplanationFactor]:
        """Find factors related to a specific step."""
        related = []
        step_terms = set(step.description.lower().split())
        step_terms.update(inp.lower() for inp in step.inputs)

        for factor in explanation.factors:
            factor_terms = set(factor.name.lower().split("_"))
            if factor_terms & step_terms:
                related.append(factor)

        return related

    def clear_cache(self) -> None:
        """Clear the drilldown cache (no-op, kept for API compatibility)."""
        pass  # Cache removed in S39 hardening - method kept for compatibility


# Global service instance
_default_drilldown: Optional[DrilldownService] = None


def get_drilldown_service() -> DrilldownService:
    """Get the default drilldown service instance."""
    global _default_drilldown
    if _default_drilldown is None:
        _default_drilldown = DrilldownService()
    return _default_drilldown
