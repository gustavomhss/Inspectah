from pathlib import Path
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import importlib.util

from app.truthdb.services import PromotionService
from app.truthdb.metrics import snapshot


def _load_migration():
    path = ROOT / "migrations/versions/0034_s32_truthdb_blocks.py"
    spec = importlib.util.spec_from_file_location("s32_truthdb_blocks", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mk_claim(claim_id: str, good: bool = True) -> dict:
    return {
        "id": claim_id,
        "type": "news_fact_simple",
        "content": f"claim content {claim_id}",
        "evidences": [{"id": f"ev-{claim_id}", "type": "source"}] if good else [],
    }


def test_promotion_success(tmp_path: Path):
    db_path = tmp_path / "s32.sqlite"
    _load_migration().apply_migration(db_path)
    svc = PromotionService(db_path=db_path)

    claim = _mk_claim("c1", good=True)
    ts = svc.promote_claim(claim)

    # TruthState created with final status and decision
    assert ts.status.value in ("TRUE", "PENDING")
    counters = Counter(snapshot()["counters"])
    # Aggregated check by prefix (labels may include source)
    attempts = sum(v for k, v in counters.items() if k.startswith("promotion_attempt:news_fact_simple"))
    success = sum(v for k, v in counters.items() if k.startswith("promotion_success:news_fact_simple"))
    assert attempts >= 1
    assert success >= 1


def test_unsupported_claim_type_raises(tmp_path: Path):
    db_path = tmp_path / "s32.sqlite"
    _load_migration().apply_migration(db_path)
    svc = PromotionService(db_path=db_path)

    bad_claim = {"id": "c2", "type": "other", "content": "x"}
    try:
        svc.promote_claim(bad_claim)
    except ValueError:
        return
    raise AssertionError("Expected ValueError for unsupported claim type")


def run_tests():
    tmpdir = Path("/tmp") / "s32_promotion_tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    test_promotion_success(tmpdir)
    test_unsupported_claim_type_raises(tmpdir)


if __name__ == "__main__":
    run_tests()
