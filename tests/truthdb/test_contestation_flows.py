from pathlib import Path
import sys
import importlib.util
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.truthdb.services import PromotionService, ContestationService  # noqa: E402
from app.truthdb.metrics import snapshot  # noqa: E402


def _load_migration():
    path = ROOT / "migrations/versions/0034_s32_truthdb_blocks.py"
    spec = importlib.util.spec_from_file_location("s32_truthdb_blocks", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mk_claim(claim_id: str) -> dict:
    return {
        "id": claim_id,
        "type": "news_fact_simple",
        "content": f"claim content {claim_id}",
        "evidences": [{"id": f"ev-{claim_id}", "type": "source"}],
    }


def test_contestation_flow(tmp_path: Path):
    db_path = tmp_path / "s32.sqlite"
    _load_migration().apply_migration(db_path)

    promotion = PromotionService(db_path=db_path)
    contest = ContestationService(db_path=db_path)

    ts = promotion.promote_claim(_mk_claim("c1"))
    record = contest.register_contestation(ts.id, {"reason": "doubt"})
    dec_block = contest.process_contestation(record.id)

    counters = Counter(snapshot()["counters"])
    cont_pending = sum(v for k, v in counters.items() if k.startswith("contestation:news_fact_simple") and "pending" in k)
    assert cont_pending >= 1
    assert dec_block is not None
    assert dec_block.fact_block_id == ts.fact_block_id
    success = sum(v for k, v in counters.items() if k.startswith("promotion_success:news_fact_simple"))
    assert success >= 1


def run_tests():
    tmpdir = Path("/tmp") / "s32_contestation_tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    test_contestation_flow(tmpdir)


if __name__ == "__main__":
    run_tests()
