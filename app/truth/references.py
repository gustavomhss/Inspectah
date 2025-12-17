"""
Sprint 40: Build References for DecisionBlock provenance.

Task: S40-BE-004
Builds the references object with guias, pilares, policy, and e40_5 results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.guardian.models import (
    E40_5Result,
    GuiaReference,
    PilarReference,
    PolicyReference,
    References,
)


# Default guia mappings by domain
DOMAIN_GUIA_MAPPINGS: dict[str, list[dict[str, str]]] = {
    "saude": [
        {"guia": "MQV", "documento": "01_Guia_3X", "tabela": "G2", "secao": "Cap.2"},
    ],
    "politica": [
        {"guia": "MQV", "documento": "02_Guia_Pol", "tabela": "G3", "secao": "Cap.3"},
    ],
    "economia": [
        {"guia": "MQV", "documento": "03_Guia_Eco", "tabela": "G4", "secao": "Cap.4"},
    ],
    "default": [
        {"guia": "MQV", "documento": "00_Guia_Geral", "tabela": "G1", "secao": "Cap.1"},
    ],
}

# Default pilar mappings
DEFAULT_PILARES: list[dict[str, str]] = [
    {"pilar": "P5", "documento": "P5-4", "secao": "§3.2"},
]


@dataclass
class PolicyResult:
    """Result from policy execution."""

    version: str
    rules_applied: list[str]


@dataclass
class E40_5CheckResult:
    """Result from E40.5 check."""

    status: str  # PASS, FAIL, SKIP, TIMEOUT, DEGRADED
    invariants_checked: list[str]
    violations: list[dict[str, str]]


@dataclass
class ClaimContext:
    """Context for a claim being processed."""

    claim_id: str
    domain: str
    gate: str
    text: str | None = None


def build_references(
    claim: ClaimContext | dict[str, Any],
    policy_result: PolicyResult | dict[str, Any] | None = None,
    e40_5_result: E40_5CheckResult | dict[str, Any] | None = None,
    custom_guias: list[dict[str, Any]] | None = None,
    custom_pilares: list[dict[str, Any]] | None = None,
) -> References:
    """
    Build a References object for a DecisionBlock.

    This function assembles complete provenance by combining:
    - Domain-specific guia references
    - Pilar references (ethical/constitutional)
    - Policy execution results
    - E40.5 invariant check results

    Args:
        claim: Claim context (ClaimContext or dict with claim_id, domain, gate)
        policy_result: Result from policy execution (optional)
        e40_5_result: Result from E40.5 check (required for valid blocks)
        custom_guias: Override default guias (optional)
        custom_pilares: Override default pilares (optional)

    Returns:
        References object with complete provenance

    Example:
        >>> claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}
        >>> policy = {"version": "v1.0", "rules_applied": ["rule1"]}
        >>> e40_5 = {"status": "PASS", "invariants_checked": ["INV-1"], "violations": []}
        >>> refs = build_references(claim, policy, e40_5)
        >>> refs.guias[0].guia
        'MQV'
    """
    # Extract claim fields
    if isinstance(claim, dict):
        domain = claim.get("domain", "default")
        gate = claim.get("gate", "")
    else:
        domain = claim.domain
        gate = claim.gate

    # Build guias
    if custom_guias:
        guias = [
            GuiaReference(
                guia=g.get("guia", "MQV"),
                documento=g.get("documento", ""),
                tabela=g.get("tabela"),
                secao=g.get("secao"),
                dominio=g.get("dominio", domain),
                gate=g.get("gate", gate),
            )
            for g in custom_guias
        ]
    else:
        # Use domain-specific defaults
        domain_guias = DOMAIN_GUIA_MAPPINGS.get(domain, DOMAIN_GUIA_MAPPINGS["default"])
        guias = [
            GuiaReference(
                guia=g["guia"],
                documento=g["documento"],
                tabela=g.get("tabela"),
                secao=g.get("secao"),
                dominio=domain,
                gate=gate,
            )
            for g in domain_guias
        ]

    # Build pilares
    if custom_pilares:
        pilares = [
            PilarReference(
                pilar=p.get("pilar", "P5"),
                documento=p.get("documento", ""),
                secao=p.get("secao"),
            )
            for p in custom_pilares
        ]
    else:
        pilares = [
            PilarReference(
                pilar=p["pilar"],
                documento=p["documento"],
                secao=p.get("secao"),
            )
            for p in DEFAULT_PILARES
        ]

    # Build policy reference
    policy_ref = None
    if policy_result:
        if isinstance(policy_result, dict):
            policy_ref = PolicyReference(
                version=policy_result.get("version", "unknown"),
                rules_applied=policy_result.get("rules_applied", []),
            )
        else:
            policy_ref = PolicyReference(
                version=policy_result.version,
                rules_applied=policy_result.rules_applied,
            )

    # Build E40.5 result
    if e40_5_result:
        if isinstance(e40_5_result, dict):
            e40_5 = E40_5Result(
                status=e40_5_result.get("status", "SKIP"),
                invariants_checked=e40_5_result.get("invariants_checked", []),
                violations=e40_5_result.get("violations", []),
            )
        else:
            e40_5 = E40_5Result(
                status=e40_5_result.status,
                invariants_checked=e40_5_result.invariants_checked,
                violations=e40_5_result.violations,
            )
    else:
        # Default to SKIP if no E40.5 result provided
        e40_5 = E40_5Result(
            status="SKIP",
            invariants_checked=[],
            violations=[],
        )

    return References(
        guias=guias,
        pilares=pilares,
        e40_5=e40_5,
        policy=policy_ref,
    )


def build_references_dict(
    claim: ClaimContext | dict[str, Any],
    policy_result: PolicyResult | dict[str, Any] | None = None,
    e40_5_result: E40_5CheckResult | dict[str, Any] | None = None,
    custom_guias: list[dict[str, Any]] | None = None,
    custom_pilares: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build a references dict (for JSON serialization).

    Same as build_references but returns a dict instead of References object.
    """
    refs = build_references(
        claim=claim,
        policy_result=policy_result,
        e40_5_result=e40_5_result,
        custom_guias=custom_guias,
        custom_pilares=custom_pilares,
    )
    return refs.to_dict()
