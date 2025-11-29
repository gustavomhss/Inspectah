from app.policies.context_builder import build_basic_context
from app.policies.engine import evaluate_policy
from app.policies.models import PromotionPolicyConfig
from app.truth.enums import TruthState


def test_non_sensitive_promotes_with_recommendation():
    policy = PromotionPolicyConfig(
        name="global_default",
        domain="general",
        min_confidence=0.5,
        min_sources=1,
        require_debunk=False,
        require_human=False,
        sensitive=False,
        default_decision="HOLD",
    )
    ctx = build_basic_context(
        domain="general",
        current_state=TruthState.UNDER_REVIEW,
        recommendation="PROMOTE",
        confidence=0.8,
        sources_count=2,
    )
    decision = evaluate_policy(policy, ctx)
    assert decision.decision == "PROMOTE"
    assert decision.target_state == TruthState.ESTABLISHED_FACT


def test_sensitive_blocks_without_debunk_and_human():
    policy = PromotionPolicyConfig(
        name="politics_default",
        domain="politics",
        min_confidence=0.7,
        min_sources=2,
        require_debunk=True,
        require_human=True,
        sensitive=True,
        default_decision="HOLD",
    )
    ctx = build_basic_context(
        domain="politics",
        current_state=TruthState.UNDER_REVIEW,
        recommendation="PROMOTE",
        confidence=0.9,
        sources_count=3,
        has_debunk=False,
        human_required=True,
    )
    decision = evaluate_policy(policy, ctx)
    assert decision.decision in {"BLOCK", "HOLD"}
    assert decision.target_state in {TruthState.UNDER_REVIEW, TruthState.PROVISIONAL}
