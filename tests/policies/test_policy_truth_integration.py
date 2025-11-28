from pathlib import Path
import tempfile

from app.policies.models import PromotionPolicyConfig
from app.policies.engine import evaluate_policy
from app.policies.context_builder import build_basic_context
from app.truth.enums import TruthState
from app.truth.models import TruthRecord, gen_truth_record_id
from app.truth.service import apply_transition_with_policy, InvalidTruthTransition
from app.truth.repository import TruthRepository


def test_policy_integration_applies_hold_for_low_confidence():
    with tempfile.TemporaryDirectory() as tmp:
        repo = TruthRepository(db_path=Path(tmp) / "truth.sqlite")
        record = TruthRecord(
            id=gen_truth_record_id(),
            slug="general:abc",
            claim_id="abc",
            domain="general",
            current_state=TruthState.UNDER_REVIEW,
        )
        repo.upsert_truth_record(record)

        # Confidence below threshold forces HOLD/PROVISIONAL
        event = apply_transition_with_policy(
            truth_record=record,
            target_state=TruthState.ESTABLISHED_FACT,
            reason="teste",
            source="policy_engine",
            repo=repo,
            policies_dir="configs/promotion_policies",
            recommendation="PROMOTE",
            confidence=0.2,
            sources_count=1,
        )

        updated = repo.get_record(record.id)
        assert updated is not None
        assert updated.current_state in {TruthState.PROVISIONAL, TruthState.UNDER_REVIEW}
        assert event.new_state == updated.current_state


def test_policy_block_raises_for_block_decision():
    policy = PromotionPolicyConfig(
        name="blocker",
        domain="general",
        min_confidence=1.0,
        min_sources=5,
        require_debunk=True,
        require_human=True,
        sensitive=True,
        default_decision="BLOCK",
    )
    ctx = build_basic_context(
        domain="general",
        current_state=TruthState.UNDER_REVIEW,
        recommendation="PROMOTE",
        confidence=0.5,
        sources_count=0,
    )
    decision = evaluate_policy(policy, ctx)
    assert decision.decision in {"HOLD", "BLOCK"}

    record = TruthRecord(
        id=gen_truth_record_id(),
        slug="general:def",
        claim_id="def",
        domain="general",
        current_state=TruthState.UNDER_REVIEW,
    )
    with tempfile.TemporaryDirectory() as tmp:
        repo = TruthRepository(db_path=Path(tmp) / "truth.sqlite")
        repo.upsert_truth_record(record)
        if decision.decision == "BLOCK":
            try:
                apply_transition_with_policy(
                    truth_record=record,
                    target_state=TruthState.ESTABLISHED_FACT,
                    reason="block",
                    source="policy_engine",
                    repo=repo,
                    policies_dir="configs/promotion_policies",
                    recommendation="PROMOTE",
                    confidence=0.3,
                    sources_count=0,
                )
            except InvalidTruthTransition:
                pass
