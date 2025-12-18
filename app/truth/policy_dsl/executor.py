"""
Truth Policy DSL Executor — S37

Executes policies against claim/decision contexts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.truth.policy_dsl.grammar import OnThenRule, PolicyAST, RequireCondition


class PolicyAction(str, Enum):
    """Actions that can be triggered by a policy."""

    AUTO_APPROVE = "auto_approve"
    AUTO_REJECT = "auto_reject"
    HUMAN_REVIEW = "human_review"
    COMMITTEE_QUORUM = "committee_quorum"
    ESCALATE = "escalate"
    DEFER = "defer"
    FLAG_FOR_REVIEW = "flag_for_review"


@dataclass
class RequirementResult:
    """Result of evaluating a single requirement."""

    requirement: RequireCondition
    passed: bool
    actual_value: Any
    message: str


@dataclass
class RuleResult:
    """Result of evaluating a single rule."""

    rule: OnThenRule
    triggered: bool
    action: Optional[PolicyAction] = None
    action_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyExecutionResult:
    """Result of executing a policy against a context."""

    policy_name: str
    policy_version: str
    domain: str
    gate: str
    all_requirements_met: bool
    requirement_results: List[RequirementResult]
    triggered_rules: List[RuleResult]
    final_action: Optional[PolicyAction]
    final_action_params: Dict[str, Any]
    context_used: Dict[str, Any]


class PolicyExecutor:
    """
    Executes policies against claim/decision contexts.

    A context is a dictionary containing values like:
    - sources: number of independent sources
    - evidence_count: number of evidences
    - evidence_strength: average strength (0-1)
    - source_diversity: diversity score (0-1)
    - confidence: confidence level ("high", "medium", "low")
    - has_contradiction: boolean
    - contradiction_strength: "weak" or "strong"
    - temporal_consistent: boolean
    - risk_level: "high", "medium", "low"
    """

    def __init__(self):
        self.operators = {
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            "=": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }

    def execute(
        self,
        policy: PolicyAST,
        context: Dict[str, Any],
    ) -> PolicyExecutionResult:
        """
        Execute a policy against a context.

        Args:
            policy: The parsed policy AST
            context: Dictionary with context values

        Returns:
            PolicyExecutionResult with all evaluation details
        """
        # Evaluate all requirements
        req_results = []
        all_met = True

        for req in policy.requirements:
            result = self._evaluate_requirement(req, context)
            req_results.append(result)
            if not result.passed:
                all_met = False

        # Evaluate all rules (only if requirements met, unless rule overrides)
        rule_results = []
        triggered_rules: List[RuleResult] = []

        for rule in policy.rules:
            result = self._evaluate_rule(rule, context)
            rule_results.append(result)
            if result.triggered:
                triggered_rules.append(result)

        # Determine final action
        final_action = None
        final_params = {}

        if not all_met:
            # Requirements not met - check for fallback rules or default to reject
            for tr in triggered_rules:
                if tr.action == PolicyAction.HUMAN_REVIEW:
                    final_action = PolicyAction.HUMAN_REVIEW
                    final_params = tr.action_params
                    break
            if final_action is None:
                final_action = PolicyAction.HUMAN_REVIEW
                final_params = {"reason": "requirements_not_met"}
        elif triggered_rules:
            # Use first triggered rule (priority order)
            tr = triggered_rules[0]
            final_action = tr.action
            final_params = tr.action_params
        else:
            # All requirements met, no specific rule triggered
            final_action = PolicyAction.AUTO_APPROVE

        return PolicyExecutionResult(
            policy_name=policy.name,
            policy_version=policy.version,
            domain=policy.domain,
            gate=policy.gate,
            all_requirements_met=all_met,
            requirement_results=req_results,
            triggered_rules=rule_results,
            final_action=final_action,
            final_action_params=final_params,
            context_used=context,
        )

    def _evaluate_requirement(
        self,
        req: RequireCondition,
        context: Dict[str, Any],
    ) -> RequirementResult:
        """Evaluate a single requirement."""
        field = req.field
        operator = req.operator
        expected = req.value
        modifier = req.modifier

        # Special handling for boolean requirements
        if field == "no_contradiction":
            has_contradiction = context.get("has_contradiction", False)
            if modifier == "strong":
                # Only strong contradictions fail
                contradiction_strength = context.get("contradiction_strength", "weak")
                actual = not (has_contradiction and contradiction_strength == "strong")
            else:
                actual = not has_contradiction
            passed = actual == expected
            return RequirementResult(
                requirement=req,
                passed=passed,
                actual_value=actual,
                message=f"no_contradiction ({modifier or 'any'}): {actual}",
            )

        if field == "temporal_consistency":
            actual = context.get("temporal_consistent", True)
            passed = actual == expected
            return RequirementResult(
                requirement=req,
                passed=passed,
                actual_value=actual,
                message=f"temporal_consistency: {actual}",
            )

        # Get actual value from context
        actual = context.get(field)
        if actual is None:
            return RequirementResult(
                requirement=req,
                passed=False,
                actual_value=None,
                message=f"Field '{field}' not found in context",
            )

        # Apply modifier if present
        if modifier == "independent" and field == "sources":
            # Use independent_sources if available
            actual = context.get("independent_sources", actual)

        # Evaluate comparison
        try:
            op_func = self.operators.get(operator)
            if op_func is None:
                passed = False
                message = f"Unknown operator: {operator}"
            else:
                passed = op_func(actual, expected)
                message = f"{field} {operator} {expected}: actual={actual}"
        except TypeError:
            passed = False
            message = f"Cannot compare {actual} with {expected}"

        return RequirementResult(
            requirement=req,
            passed=passed,
            actual_value=actual,
            message=message,
        )

    def _evaluate_rule(
        self,
        rule: OnThenRule,
        context: Dict[str, Any],
    ) -> RuleResult:
        """Evaluate a single ON...THEN rule."""
        condition_field = rule.condition_field
        condition_op = rule.condition_operator
        condition_value = rule.condition_value

        # Check if condition is a known condition name
        known_conditions = {
            "high_confidence": lambda ctx: ctx.get("confidence") == "high",
            "low_confidence": lambda ctx: ctx.get("confidence") == "low",
            "medium_confidence": lambda ctx: ctx.get("confidence") == "medium",
            "disputed": lambda ctx: ctx.get("has_contradiction", False),
            "no_evidence": lambda ctx: ctx.get("evidence_count", 0) == 0,
            "high_risk": lambda ctx: ctx.get("risk_level") == "high",
            "low_risk": lambda ctx: ctx.get("risk_level") == "low",
        }

        triggered = False

        if condition_field in known_conditions and condition_value is True:
            triggered = known_conditions[condition_field](context)
        else:
            # Evaluate field op value
            actual = context.get(condition_field)
            if actual is not None:
                try:
                    op_func = self.operators.get(condition_op, lambda a, b: a == b)
                    triggered = op_func(actual, condition_value)
                except TypeError:
                    triggered = False

        # Map action string to PolicyAction
        action = None
        if triggered:
            action_map = {
                "auto_approve": PolicyAction.AUTO_APPROVE,
                "auto_reject": PolicyAction.AUTO_REJECT,
                "human_review": PolicyAction.HUMAN_REVIEW,
                "committee_quorum": PolicyAction.COMMITTEE_QUORUM,
                "escalate": PolicyAction.ESCALATE,
                "defer": PolicyAction.DEFER,
                "flag_for_review": PolicyAction.FLAG_FOR_REVIEW,
            }
            action = action_map.get(rule.action.lower(), PolicyAction.HUMAN_REVIEW)

        return RuleResult(
            rule=rule,
            triggered=triggered,
            action=action,
            action_params=rule.action_params if triggered else {},
        )


def execute_policy(
    policy: PolicyAST,
    context: Dict[str, Any],
) -> PolicyExecutionResult:
    """
    Convenience function to execute a policy.

    Args:
        policy: Parsed policy AST
        context: Context dictionary

    Returns:
        PolicyExecutionResult
    """
    executor = PolicyExecutor()
    return executor.execute(policy, context)
