from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from . import actions_contract
from .invariants import InvariantViolation
from .models import BlocoTema, Complemento, FatoRegistravel, TruthDB, VersaoFato
from .state_machine import FactState


@dataclass(frozen=True)
class EngineResult:
    action: str
    accepted: bool
    errors: Tuple[str, ...] = ()
    details: str = ""


class TruthDBEngine:
    def __init__(self, truthdb: TruthDB | None = None) -> None:
        self._truthdb = truthdb or TruthDB()

    @property
    def truthdb(self) -> TruthDB:
        return self._truthdb

    def apply(self, action_name: str, payload: Dict[str, object]) -> EngineResult:
        validation = actions_contract.validate_action_payload(action_name, payload)
        if not validation.is_valid:
            return EngineResult(action=action_name, accepted=False, errors=validation.errors)

        handler = getattr(self, f"_handle_{action_name}", None)
        if handler is None:
            return EngineResult(action=action_name, accepted=False, errors=("handler_indisponivel",))

        try:
            handler(payload)
        except InvariantViolation as exc:
            return EngineResult(action=action_name, accepted=False, errors=(f"invariante:{exc}",))
        except Exception as exc:
            return EngineResult(action=action_name, accepted=False, errors=(f"erro:{exc}",))
        return EngineResult(action=action_name, accepted=True, details="aplicado")

    def _handle_criar_bloco_tema(self, payload: Dict[str, object]) -> None:
        bloco = BlocoTema(
            bloco_id=str(payload["id_bloco"]),
            titulo=str(payload["titulo"]),
            descricao_curta=str(payload["descricao_curta"]),
            dominio=str(payload["dominio"]),
            referencias_iniciais=tuple(payload.get("referencias_iniciais", [])),
            meta=dict(payload.get("meta", {})),
        )
        self._truthdb.register_bloco(bloco)

    def _handle_criar_fato_registravel(self, payload: Dict[str, object]) -> None:
        fato = FatoRegistravel(
            fato_id=str(payload["id_fato"]),
            bloco_id=str(payload["id_bloco"]),
            resumo_fato=str(payload["resumo_fato"]),
            descricao_detalhada=str(payload["descricao_detalhada"]),
            estado_inicial=FactState(str(payload["estado_inicial"])),
            evidencias=tuple(payload.get("evidencias", [])),
            relatorio_simples=str(payload["relatorio_simples"]),
            hash_conteudo=str(payload.get("hash_conteudo", "")),
            ancora_externa=str(payload.get("ancora_externa", "")),
        )
        self._truthdb.register_fato(fato)

    def _handle_anexar_complemento(self, payload: Dict[str, object]) -> None:
        complemento = Complemento(
            complemento_id=str(payload["complemento_id"]),
            bloco_id=payload.get("id_bloco"),
            fato_id=payload.get("id_fato"),
            tipo=str(payload["tipo"]),
            conteudo=str(payload["conteudo"]),
            referencias=tuple(payload.get("referencias", [])),
        )
        self._truthdb.add_complemento(complemento)

    def _handle_criar_versao_fato(self, payload: Dict[str, object]) -> None:
        versao = VersaoFato(
            versao_id=str(payload["versao_id"]),
            fato_id=str(payload["id_fato"]),
            numero_versao=int(payload["numero_versao"]),
            descricao=str(payload["descricao"]),
            estado=FactState(str(payload["estado"])),
            evidencias=tuple(payload.get("evidencias", [])),
            hash_conteudo=str(payload.get("hash_conteudo", "")),
        )
        self._truthdb.create_versao(versao)

    def _handle_atualizar_estado_fato(self, payload: Dict[str, object]) -> None:
        self._truthdb.update_estado(
            fato_id=str(payload["id_fato"]),
            novo_estado=FactState(str(payload["estado_novo"])),
            justificativa=str(payload["justificativa"]),
        )

    def _handle_promover_complemento_a_fato(self, payload: Dict[str, object]) -> None:
        complemento = self._truthdb.get_complemento(str(payload["complemento_id"]))
        if complemento is None:
            raise InvariantViolation("complemento_inexistente")
        fato = FatoRegistravel(
            fato_id=str(payload["novo_id_fato"]),
            bloco_id=str(payload["id_bloco"]),
            resumo_fato=str(payload["resumo_fato"]),
            descricao_detalhada=complemento.conteudo,
            estado_inicial=FactState(str(payload["estado_inicial"])),
            evidencias=tuple(payload.get("evidencias", complemento.referencias)),
            relatorio_simples=str(payload.get("relatorio_simples", "")),
            hash_conteudo="",
            ancora_externa="",
        )
        self._truthdb.register_fato(fato)
