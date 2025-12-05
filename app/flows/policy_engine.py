from __future__ import annotations

from typing import Dict, List, Optional

DEFAULT_POLICIES: Dict[str, List[Dict]] = {
    "noticias": [
        {"id": "pol_news_source_trust", "etapa": "interprete", "enforcement": "block_on_violation"},
        {"id": "pol_news_confidence_gate", "etapa": "decision_maker", "enforcement": "require_confidence"},
    ],
    "contestacao": [
        {"id": "pol_contestacao_origem_obrigatoria", "etapa": "interprete", "enforcement": "block_on_violation"},
        {"id": "pol_contestacao_protecao_dados", "etapa": "debunker", "enforcement": "block_on_violation"},
    ],
}


class PolicyViolation(Exception):
    pass


def policies_for_domain(domain: str) -> List[Dict]:
    return DEFAULT_POLICIES.get(domain, [])


def validate_transition(domain: str, target_state: str) -> None:
    """
    Regras mínimas: para entrar em teste/ativo, o domínio precisa ter políticas cadastradas.
    """
    if target_state in {"em_teste", "ativo"} and not policies_for_domain(domain):
        raise PolicyViolation(f"Domínio {domain} sem políticas definidas para estado {target_state}")


def validate_step(domain: str, step_type: str, context: Optional[Dict] = None) -> None:
    """
    Validações simples por etapa/domínio. Contexto opcional com flags ou métricas.
    """
    context = context or {}
    for pol in policies_for_domain(domain):
        if pol.get("etapa") != step_type:
            continue
        if pol["enforcement"] == "require_confidence":
            conf = context.get("confidence", 0)
            if conf < context.get("min_confidence", 0.6):
                raise PolicyViolation("Confiança mínima não atendida para decisão")
        if pol["enforcement"] == "block_on_violation" and context.get("violation"):
            raise PolicyViolation(f"Violação de política: {pol['id']}")
