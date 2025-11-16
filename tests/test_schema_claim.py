import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "inspectah_claim_v0_1.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_claim_enums_match_spec():
    schema = load_schema()
    claim_type = schema["properties"]["claim_type"]["enum"]
    assert set(claim_type) == {
        "resultado_binario",
        "resultado_numerico",
        "estado_evento",
        "data_evento",
        "classificacao",
    }
    polarity = schema["properties"]["polarity"]["enum"]
    assert set(polarity) == {
        "afirma_que_e_verdade",
        "afirma_que_e_falso",
        "informa_sem_julgar",
        "indeterminado",
    }
    local_verdict = schema["properties"]["local_verdict"]["enum"]
    assert set(local_verdict) == {
        "segundo_esta_fonte_este_e_o_valor",
        "segundo_esta_fonte_isto_ocorreu",
        "segundo_esta_fonte_isto_nao_ocorreu",
        "segundo_esta_fonte_ainda_esta_pendente",
        "nao_ha_veredito_claro",
    }


def test_claim_required_fields():
    schema = load_schema()
    required = set(schema["required"])
    assert {"claim_id", "claim_type", "declared_metric", "declared_value", "polarity", "local_verdict", "confidence_claim"} <= required
