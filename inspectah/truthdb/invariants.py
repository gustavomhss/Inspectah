from __future__ import annotations

from typing import Dict, Mapping, Optional

from .state_machine import FactState, StateMachine

if False:  # pragma: no cover - only for typing
    from .models import BlocoTema, Complemento, FatoRegistravel, VersaoFato


class InvariantViolation(RuntimeError):
    """Erro lançado quando qualquer invariante da Truth-DB é quebrado."""


def ensure_block_integrity(bloco: "BlocoTema") -> None:
    if not bloco.bloco_id.strip():
        raise InvariantViolation("Bloco sem ID definido")
    if not bloco.titulo.strip():
        raise InvariantViolation(f"Bloco {bloco.bloco_id} sem titulo")
    if not bloco.dominio.strip():
        raise InvariantViolation(f"Bloco {bloco.bloco_id} sem dominio")


def ensure_fact_integrity(fato: "FatoRegistravel") -> None:
    if not fato.fato_id.strip():
        raise InvariantViolation("Fato sem ID")
    if not fato.resumo_fato.strip():
        raise InvariantViolation(f"Fato {fato.fato_id} sem resumo")
    if not fato.evidencias:
        raise InvariantViolation(f"Fato {fato.fato_id} exige pelo menos 1 evidência")


def ensure_complemento_integrity(
    complemento: "Complemento",
    blocos: Mapping[str, "BlocoTema"],
    fatos: Mapping[str, "FatoRegistravel"],
) -> None:
    if not complemento.complemento_id.strip():
        raise InvariantViolation("Complemento sem ID")
    if not complemento.bloco_id and not complemento.fato_id:
        raise InvariantViolation("Complemento precisa apontar para bloco ou fato")
    if complemento.bloco_id and complemento.bloco_id not in blocos:
        raise InvariantViolation(f"Bloco {complemento.bloco_id} inexistente para complemento")
    if complemento.fato_id and complemento.fato_id not in fatos:
        raise InvariantViolation(f"Fato {complemento.fato_id} inexistente para complemento")


def ensure_version_integrity(versao: "VersaoFato", expected_next: Optional[int] = None) -> None:
    if expected_next is not None and versao.numero_versao != expected_next:
        raise InvariantViolation(
            f"Versão {versao.versao_id} fora de ordem. Esperado {expected_next}, recebido {versao.numero_versao}"
        )
    if not isinstance(versao.estado, FactState):
        raise InvariantViolation("Versão precisa carregar estado válido")
    if not versao.evidencias:
        raise InvariantViolation(f"Versão {versao.versao_id} sem evidências")
    if not versao.hash_conteudo:
        raise InvariantViolation(f"Versão {versao.versao_id} sem hash_conteudo")


def ensure_future_ready_fields(fato: "FatoRegistravel", *, silent: bool) -> bool:
    pronto = bool(fato.hash_conteudo and fato.ancora_externa and fato.evidencias)
    if pronto or silent:
        return pronto
    raise InvariantViolation(f"Fato {fato.fato_id} não cumpre requisitos future-ready")


def validate_state_machine_alignment(state_machine: StateMachine, spec: Dict[str, list[str]]) -> None:
    for state_name, targets in spec.items():
        origin = FactState(state_name)
        for target in targets:
            destino = FactState(target)
            if not state_machine.is_valid_transition(origin, destino):
                raise InvariantViolation(
                    f"Transição {origin.value}->{destino.value} não autorizada segundo state machine"
                )
