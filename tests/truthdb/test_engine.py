from inspectah.truthdb.engine import TruthDBEngine


def _sample_bloco_payload():
    return {
        "id_bloco": "obra_123",
        "titulo": "Obra 123",
        "descricao_curta": "Reforma",
        "dominio": "obras_publicas",
        "referencias_iniciais": ["https://fonte"],
    }


def _sample_fato_payload():
    return {
        "id_bloco": "obra_123",
        "id_fato": "obra_123_prazo",
        "resumo_fato": "Prazo oficial",
        "descricao_detalhada": "Detalhe",
        "estado_inicial": "planejado",
        "evidencias": ["https://fonte"],
        "relatorio_simples": "Resumo",
    }


def test_engine_accepts_flow():
    engine = TruthDBEngine()
    assert engine.apply("criar_bloco_tema", _sample_bloco_payload()).accepted
    assert engine.apply("criar_fato_registravel", _sample_fato_payload()).accepted
    versao_payload = {
        "id_fato": "obra_123_prazo",
        "versao_id": "v1",
        "numero_versao": 1,
        "descricao": "Inicial",
        "estado": "planejado",
        "evidencias": ["https://fonte"],
        "hash_conteudo": "hash_v1",
    }
    assert engine.apply("criar_versao_fato", versao_payload).accepted
    update_payload = {
        "id_fato": "obra_123_prazo",
        "estado_anterior": "planejado",
        "estado_novo": "confirmado",
        "justificativa": "Nova evidência",
        "relatorio_simples": "Resumo",
    }
    assert engine.apply("atualizar_estado_fato", update_payload).accepted


def test_engine_rejects_invalid_transition():
    engine = TruthDBEngine()
    engine.apply("criar_bloco_tema", _sample_bloco_payload())
    engine.apply("criar_fato_registravel", _sample_fato_payload())
    invalid_payload = {
        "id_fato": "obra_123_prazo",
        "estado_anterior": "planejado",
        "estado_novo": "planejado",
        "justificativa": "Sem mudança",
        "relatorio_simples": "Resumo",
    }
    assert not engine.apply("atualizar_estado_fato", invalid_payload).accepted


def test_engine_rejects_missing_block():
    engine = TruthDBEngine()
    payload = _sample_fato_payload()
    payload["id_bloco"] = "faltante"
    assert not engine.apply("criar_fato_registravel", payload).accepted


def test_engine_rejects_unknown_action():
    engine = TruthDBEngine()
    assert not engine.apply("acao_x", {}).accepted
