from __future__ import annotations

import pytest

from inspectah.fields.iel import evaluate_expression, validate_expression


def test_basic_math_and_concat():
    values = {"price": 10, "fee": 2, "title": "Inspectah"}
    assert evaluate_expression("price + fee", values) == 12
    assert evaluate_expression("concat(title, ' v0')", values) == "Inspectah v0"


def test_coalesce_and_if():
    values = {"value": None, "fallback": 42}
    assert evaluate_expression("coalesce(value, fallback)", values) == 42
    assert evaluate_expression("if(value, 1, 0)", values) == 0


def test_length_and_round_history():
    values = {"title": "abc", "score": 1.2345}
    assert evaluate_expression("length(title)", values) == 3
    history = [{"score": 10}, {"score": 20}]
    assert evaluate_expression("lag('score', offset=2)", values, history=history) == 20


def test_invalid_function_rejected():
    values = {"title": "abc"}
    with pytest.raises(ValueError):
        validate_expression("__import__('os').system('ls')", list(values.keys()))


def test_unknown_identifier_rejected():
    values = {"title": "abc"}
    with pytest.raises(ValueError):
        validate_expression("secret + 1", list(values.keys()))
