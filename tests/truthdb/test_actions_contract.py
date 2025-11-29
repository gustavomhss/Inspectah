from inspectah.truthdb import actions_contract


def test_list_actions_contains_known_entries():
    actions = actions_contract.list_actions()
    assert "criar_bloco_tema" in actions
    assert "atualizar_estado_fato" in actions


def test_validate_action_payload_success():
    payload = {
        "id_bloco": "obra_123",
        "id_fato": "obra_123_prazo",
        "resumo_fato": "Prazo",
        "descricao_detalhada": "Detalhe",
        "estado_inicial": "planejado",
        "evidencias": ["fonte"],
        "relatorio_simples": "Resumo"
    }
    result = actions_contract.validate_action_payload("criar_fato_registravel", payload)
    assert result.is_valid


def test_validate_action_payload_missing_field():
    result = actions_contract.validate_action_payload("criar_bloco_tema", {"id_bloco": "x"})
    assert not result.is_valid
    assert any(err.startswith("campo_obrigatorio_faltando") for err in result.errors)


def test_validate_action_payload_invalid_state():
    payload = {
        "id_fato": "obra",
        "versao_id": "v1",
        "numero_versao": 1,
        "descricao": "desc",
        "estado": "estado_invalido",
        "evidencias": ["fonte"]
    }
    result = actions_contract.validate_action_payload("criar_versao_fato", payload)
    assert not result.is_valid
    assert "estado_invalido" in result.errors


def test_validate_unknown_action():
    result = actions_contract.validate_action_payload("acao_x", {})
    assert not result.is_valid
    assert result.errors == ("acao_desconhecida",)
