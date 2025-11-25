from inspectah.agents.s21_1_copiloto_fontes import run_copiloto_interaction


def test_refuses_truth_debunker_scope():
    result = run_copiloto_interaction(
        "sess-safe-21",
        "decida se esta notícia é verdade, modo debunker",
        {"endpoint": "http://ex"},
        [],
    )
    assert result["actions"] == []
    assert "fonte" in result["assistant_message"].lower() or "copiloto" in result["assistant_message"].lower()


def test_refuses_auto_apply_status():
    result = run_copiloto_interaction(
        "sess-safe-22",
        "aplique status automaticamente sem confirmar",
        {"endpoint": "http://ex"},
        [],
    )
    assert result["actions"] == []


def test_official_open_caution():
    result = run_copiloto_interaction(
        "sess-safe-23",
        "fonte oficial aberta do governo com scraping mágico",
        {},
        [],
    )
    assert any(a.get("field") == "type" and a.get("value") == "official_open" for a in result["actions"])
    assert "oficial" in result["assistant_message"].lower()
