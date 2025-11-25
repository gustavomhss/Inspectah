from inspectah.agents.s21_1_copiloto_fontes import run_copiloto_interaction


def test_copiloto_suggests_type_for_news_request():
    result = run_copiloto_interaction(
        "sess-1",
        "quero cadastrar uma fonte de notícias do brasil",
        {"endpoint": "https://exemplo.com/rss"},
        [],
    )
    assert isinstance(result.get("assistant_message"), str)
    assert "actions" in result
    actions = result["actions"]
    has_type_suggestion = any(action.get("field") == "type" for action in actions)
    assert has_type_suggestion


def test_copiloto_returns_validation_issue_for_invalid_type():
    result = run_copiloto_interaction(
        "sess-2",
        "fonte qualquer",
        {"type": "invalid_type", "endpoint": ""},
        [],
    )
    assert result["actions"] == []
    assert "problemas" in result["assistant_message"].lower()
