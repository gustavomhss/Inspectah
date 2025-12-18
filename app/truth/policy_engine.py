"""
Truth Policy Engine — S37

Central engine for loading, caching, and executing policies.
Integrates with E40.5 for invariant verification.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.truth.policy_dsl.executor import (
    PolicyAction,
    PolicyExecutionResult,
    PolicyExecutor,
)
from app.truth.policy_dsl.grammar import PolicyAST
from app.truth.policy_dsl.parser import PolicyParseError, parse_policy

logger = logging.getLogger(__name__)

DEFAULT_POLICIES_DIR = Path("policies")


class PolicyEngine:
    """
    Central engine for policy management and execution.

    Features:
    - Load policies from files
    - Cache parsed policies
    - Execute policies against contexts
    - Integrate with E40.5 invariants
    """

    def __init__(self, policies_dir: Optional[Path] = None):
        self.policies_dir = policies_dir or DEFAULT_POLICIES_DIR
        self.executor = PolicyExecutor()
        self._policy_cache: Dict[str, PolicyAST] = {}
        self._loaded = False

    def load_policies(self) -> int:
        """
        Load all policies from the policies directory.

        Returns:
            Number of policies loaded
        """
        if not self.policies_dir.exists():
            logger.warning(f"Policies directory not found: {self.policies_dir}")
            return 0

        count = 0
        for policy_file in self.policies_dir.glob("*.policy"):
            try:
                policy = self._load_policy_file(policy_file)
                cache_key = f"{policy.domain}:{policy.gate}"
                self._policy_cache[cache_key] = policy
                self._policy_cache[policy.name] = policy
                count += 1
                logger.info(f"Loaded policy: {policy.name} ({cache_key})")
            except Exception as e:
                logger.error(f"Failed to load policy {policy_file}: {e}")

        self._loaded = True
        return count

    def _load_policy_file(self, path: Path) -> PolicyAST:
        """Load and parse a single policy file."""
        text = path.read_text(encoding="utf-8")
        policy = parse_policy(text)

        # Validate the parsed policy
        errors = policy.validate()
        if errors:
            raise ValueError(f"Policy validation failed: {'; '.join(errors)}")

        return policy

    def get_policy(
        self,
        domain: str,
        gate: str,
    ) -> Optional[PolicyAST]:
        """
        Get a policy by domain and gate.

        Args:
            domain: Domain name
            gate: Gate identifier (G1, G7, etc.)

        Returns:
            PolicyAST or None if not found
        """
        if not self._loaded:
            self.load_policies()

        cache_key = f"{domain}:{gate}"
        return self._policy_cache.get(cache_key)

    def get_policy_by_name(self, name: str) -> Optional[PolicyAST]:
        """Get a policy by name."""
        if not self._loaded:
            self.load_policies()
        return self._policy_cache.get(name)

    def list_policies(self) -> List[Dict[str, Any]]:
        """List all loaded policies."""
        if not self._loaded:
            self.load_policies()

        policies = []
        seen = set()
        for key, policy in self._policy_cache.items():
            if policy.name not in seen:
                policies.append({
                    "name": policy.name,
                    "domain": policy.domain,
                    "gate": policy.gate,
                    "version": policy.version,
                    "requirements": len(policy.requirements),
                    "rules": len(policy.rules),
                })
                seen.add(policy.name)

        return policies

    def execute(
        self,
        domain: str,
        gate: str,
        context: Dict[str, Any],
        policy_name: Optional[str] = None,
    ) -> PolicyExecutionResult:
        """
        Execute a policy for a domain/gate against a context.

        Args:
            domain: Domain name
            gate: Gate identifier
            context: Context dictionary with values to check
            policy_name: Optional specific policy name to use

        Returns:
            PolicyExecutionResult

        Raises:
            ValueError: If no policy found for domain/gate
        """
        if policy_name:
            policy = self.get_policy_by_name(policy_name)
        else:
            policy = self.get_policy(domain, gate)

        if not policy:
            raise ValueError(f"No policy found for {domain}:{gate}")

        # Execute policy
        result = self.executor.execute(policy, context)

        # Log execution
        logger.info(
            f"Executed policy {policy.name}: "
            f"requirements_met={result.all_requirements_met}, "
            f"action={result.final_action}"
        )

        return result

    def check_e40_5_invariants(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, bool]:
        """
        Check E40.5 invariants against a context.

        E40.5 invariants are fundamental truth conditions that must hold
        regardless of specific policy rules.

        Returns:
            Dict mapping invariant name to pass/fail status
        """
        invariants = {}

        # I1: Evidence existence
        # A claim cannot be marked verified without at least one evidence
        evidence_count = context.get("evidence_count", 0)
        invariants["evidence_exists"] = evidence_count > 0

        # I2: Source plurality
        # Verified claims should have multiple sources for non-trivial gates
        sources = context.get("sources", 0)
        gate = context.get("gate", "G1")
        if gate in ("G2", "G3", "G7", "G8", "G9"):
            invariants["source_plurality"] = sources >= 2
        else:
            invariants["source_plurality"] = True

        # I3: Temporal coherence
        # Claims should not contradict temporal order of events
        invariants["temporal_coherence"] = context.get("temporal_consistent", True)

        # I4: Non-contradiction (for verified claims)
        # Verified claims should not have strong contradictions
        state = context.get("state", "pending")
        has_contradiction = context.get("has_contradiction", False)
        contradiction_strength = context.get("contradiction_strength", "weak")
        if state == "verified":
            invariants["non_contradiction"] = not (
                has_contradiction and contradiction_strength == "strong"
            )
        else:
            invariants["non_contradiction"] = True

        # I5: Confidence bounds
        # Confidence values should be within expected ranges
        confidence_score = context.get("confidence_score", 0.5)
        invariants["confidence_bounds"] = 0.0 <= confidence_score <= 1.0

        return invariants

    def execute_with_invariants(
        self,
        domain: str,
        gate: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a policy with E40.5 invariant checking.

        Returns combined result with policy execution and invariant status.
        """
        # Check invariants first
        invariants = self.check_e40_5_invariants({**context, "gate": gate})
        all_invariants_pass = all(invariants.values())

        # Execute policy
        result = self.execute(domain, gate, context)

        # Override action if invariants fail
        if not all_invariants_pass and result.final_action == PolicyAction.AUTO_APPROVE:
            result = PolicyExecutionResult(
                policy_name=result.policy_name,
                policy_version=result.policy_version,
                domain=result.domain,
                gate=result.gate,
                all_requirements_met=result.all_requirements_met,
                requirement_results=result.requirement_results,
                triggered_rules=result.triggered_rules,
                final_action=PolicyAction.HUMAN_REVIEW,
                final_action_params={"reason": "invariant_violation"},
                context_used=result.context_used,
            )

        return {
            "execution_result": result,
            "invariants": invariants,
            "all_invariants_pass": all_invariants_pass,
        }


# Singleton instance
_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get or create the default policy engine instance."""
    global _engine
    if _engine is None:
        _engine = PolicyEngine()
    return _engine
