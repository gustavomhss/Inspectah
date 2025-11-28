from datetime import datetime, timezone

from inspectah.truthdb.invariants import InvariantViolation
from inspectah.truthdb.models import (
    BlocoTema,
    FatoRegistravel,
    TruthDB,
    VersaoFato,
    build_pilot_truthdb,
)
from inspectah.truthdb.state_machine import FactState


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


def test_build_pilot_truthdb_future_ready():
    db = build_pilot_truthdb()
    db.validate()
    assert abs(db.future_ready_completeness() - 1.0) < 1e-6


def test_fact_requires_existing_block():
    db = TruthDB()
    try:
        db.register_fato(
            FatoRegistravel(
                fato_id="isolated",
                bloco_id="missing",
                resumo_fato="Sem bloco",
                descricao_detalhada="",
                estado_inicial=FactState.PLANEJADO,
                evidencias=["http://fonte"],
                relatorio_simples="",
                hash_conteudo="hash",
                ancora_externa="anchor",
                created_at=_utc("2024-01-01T00:00:00"),
            )
        )
    except InvariantViolation:
        return
    raise AssertionError("Esperava InvariantViolation ao registrar fato sem bloco")


def test_future_ready_metric_handles_missing_anchor():
    db = TruthDB()
    bloco = BlocoTema(
        bloco_id="tema",
        titulo="Tema piloto",
        descricao_curta="desc",
        dominio="demo",
        referencias_iniciais=["https://fonte"],
    )
    db.register_bloco(bloco)

    db.register_fato(
        FatoRegistravel(
            fato_id="fato_ok",
            bloco_id="tema",
            resumo_fato="Pronto",
            descricao_detalhada="",
            estado_inicial=FactState.PLANEJADO,
            evidencias=["https://fonte"],
            relatorio_simples="",
            hash_conteudo="hash",
            ancora_externa="anchor",
            created_at=_utc("2024-01-01T00:00:00"),
        )
    )
    db.register_fato(
        FatoRegistravel(
            fato_id="fato_incompleto",
            bloco_id="tema",
            resumo_fato="Sem ancora",
            descricao_detalhada="",
            estado_inicial=FactState.PLANEJADO,
            evidencias=["https://fonte"],
            relatorio_simples="",
            hash_conteudo="hash2",
            ancora_externa="",
            created_at=_utc("2024-01-02T00:00:00"),
        )
    )

    assert abs(db.future_ready_completeness() - 0.5) < 1e-6


def test_version_sequence_must_be_strict():
    db = TruthDB()
    bloco = BlocoTema(
        bloco_id="tema",
        titulo="Tema",
        descricao_curta="desc",
        dominio="demo",
        referencias_iniciais=["https://fonte"],
    )
    db.register_bloco(bloco)
    fato = FatoRegistravel(
        fato_id="fato",
        bloco_id="tema",
        resumo_fato="Resumo",
        descricao_detalhada="detalhe",
        estado_inicial=FactState.PLANEJADO,
        evidencias=["https://fonte"],
        relatorio_simples="",
        hash_conteudo="hash",
        ancora_externa="anchor",
        created_at=_utc("2024-01-03T00:00:00"),
    )
    db.register_fato(fato)
    db.create_versao(
        VersaoFato(
            versao_id="v1",
            fato_id="fato",
            numero_versao=1,
            descricao="Inicial",
            estado=FactState.PLANEJADO,
            evidencias=["https://fonte"],
            hash_conteudo="hash_v1",
        )
    )
    try:
        db.create_versao(
            VersaoFato(
                versao_id="v2",
                fato_id="fato",
                numero_versao=3,
                descricao="Fora de ordem",
                estado=FactState.CONFIRMADO,
                evidencias=["https://fonte"],
                hash_conteudo="hash_v3",
            )
        )
    except InvariantViolation:
        return
    raise AssertionError("Versão fora de ordem deveria falhar")
