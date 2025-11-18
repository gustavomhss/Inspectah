from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .state_machine import FactState


@dataclass(frozen=True)
class ActionSpec:
    name: str
    required_fields: Tuple[str, ...]
    optional_fields: Tuple[str, ...] = ()
    description: str = ""


ACTION_SPECS: Dict[str, ActionSpec] = {
    "criar_bloco_tema": ActionSpec(
        name="criar_bloco_tema",
        required_fields=(
            "id_bloco",
            "titulo",
            "descricao_curta",
            "dominio",
            "referencias_iniciais",
        ),
        optional_fields=("meta",),
        description="Cria um bloco-tema canônico.",
    ),
    "criar_fato_registravel": ActionSpec(
        name="criar_fato_registravel",
        required_fields=(
            "id_bloco",
            "id_fato",
            "resumo_fato",
            "descricao_detalhada",
            "estado_inicial",
            "evidencias",
            "relatorio_simples",
        ),
        optional_fields=("hash_conteudo", "ancora_externa"),
        description="Cria um fato registrável.",
    ),
    "anexar_complemento": ActionSpec(
        name="anexar_complemento",
        required_fields=("complemento_id", "tipo", "conteudo", "referencias"),
        optional_fields=("id_bloco", "id_fato"),
        description="Anexa complemento a bloco ou fato.",
    ),
    "criar_versao_fato": ActionSpec(
        name="criar_versao_fato",
        required_fields=(
            "id_fato",
            "versao_id",
            "numero_versao",
            "descricao",
            "estado",
            "evidencias",
        ),
        optional_fields=("hash_conteudo",),
        description="Registra nova versão do fato.",
    ),
    "atualizar_estado_fato": ActionSpec(
        name="atualizar_estado_fato",
        required_fields=(
            "id_fato",
            "estado_anterior",
            "estado_novo",
            "justificativa",
            "relatorio_simples",
        ),
        optional_fields=("evidencias",),
        description="Atualiza estado via máquina.",
    ),
    "promover_complemento_a_fato": ActionSpec(
        name="promover_complemento_a_fato",
        required_fields=(
            "complemento_id",
            "novo_id_fato",
            "id_bloco",
            "resumo_fato",
            "estado_inicial",
        ),
        optional_fields=("evidencias", "relatorio_simples"),
        description="Promove complemento existente para fato.",
    ),
}


@dataclass(frozen=True)
class ActionValidationResult:
    action: str
    is_valid: bool
    errors: Tuple[str, ...]


def list_actions() -> Tuple[str, ...]:
    return tuple(sorted(ACTION_SPECS.keys()))


def get_action_spec(name: str) -> ActionSpec:
    if name not in ACTION_SPECS:
        raise KeyError(f"Ação desconhecida: {name}")
    return ACTION_SPECS[name]


def validate_action_payload(name: str, payload: Dict[str, object]) -> ActionValidationResult:
    spec = ACTION_SPECS.get(name)
    if spec is None:
        return ActionValidationResult(action=name, is_valid=False, errors=("acao_desconhecida",))

    errors: List[str] = []
    for field in spec.required_fields:
        if field not in payload:
            errors.append(f"campo_obrigatorio_faltando:{field}")

    if name == "criar_fato_registravel":
        _validate_state_field(payload.get("estado_inicial"), errors)
    elif name == "criar_versao_fato":
        _validate_state_field(payload.get("estado"), errors)
    elif name == "atualizar_estado_fato":
        _validate_state_field(payload.get("estado_novo"), errors)
        _validate_state_field(payload.get("estado_anterior"), errors)
    elif name == "promover_complemento_a_fato":
        _validate_state_field(payload.get("estado_inicial"), errors)

    if name == "anexar_complemento" and not any(
        key in payload for key in ("id_bloco", "id_fato")
    ):
        errors.append("alvo_complemento_obrigatorio")

    if name == "criar_bloco_tema":
        refs = payload.get("referencias_iniciais")
        if not isinstance(refs, (list, tuple)) or not refs:
            errors.append("referencias_iniciais_invalidas")

    return ActionValidationResult(action=name, is_valid=len(errors) == 0, errors=tuple(errors))


def _validate_state_field(value: object, errors: List[str]) -> None:
    if value is None:
        errors.append("estado_obrigatorio")
        return
    try:
        FactState(str(value))
    except ValueError:
        errors.append("estado_invalido")
