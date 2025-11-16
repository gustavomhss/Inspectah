from inspectah.equivalence_key import generate_equivalence_key


def test_equivalence_key_is_deterministic():
    key1 = generate_equivalence_key(
        declared_metric="indice_X",
        declared_subject="Brasil",
        published_at="2025-03-10T00:00:00Z",
        entities=["IBGE", "IPCA"],
    )
    key2 = generate_equivalence_key(
        declared_metric=" indice_X ",
        declared_subject="brasil",
        published_at="2025-03-10T03:00:00+00:00",
        entities=["IPCA", "IBGE"],
    )
    assert key1 == key2


def test_equivalence_key_handles_missing_data():
    key = generate_equivalence_key(declared_metric="status_obra", published_at=None)
    assert key.startswith("status_obra")
    assert "undated" in key


def test_equivalence_key_needs_metric():
    try:
        generate_equivalence_key(declared_metric="")
    except ValueError:
        return
    raise AssertionError("Esperava ValueError quando metric está vazio")
