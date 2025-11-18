from inspectah.pipelines import s10_domain_a_obras, s10_domain_b_precos
import inspectah.truthdb.exports as exports
from inspectah.truthdb.engine import TruthDBEngine


def _build_truthdb():
    engine = TruthDBEngine()
    s10_domain_a_obras.build_domain_a_truthdb(engine=engine)
    s10_domain_b_precos.build_domain_b_truthdb(engine=engine)
    return engine.truthdb


def test_export_truthdb_contains_sections():
    truthdb = _build_truthdb()
    data = exports.export_truthdb(truthdb)
    assert "blocos" in data and "fatos" in data


def test_export_metrics_pass():
    truthdb = _build_truthdb()
    fact_ids = ["obra_123_prazo", "preco_media_sp_julho"]
    data = exports.export_facts(truthdb, fact_ids)
    assert set(data.keys()) == set(fact_ids)
    metrics = exports.build_export_metrics(data)
    assert metrics["audit_trace_completeness"] == 1.0
    assert metrics["future_ready_completeness"] == 1.0
