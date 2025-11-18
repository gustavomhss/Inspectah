from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, Optional, Sequence

from .invariants import (
    InvariantViolation,
    ensure_block_integrity,
    ensure_complemento_integrity,
    ensure_fact_integrity,
    ensure_future_ready_fields,
    ensure_version_integrity,
)
from .state_machine import FactState, StateMachine


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _hash_payload(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class BlocoTema:
    bloco_id: str
    titulo: str
    descricao_curta: str
    dominio: str
    referencias_iniciais: Sequence[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utcnow)
    meta: Dict[str, str] = field(default_factory=dict)
    hash_conteudo: str = ""

    def future_ready(self) -> bool:
        return bool(self.hash_conteudo and self.referencias_iniciais)


@dataclass(frozen=True, slots=True)
class FatoRegistravel:
    fato_id: str
    bloco_id: str
    resumo_fato: str
    descricao_detalhada: str
    estado_inicial: FactState
    evidencias: Sequence[str] = field(default_factory=list)
    relatorio_simples: str = ""
    created_at: datetime = field(default_factory=_utcnow)
    hash_conteudo: str = ""
    ancora_externa: str = ""

    def future_ready(self) -> bool:
        return bool(self.hash_conteudo and self.ancora_externa and self.evidencias)


@dataclass(frozen=True, slots=True)
class Complemento:
    complemento_id: str
    bloco_id: Optional[str]
    fato_id: Optional[str]
    tipo: str
    conteudo: str
    referencias: Sequence[str] = field(default_factory=list)
    criado_em: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True, slots=True)
class VersaoFato:
    versao_id: str
    fato_id: str
    numero_versao: int
    descricao: str
    estado: FactState
    evidencias: Sequence[str]
    criada_em: datetime = field(default_factory=_utcnow)
    hash_conteudo: str = ""
    autor: str = "guardiao"


@dataclass(frozen=True, slots=True)
class EstadoFato:
    fato_id: str
    estado_atual: FactState
    atualizado_em: datetime
    justificativa: str


class TruthDB:
    """Versão em memória da Truth-DB usada nos gates e testes da S10."""

    def __init__(self, *, state_machine: Optional[StateMachine] = None) -> None:
        self._state_machine = state_machine or StateMachine()
        self._blocos: Dict[str, BlocoTema] = {}
        self._fatos: Dict[str, FatoRegistravel] = {}
        self._complementos: Dict[str, Complemento] = {}
        self._versoes: Dict[str, VersaoFato] = {}
        self._estados: Dict[str, EstadoFato] = {}

    def register_bloco(self, bloco: BlocoTema) -> None:
        ensure_block_integrity(bloco)
        if bloco.bloco_id in self._blocos:
            raise InvariantViolation(f"Bloco {bloco.bloco_id} duplicado")
        self._blocos[bloco.bloco_id] = bloco

    def register_fato(self, fato: FatoRegistravel) -> None:
        if fato.bloco_id not in self._blocos:
            raise InvariantViolation(
                f"Fato {fato.fato_id} vinculado a bloco inexistente {fato.bloco_id}"
            )
        ensure_fact_integrity(fato)
        if fato.fato_id in self._fatos:
            raise InvariantViolation(f"Fato {fato.fato_id} duplicado")
        if not self._state_machine.is_valid_state(fato.estado_inicial):
            raise InvariantViolation(f"Estado inicial inválido para {fato.fato_id}")
        self._fatos[fato.fato_id] = fato
        self._estados[fato.fato_id] = EstadoFato(
            fato_id=fato.fato_id,
            estado_atual=fato.estado_inicial,
            atualizado_em=fato.created_at,
            justificativa="estado_inicial",
        )

    def add_complemento(self, complemento: Complemento) -> None:
        ensure_complemento_integrity(complemento, blocos=self._blocos, fatos=self._fatos)
        if complemento.complemento_id in self._complementos:
            raise InvariantViolation(f"Complemento {complemento.complemento_id} duplicado")
        self._complementos[complemento.complemento_id] = complemento

    def create_versao(self, versao: VersaoFato) -> None:
        if versao.fato_id not in self._fatos:
            raise InvariantViolation(f"Fato {versao.fato_id} inexistente para versão")
        ensure_version_integrity(versao, expected_next=self._next_version_number(versao.fato_id))
        if versao.versao_id in self._versoes:
            raise InvariantViolation(f"Versão {versao.versao_id} duplicada")
        self._versoes[versao.versao_id] = versao

    def update_estado(self, fato_id: str, novo_estado: FactState, *, justificativa: str) -> None:
        if fato_id not in self._estados:
            raise InvariantViolation(f"Estado solicitado para fato inexistente {fato_id}")
        atual = self._estados[fato_id]
        self._state_machine.validate_transition(atual.estado_atual, novo_estado)
        self._estados[fato_id] = EstadoFato(
            fato_id=fato_id,
            estado_atual=novo_estado,
            atualizado_em=_utcnow(),
            justificativa=justificativa,
        )

    def future_ready_completeness(self) -> float:
        if not self._fatos:
            return 1.0
        prontos = sum(
            1 for fato in self._fatos.values() if ensure_future_ready_fields(fato, silent=True)
        )
        return prontos / len(self._fatos)

    def snapshot(self) -> Dict[str, Dict[str, object]]:
        return {
            "blocos": self._blocos.copy(),
            "fatos": self._fatos.copy(),
            "complementos": self._complementos.copy(),
            "versoes": self._versoes.copy(),
            "estados": self._estados.copy(),
        }

    def validate(self) -> None:
        for bloco in self._blocos.values():
            ensure_block_integrity(bloco)
        for fato in self._fatos.values():
            ensure_fact_integrity(fato)
            ensure_future_ready_fields(fato, silent=False)
        for complemento in self._complementos.values():
            ensure_complemento_integrity(complemento, self._blocos, self._fatos)
        for versao in self._versoes.values():
            ensure_version_integrity(versao)
        self._validate_version_sequences()
        for estado in self._estados.values():
            if not self._state_machine.is_valid_state(estado.estado_atual):
                raise InvariantViolation(f"Estado inválido registrado {estado.estado_atual}")

    def _next_version_number(self, fato_id: str) -> int:
        sequencia = [
            versao.numero_versao for versao in self._versoes.values() if versao.fato_id == fato_id
        ]
        return (max(sequencia) + 1) if sequencia else 1

    def _validate_version_sequences(self) -> None:
        for fato_id in self._fatos.keys():
            numeros = sorted(
                versao.numero_versao
                for versao in self._versoes.values()
                if versao.fato_id == fato_id
            )
            if numeros and numeros != list(range(1, len(numeros) + 1)):
                raise InvariantViolation(f"Sequência de versões inconsistente para {fato_id}")


def build_pilot_truthdb() -> TruthDB:
    """Constrói um dataset determinístico para ser usado pelos gates."""

    state_machine = StateMachine()
    truthdb = TruthDB(state_machine=state_machine)

    bloco = BlocoTema(
        bloco_id="obra_2025_123",
        titulo="Reforma da escola municipal X (contrato 2025-123)",
        descricao_curta="Obra estruturante priorizada pelo programa municipal",
        dominio="obras_publicas",
        referencias_iniciais=[
            "https://transparencia.niteroi.gov/contratos/2025-123",
            "https://imprensa.niteroi.gov/releases/obra-escola-x",
        ],
        hash_conteudo=_hash_payload("obra_2025_123"),
        meta={"cidade": "Niteroi", "responsavel": "SEDUC"},
    )
    truthdb.register_bloco(bloco)

    fato = FatoRegistravel(
        fato_id="obra_2025_123_prazo_conclusao",
        bloco_id=bloco.bloco_id,
        resumo_fato="Prazo de conclusão em 15/12/2025",
        descricao_detalhada="Contrato estabelece conclusão da reforma até 15/12/2025.",
        estado_inicial=FactState.PLANEJADO,
        evidencias=[bloco.referencias_iniciais[0]],
        relatorio_simples="Prazo registrado conforme cláusula terceira do contrato",
        hash_conteudo=_hash_payload("prazo_15122025"),
        ancora_externa="on_chain_slot_placeholder",
    )
    truthdb.register_fato(fato)

    complemento = Complemento(
        complemento_id="compl_001",
        bloco_id=bloco.bloco_id,
        fato_id=fato.fato_id,
        tipo="fonte_secundaria",
        conteudo="Reportagem citando atraso e aditivo",
        referencias=["https://jornal.local/obra_atraso"],
    )
    truthdb.add_complemento(complemento)

    versao_planejada = VersaoFato(
        versao_id="versao_001",
        fato_id=fato.fato_id,
        numero_versao=1,
        descricao="Escopo planejado e prazo inicial.",
        estado=FactState.PLANEJADO,
        evidencias=fato.evidencias,
        hash_conteudo=_hash_payload("versao_planejada"),
    )
    truthdb.create_versao(versao_planejada)

    truthdb.update_estado(
        fato_id=fato.fato_id, novo_estado=FactState.ADIADO, justificativa="Aditivo publicado"
    )
    versao_aditiva = VersaoFato(
        versao_id="versao_002",
        fato_id=fato.fato_id,
        numero_versao=2,
        descricao="Prazo prorrogado até 2026 após aditivo.",
        estado=FactState.ADIADO,
        evidencias=["https://diario.oficial/aditivo_obra_2025_123"],
        hash_conteudo=_hash_payload("versao_aditiva"),
    )
    truthdb.create_versao(versao_aditiva)

    return truthdb
