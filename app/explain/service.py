"""
S39-BE-025: Explainability Service v1

Generates explanations for system decisions (verdicts, signals, policies).
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


def _utc_now() -> datetime:
    """Get current UTC datetime without timezone info."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _generate_id(prefix: str = "exp") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:26]}"


class ExplanationType(str, Enum):
    """Types of explanations."""
    VERDICT = "verdict"
    SIGNAL = "signal"
    RELATION = "relation"
    POLICY = "policy"
    FLOW = "flow"


class FactorDirection(str, Enum):
    """Direction of factor influence."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ImpactLevel(str, Enum):
    """Impact level of a difference or change."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReasoningStep:
    """A single step in the reasoning chain."""
    step_number: int
    description: str
    inputs: List[str]
    output: str
    confidence: Optional[float] = None
    evidence_refs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "description": self.description,
            "inputs": self.inputs,
            "output": self.output,
            "confidence": self.confidence,
            "evidence_refs": self.evidence_refs,
            "metadata": self.metadata,
        }


@dataclass
class ExplanationFactor:
    """A factor that influenced a decision."""
    name: str
    value: Optional[str]
    weight: float
    direction: FactorDirection
    description: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "weight": self.weight,
            "direction": self.direction.value,
            "description": self.description,
            "source": self.source,
        }


@dataclass
class Counterfactual:
    """A counterfactual scenario."""
    condition: str
    outcome: str
    likelihood: Optional[float] = None
    variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition": self.condition,
            "outcome": self.outcome,
            "likelihood": self.likelihood,
            "variables": self.variables,
        }


@dataclass
class Explanation:
    """Complete explanation for a decision."""
    id: str
    type: ExplanationType
    target_id: str
    summary: str
    reasoning_path: List[ReasoningStep]
    factors: List[ExplanationFactor] = field(default_factory=list)
    counterfactuals: List[Counterfactual] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "target_id": self.target_id,
            "summary": self.summary,
            "reasoning_path": [s.to_dict() for s in self.reasoning_path],
            "factors": [f.to_dict() for f in self.factors],
            "counterfactuals": [c.to_dict() for c in self.counterfactuals],
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @property
    def total_steps(self) -> int:
        """Get total number of reasoning steps."""
        return len(self.reasoning_path)

    @property
    def avg_step_confidence(self) -> Optional[float]:
        """Get average confidence across steps."""
        confidences = [s.confidence for s in self.reasoning_path if s.confidence is not None]
        if not confidences:
            return None
        return sum(confidences) / len(confidences)

    def get_step(self, step_number: int) -> Optional[ReasoningStep]:
        """Get a specific step by number."""
        for step in self.reasoning_path:
            if step.step_number == step_number:
                return step
        return None

    def get_positive_factors(self) -> List[ExplanationFactor]:
        """Get factors with positive influence."""
        return [f for f in self.factors if f.direction == FactorDirection.POSITIVE]

    def get_negative_factors(self) -> List[ExplanationFactor]:
        """Get factors with negative influence."""
        return [f for f in self.factors if f.direction == FactorDirection.NEGATIVE]


@dataclass
class ComparisonDifference:
    """A difference between two decisions."""
    aspect: str
    value_a: str
    value_b: str
    impact: ImpactLevel
    explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aspect": self.aspect,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "impact": self.impact.value,
            "explanation": self.explanation,
        }


@dataclass
class DecisionComparison:
    """Comparison between two decisions."""
    decision_a: Explanation
    decision_b: Explanation
    differences: List[ComparisonDifference]
    similarity_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_a": self.decision_a.to_dict(),
            "decision_b": self.decision_b.to_dict(),
            "differences": [d.to_dict() for d in self.differences],
            "similarity_score": self.similarity_score,
        }


class ExplainabilityService:
    """
    Service for generating and managing explanations.
    """

    def __init__(self):
        self._explanations: Dict[str, Explanation] = {}
        self._generators: Dict[ExplanationType, Callable] = {}
        self._register_default_generators()

    def _register_default_generators(self) -> None:
        """Register default explanation generators."""
        self._generators[ExplanationType.VERDICT] = self._generate_verdict_explanation
        self._generators[ExplanationType.SIGNAL] = self._generate_signal_explanation
        self._generators[ExplanationType.RELATION] = self._generate_relation_explanation
        self._generators[ExplanationType.POLICY] = self._generate_policy_explanation
        self._generators[ExplanationType.FLOW] = self._generate_flow_explanation

    def register_generator(
        self,
        exp_type: ExplanationType,
        generator: Callable,
    ) -> None:
        """Register a custom explanation generator."""
        self._generators[exp_type] = generator

    def generate_explanation(
        self,
        exp_type: ExplanationType,
        target_id: str,
        context: Dict[str, Any],
        include_counterfactuals: bool = False,
    ) -> Explanation:
        """
        Generate an explanation for a decision.

        Args:
            exp_type: Type of explanation
            target_id: ID of the target being explained
            context: Context data for generating the explanation
            include_counterfactuals: Whether to include counterfactual scenarios

        Returns:
            Explanation object
        """
        generator = self._generators.get(exp_type)
        if not generator:
            raise ValueError(f"No generator registered for type: {exp_type}")

        explanation = generator(target_id, context, include_counterfactuals)
        self._explanations[explanation.id] = explanation

        return explanation

    def get_explanation(self, explanation_id: str) -> Optional[Explanation]:
        """Get a stored explanation by ID."""
        return self._explanations.get(explanation_id)

    def list_explanations(
        self,
        exp_type: Optional[ExplanationType] = None,
        target_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Explanation]:
        """List stored explanations with optional filters."""
        explanations = list(self._explanations.values())

        if exp_type:
            explanations = [e for e in explanations if e.type == exp_type]

        if target_id:
            explanations = [e for e in explanations if e.target_id == target_id]

        # Sort by creation time descending
        explanations.sort(key=lambda e: e.created_at, reverse=True)

        return explanations[offset:offset + limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        explanations = list(self._explanations.values())
        type_counts = {}
        for exp in explanations:
            type_counts[exp.type.value] = type_counts.get(exp.type.value, 0) + 1

        return {
            "total_explanations": len(explanations),
            "by_type": type_counts,
            "registered_generators": list(self._generators.keys()),
        }

    def delete_explanation(self, explanation_id: str) -> bool:
        """Delete an explanation."""
        if explanation_id in self._explanations:
            del self._explanations[explanation_id]
            return True
        return False

    def compare_decisions(
        self,
        explanation_a: Explanation,
        explanation_b: Explanation,
    ) -> DecisionComparison:
        """
        Compare two decisions and identify differences.

        Args:
            explanation_a: First explanation
            explanation_b: Second explanation

        Returns:
            DecisionComparison with differences and similarity score
        """
        differences = []

        # Compare types
        if explanation_a.type != explanation_b.type:
            differences.append(ComparisonDifference(
                aspect="type",
                value_a=explanation_a.type.value,
                value_b=explanation_b.type.value,
                impact=ImpactLevel.HIGH,
                explanation="Different decision types",
            ))

        # Compare step counts
        if len(explanation_a.reasoning_path) != len(explanation_b.reasoning_path):
            differences.append(ComparisonDifference(
                aspect="reasoning_steps",
                value_a=str(len(explanation_a.reasoning_path)),
                value_b=str(len(explanation_b.reasoning_path)),
                impact=ImpactLevel.MEDIUM,
                explanation="Different number of reasoning steps",
            ))

        # Compare factors
        factors_a = {f.name for f in explanation_a.factors}
        factors_b = {f.name for f in explanation_b.factors}

        only_in_a = factors_a - factors_b
        only_in_b = factors_b - factors_a

        if only_in_a:
            differences.append(ComparisonDifference(
                aspect="factors",
                value_a=", ".join(only_in_a),
                value_b="(missing)",
                impact=ImpactLevel.MEDIUM,
                explanation="Factors only in first decision",
            ))

        if only_in_b:
            differences.append(ComparisonDifference(
                aspect="factors",
                value_a="(missing)",
                value_b=", ".join(only_in_b),
                impact=ImpactLevel.MEDIUM,
                explanation="Factors only in second decision",
            ))

        # Compare common factors
        common_factors = factors_a & factors_b
        for factor_name in common_factors:
            factor_a = next(f for f in explanation_a.factors if f.name == factor_name)
            factor_b = next(f for f in explanation_b.factors if f.name == factor_name)

            if factor_a.direction != factor_b.direction:
                differences.append(ComparisonDifference(
                    aspect=f"factor_{factor_name}_direction",
                    value_a=factor_a.direction.value,
                    value_b=factor_b.direction.value,
                    impact=ImpactLevel.HIGH,
                    explanation=f"Factor '{factor_name}' has different influence direction",
                ))

            weight_diff = abs(factor_a.weight - factor_b.weight)
            if weight_diff > 0.1:
                differences.append(ComparisonDifference(
                    aspect=f"factor_{factor_name}_weight",
                    value_a=str(factor_a.weight),
                    value_b=str(factor_b.weight),
                    impact=ImpactLevel.LOW if weight_diff < 0.3 else ImpactLevel.MEDIUM,
                    explanation=f"Factor '{factor_name}' has different weight",
                ))

        # Calculate similarity score
        similarity_score = self._calculate_similarity(explanation_a, explanation_b, differences)

        return DecisionComparison(
            decision_a=explanation_a,
            decision_b=explanation_b,
            differences=differences,
            similarity_score=similarity_score,
        )

    def _calculate_similarity(
        self,
        explanation_a: Explanation,
        explanation_b: Explanation,
        differences: List[ComparisonDifference],
    ) -> float:
        """Calculate similarity score between two explanations."""
        if not differences:
            return 1.0

        # Weight penalties by impact
        penalties = {
            ImpactLevel.HIGH: 0.3,
            ImpactLevel.MEDIUM: 0.15,
            ImpactLevel.LOW: 0.05,
        }

        total_penalty = sum(penalties.get(d.impact, 0.1) for d in differences)
        similarity = max(0.0, 1.0 - total_penalty)

        return round(similarity, 2)

    def generate_counterfactuals(
        self,
        explanation: Explanation,
        num_counterfactuals: int = 3,
    ) -> List[Counterfactual]:
        """
        Generate counterfactual scenarios for an explanation.

        Args:
            explanation: The explanation to generate counterfactuals for
            num_counterfactuals: Number of counterfactuals to generate

        Returns:
            List of counterfactual scenarios
        """
        counterfactuals = []

        # Generate counterfactuals based on factors
        for factor in explanation.factors[:num_counterfactuals]:
            if factor.direction == FactorDirection.POSITIVE:
                condition = f"If '{factor.name}' were absent or negative"
                outcome = "The decision confidence would likely decrease"
                likelihood = 0.7
            elif factor.direction == FactorDirection.NEGATIVE:
                condition = f"If '{factor.name}' were positive instead"
                outcome = "The decision might change to the opposite"
                likelihood = 0.6
            else:
                condition = f"If '{factor.name}' had stronger influence"
                outcome = "The decision confidence would change"
                likelihood = 0.5

            counterfactuals.append(Counterfactual(
                condition=condition,
                outcome=outcome,
                likelihood=likelihood,
                variables={factor.name: factor.value},
            ))

        return counterfactuals

    # Default Generators

    def _generate_verdict_explanation(
        self,
        target_id: str,
        context: Dict[str, Any],
        include_counterfactuals: bool,
    ) -> Explanation:
        """Generate explanation for a verdict decision."""
        verdict = context.get("verdict", "unknown")
        confidence = context.get("confidence", 0.5)
        evidence = context.get("evidence", [])
        sources = context.get("sources", [])

        steps = [
            ReasoningStep(
                step_number=1,
                description="Collected evidence from available sources",
                inputs=[f"source:{s}" for s in sources[:3]],
                output=f"Found {len(evidence)} evidence items",
                confidence=0.9,
                evidence_refs=evidence[:5],
            ),
            ReasoningStep(
                step_number=2,
                description="Analyzed evidence for consistency and reliability",
                inputs=evidence[:3],
                output=f"Evidence quality: {'high' if confidence > 0.7 else 'moderate'}",
                confidence=confidence,
            ),
            ReasoningStep(
                step_number=3,
                description="Applied policy rules to determine verdict",
                inputs=["policy_rules", "evidence_analysis"],
                output=f"Verdict: {verdict} with confidence {confidence:.2f}",
                confidence=confidence,
            ),
        ]

        factors = [
            ExplanationFactor(
                name="evidence_count",
                value=str(len(evidence)),
                weight=0.4,
                direction=FactorDirection.POSITIVE if len(evidence) >= 2 else FactorDirection.NEUTRAL,
                description="Number of evidence items supporting the verdict",
            ),
            ExplanationFactor(
                name="source_reliability",
                value=f"{len(sources)} sources",
                weight=0.3,
                direction=FactorDirection.POSITIVE if len(sources) >= 2 else FactorDirection.NEUTRAL,
                description="Reliability of sources providing evidence",
            ),
            ExplanationFactor(
                name="confidence_level",
                value=f"{confidence:.2f}",
                weight=0.3,
                direction=FactorDirection.POSITIVE if confidence >= 0.7 else FactorDirection.NEGATIVE,
                description="Overall confidence in the verdict",
            ),
        ]

        summary = f"Verdict '{verdict}' was determined based on {len(evidence)} evidence items from {len(sources)} sources with {confidence:.0%} confidence."

        explanation = Explanation(
            id=_generate_id("exp"),
            type=ExplanationType.VERDICT,
            target_id=target_id,
            summary=summary,
            reasoning_path=steps,
            factors=factors,
            metadata={"verdict": verdict, "confidence": confidence},
        )

        if include_counterfactuals:
            explanation.counterfactuals = self.generate_counterfactuals(explanation)

        return explanation

    def _generate_signal_explanation(
        self,
        target_id: str,
        context: Dict[str, Any],
        include_counterfactuals: bool,
    ) -> Explanation:
        """Generate explanation for a signal calculation."""
        signal_type = context.get("signal_type", "unknown")
        value = context.get("value", 0.0)
        scope = context.get("scope", "global")
        components = context.get("components", {})

        steps = [
            ReasoningStep(
                step_number=1,
                description=f"Gathered data for {signal_type} signal calculation",
                inputs=[f"scope:{scope}"],
                output=f"Collected {len(components)} signal components",
                confidence=0.95,
            ),
            ReasoningStep(
                step_number=2,
                description="Computed signal value from components",
                inputs=list(components.keys())[:3],
                output=f"Signal value: {value:.3f}",
                confidence=0.9,
            ),
        ]

        factors = []
        for comp_name, comp_value in list(components.items())[:5]:
            factors.append(ExplanationFactor(
                name=comp_name,
                value=str(comp_value),
                weight=1.0 / max(len(components), 1),
                direction=FactorDirection.POSITIVE if comp_value > 0.5 else FactorDirection.NEGATIVE,
                description=f"Component contributing to {signal_type}",
            ))

        summary = f"Signal '{signal_type}' at scope '{scope}' calculated as {value:.3f} from {len(components)} components."

        explanation = Explanation(
            id=_generate_id("exp"),
            type=ExplanationType.SIGNAL,
            target_id=target_id,
            summary=summary,
            reasoning_path=steps,
            factors=factors,
            metadata={"signal_type": signal_type, "value": value, "scope": scope},
        )

        if include_counterfactuals:
            explanation.counterfactuals = self.generate_counterfactuals(explanation)

        return explanation

    def _generate_relation_explanation(
        self,
        target_id: str,
        context: Dict[str, Any],
        include_counterfactuals: bool,
    ) -> Explanation:
        """Generate explanation for a claim relation."""
        relation_type = context.get("relation_type", "related")
        confidence = context.get("confidence", 0.5)
        method = context.get("method", "semantic_similarity")
        source_claim = context.get("source_claim", "unknown")
        target_claim = context.get("target_claim", "unknown")

        steps = [
            ReasoningStep(
                step_number=1,
                description="Extracted features from both claims",
                inputs=[source_claim, target_claim],
                output="Features extracted for comparison",
                confidence=0.9,
            ),
            ReasoningStep(
                step_number=2,
                description=f"Applied {method} to determine relation",
                inputs=["features_a", "features_b"],
                output=f"Relation: {relation_type} ({confidence:.2f})",
                confidence=confidence,
            ),
        ]

        factors = [
            ExplanationFactor(
                name="method",
                value=method,
                weight=0.4,
                direction=FactorDirection.NEUTRAL,
                description="Method used to infer relation",
            ),
            ExplanationFactor(
                name="confidence",
                value=f"{confidence:.2f}",
                weight=0.6,
                direction=FactorDirection.POSITIVE if confidence >= 0.7 else FactorDirection.NEUTRAL,
                description="Confidence in the inferred relation",
            ),
        ]

        summary = f"Claims related by '{relation_type}' with {confidence:.0%} confidence using {method}."

        explanation = Explanation(
            id=_generate_id("exp"),
            type=ExplanationType.RELATION,
            target_id=target_id,
            summary=summary,
            reasoning_path=steps,
            factors=factors,
            metadata={"relation_type": relation_type, "method": method},
        )

        if include_counterfactuals:
            explanation.counterfactuals = self.generate_counterfactuals(explanation)

        return explanation

    def _generate_policy_explanation(
        self,
        target_id: str,
        context: Dict[str, Any],
        include_counterfactuals: bool,
    ) -> Explanation:
        """Generate explanation for a policy decision."""
        policy_name = context.get("policy_name", "unknown")
        action = context.get("action", "unknown")
        rules_matched = context.get("rules_matched", [])
        domain = context.get("domain", "general")

        steps = [
            ReasoningStep(
                step_number=1,
                description=f"Evaluated claim against {policy_name} policy",
                inputs=[f"policy:{policy_name}", f"domain:{domain}"],
                output=f"Matched {len(rules_matched)} rules",
                confidence=0.95,
            ),
            ReasoningStep(
                step_number=2,
                description="Applied matching rules to determine action",
                inputs=rules_matched[:3],
                output=f"Action: {action}",
                confidence=0.9,
            ),
        ]

        factors = []
        for rule in rules_matched[:3]:
            factors.append(ExplanationFactor(
                name=f"rule_{rule}",
                value="matched",
                weight=1.0 / max(len(rules_matched), 1),
                direction=FactorDirection.POSITIVE,
                description=f"Policy rule that contributed to decision",
            ))

        summary = f"Policy '{policy_name}' resulted in action '{action}' after matching {len(rules_matched)} rules in domain '{domain}'."

        explanation = Explanation(
            id=_generate_id("exp"),
            type=ExplanationType.POLICY,
            target_id=target_id,
            summary=summary,
            reasoning_path=steps,
            factors=factors,
            metadata={"policy_name": policy_name, "action": action, "domain": domain},
        )

        if include_counterfactuals:
            explanation.counterfactuals = self.generate_counterfactuals(explanation)

        return explanation

    def _generate_flow_explanation(
        self,
        target_id: str,
        context: Dict[str, Any],
        include_counterfactuals: bool,
    ) -> Explanation:
        """Generate explanation for a flow execution."""
        flow_name = context.get("flow_name", "unknown")
        status = context.get("status", "completed")
        steps_executed = context.get("steps_executed", [])
        duration_ms = context.get("duration_ms", 0)

        reasoning_steps = []
        for i, step in enumerate(steps_executed[:5], 1):
            reasoning_steps.append(ReasoningStep(
                step_number=i,
                description=f"Executed step: {step.get('name', f'step_{i}')}",
                inputs=step.get("inputs", []),
                output=step.get("output", "completed"),
                confidence=step.get("confidence", 0.9),
            ))

        factors = [
            ExplanationFactor(
                name="execution_status",
                value=status,
                weight=0.4,
                direction=FactorDirection.POSITIVE if status == "completed" else FactorDirection.NEGATIVE,
                description="Overall flow execution status",
            ),
            ExplanationFactor(
                name="duration",
                value=f"{duration_ms}ms",
                weight=0.3,
                direction=FactorDirection.NEUTRAL,
                description="Total execution time",
            ),
            ExplanationFactor(
                name="steps_count",
                value=str(len(steps_executed)),
                weight=0.3,
                direction=FactorDirection.NEUTRAL,
                description="Number of steps executed",
            ),
        ]

        summary = f"Flow '{flow_name}' {status} after executing {len(steps_executed)} steps in {duration_ms}ms."

        explanation = Explanation(
            id=_generate_id("exp"),
            type=ExplanationType.FLOW,
            target_id=target_id,
            summary=summary,
            reasoning_path=reasoning_steps if reasoning_steps else [
                ReasoningStep(
                    step_number=1,
                    description="Flow execution summary",
                    inputs=[flow_name],
                    output=status,
                    confidence=0.9,
                )
            ],
            factors=factors,
            metadata={"flow_name": flow_name, "status": status, "duration_ms": duration_ms},
        )

        if include_counterfactuals:
            explanation.counterfactuals = self.generate_counterfactuals(explanation)

        return explanation


# Global service instance
_default_service: Optional[ExplainabilityService] = None


def get_service() -> ExplainabilityService:
    """Get the default explainability service instance."""
    global _default_service
    if _default_service is None:
        _default_service = ExplainabilityService()
    return _default_service
