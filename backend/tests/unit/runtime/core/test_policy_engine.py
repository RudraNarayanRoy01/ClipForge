from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.policy_engine import PolicyEngine


def test_policy_engine_deterministic_baseline():
    engine = PolicyEngine()
    intent = ExecutionIntent(
        capability_id="cap",
        payload={"data": 1}
    )
    context = PlanningContext()
    result = PlanningResult(intent=intent, strategy="balanced_planning")

    decision1 = engine.evaluate(result, context)
    decision2 = engine.evaluate(result, context)

    assert decision1.is_approved is True
    assert decision1.fallback_allowed is True
    assert decision1.policy_mode == "balanced"
    assert decision1.constraints == ()
    assert decision1.planning_result is result
    
    # Determinism check
    assert decision1 == decision2


def test_policy_engine_policy_mode_mapping():
    engine = PolicyEngine()
    intent = ExecutionIntent(capability_id="cap", payload={})
    context = PlanningContext()

    mappings = {
        "quality_first_planning": "quality_protected",
        "latency_first_planning": "latency_protected",
        "cost_aware_planning": "cost_constrained",
        "locality_preferred_planning": "locality_preferred",
        "unknown_strategy": "balanced"
    }

    for strategy, expected_mode in mappings.items():
        result = PlanningResult(intent=intent, strategy=strategy)
        decision = engine.evaluate(result, context)
        assert decision.policy_mode == expected_mode
        assert decision.is_approved is True
        assert decision.fallback_allowed is True


def test_policy_engine_constraint_pass_through():
    engine = PolicyEngine()
    intent = ExecutionIntent(capability_id="cap", payload={})
    context = PlanningContext(constraints=("constraint_1", "constraint_2"))
    result = PlanningResult(intent=intent, strategy="balanced_planning")

    decision = engine.evaluate(result, context)

    assert decision.constraints == ("constraint_1", "constraint_2")
    assert decision.is_approved is True
