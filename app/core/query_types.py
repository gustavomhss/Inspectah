from __future__ import annotations

from typing import Dict, Literal

InfoType = Literal[
    "C1_preco_medio",
    "C2_comparacao_simples",
    "C3_checagem_factual",
    "fora_de_escopo",
]

QueryType = Literal[
    "preco_medio",
    "comparacao_simples",
    "checagem_factual",
    "fora_de_escopo",
]

INFO_TYPE_TO_QUERY_TYPE: Dict[InfoType, QueryType] = {
    "C1_preco_medio": "preco_medio",
    "C2_comparacao_simples": "comparacao_simples",
    "C3_checagem_factual": "checagem_factual",
    "fora_de_escopo": "fora_de_escopo",
}

QUERY_TYPE_TO_INFO_TYPE: Dict[QueryType, InfoType] = {
    "preco_medio": "C1_preco_medio",
    "comparacao_simples": "C2_comparacao_simples",
    "checagem_factual": "C3_checagem_factual",
    "fora_de_escopo": "fora_de_escopo",
}


def resolve_info_type(query_type: QueryType) -> InfoType:
    return QUERY_TYPE_TO_INFO_TYPE[query_type]


def scenario_from_info_type(info_type: InfoType) -> str:
    if info_type == "fora_de_escopo":
        return "OUT_OF_SCOPE"
    return info_type.split("_", maxsplit=1)[0]
