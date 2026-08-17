import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.policy_decision import PolicyDecision
from src.runtime.core.route_decision import RouteDecision
from src.runtime.core.routing_engine import RoutingEngine

@pytest.fixture
def base_intent() -> ExecutionIntent:
    return ExecutionIntent(
        capability_id="test_cap",
        payload={"data": "opaque"}
    )

@pytest.fixture
def base_planning_result(base_intent: ExecutionIntent) -> PlanningResult:
    return PlanningResult(
        intent=base_intent,
        strategy="balanced_planning",
        requirements=("test_req",),
        constraints={"timeout": 30}
    )

def test_routing_valid_approval(base_planning_result: PlanningResult):
    decision = PolicyDecision(
        planning_result=base_planning_result,
        is_approved=True,
        policy_mode="balanced",
        fallback_allowed=True,
        constraints=("test_constraint",)
    )
    
    engine = RoutingEngine()
    route = engine.evaluate(decision)
    
    assert route.is_routed is True
    assert route.execution_class == "abstract_balanced"
    assert route.fallback_allowed is True
    assert route.policy_decision is decision  # Policy identity preserved

def test_routing_policy_rejection(base_planning_result: PlanningResult):
    decision = PolicyDecision(
        planning_result=base_planning_result,
        is_approved=False,
        policy_mode="balanced",
        fallback_allowed=True,
        constraints=()
    )
    
    engine = RoutingEngine()
    route = engine.evaluate(decision)
    
    assert route.is_routed is False
    assert route.execution_class == "none"
    assert route.fallback_allowed is False

def test_routing_determinism(base_planning_result: PlanningResult):
    decision = PolicyDecision(
        planning_result=base_planning_result,
        is_approved=True,
        policy_mode="locality_preferred",
        fallback_allowed=False,
        constraints=()
    )
    
    engine = RoutingEngine()
    route1 = engine.evaluate(decision)
    route2 = engine.evaluate(decision)
    
    assert route1 == route2
    assert route1.execution_class == "abstract_local"
    assert route1.fallback_allowed is False

def test_routing_immutability(base_planning_result: PlanningResult):
    decision = PolicyDecision(
        planning_result=base_planning_result,
        is_approved=True,
        policy_mode="cost_constrained",
        fallback_allowed=True,
        constraints=()
    )
    
    engine = RoutingEngine()
    route = engine.evaluate(decision)
    
    with pytest.raises(FrozenInstanceError):
        route.execution_class = "mutated"  # type: ignore

def test_payload_opacity_and_neutrality(base_planning_result: PlanningResult):
    # Verify the abstraction itself prevents payload manipulation
    decision = PolicyDecision(
        planning_result=base_planning_result,
        is_approved=True,
        policy_mode="balanced",
        fallback_allowed=True,
        constraints=()
    )
    
    engine = RoutingEngine()
    route = engine.evaluate(decision)
    
    # We just ensure the engine didn't look at it or mutate it
    assert route.policy_decision.planning_result.intent.payload["data"] == "opaque"
