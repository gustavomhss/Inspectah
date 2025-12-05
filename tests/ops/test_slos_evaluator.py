from pathlib import Path
import sys
from pathlib import Path as _Path

ROOT = _Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ops.slo_evaluator import load_slos, evaluate_slos  # noqa: E402


def test_load_slos_parses_ids_and_metrics(tmp_path: Path):
    # reuse real file
    slos = load_slos("Programa 1/Sprint 33/s33_slos.md")
    assert any(s.id == "s33_slo_recencia_fonte_noticias" for s in slos)
    assert all(s.metrica for s in slos)


def test_evaluate_slos_structure(tmp_path: Path):
    results = evaluate_slos("Programa 1/Sprint 33/s33_slos.md")
    assert len(results) >= 1
    for item in results:
        assert "slo_id" in item and "status" in item
