import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.runtime_budget_planner import BudgetDecision
from src.runtime.core.runtime_routing import RoutingDecision, RuntimeRouting
from src.runtime.core.context import RuntimeContext


def test_routing_decision_immutability():
    """Verify RoutingDecision is immutable."""
    decision = RoutingDecision(
        routing_identifier="test",
        routing_status="ESTABLISHED",
        primary_route_identifier="route-a",
        fallback_route_identifier="route-b",
        routing_rationale="Test rationale"
    )
    
    with pytest.raises(FrozenInstanceError):
        decision.routing_identifier = "mutated"
        
    with pytest.raises(FrozenInstanceError):
        decision.routing_status = "mutated"


def test_runtime_routing_consumes_budget_decision():
    """Verify RuntimeRouting consumes BudgetDecision and produces RoutingDecision."""
    engine = RuntimeRouting()
    budget_decision = BudgetDecision(
        budget_identifier="test-budget",
        budget_status="ESTABLISHED",
        budget_rationale="Available"
    )
    
    routing_decision = engine.evaluate(budget_decision)
    
    assert isinstance(routing_decision, RoutingDecision)
    assert routing_decision.routing_status == "ESTABLISHED"
    assert "evaluator" in routing_decision.routing_metadata
    assert routing_decision.routing_metadata["evaluator"] == "RuntimeRouting"
    assert routing_decision.routing_metadata["evaluated_budget"] == "test-budget"
    assert routing_decision.primary_route_identifier is not None


def test_runtime_routing_handles_unestablished_budget():
    """Verify RuntimeRouting properly handles unestablished BudgetDecision."""
    engine = RuntimeRouting()
    budget_decision = BudgetDecision(
        budget_identifier="test-budget",
        budget_status="UNAVAILABLE",
        budget_rationale="Rejected"
    )
    
    routing_decision = engine.evaluate(budget_decision)
    
    assert isinstance(routing_decision, RoutingDecision)
    assert routing_decision.routing_status == "UNAVAILABLE"
    assert routing_decision.primary_route_identifier == "NONE"


def test_runtime_context_ownership():
    """Verify RuntimeContext owns RuntimeRouting."""
    context = RuntimeContext()
    
    assert hasattr(context, "runtime_routing")
    assert isinstance(context.runtime_routing, RuntimeRouting)


def test_routing_decision_purity():
    """Verify RoutingDecision does not contain execution, scheduling, budget, or provider information."""
    decision = RoutingDecision(
        routing_identifier="test",
        routing_status="ESTABLISHED",
        primary_route_identifier="route-a",
        fallback_route_identifier="route-b",
        routing_rationale="Test rationale"
    )
    
    # Assert restricted fields do NOT exist
    assert not hasattr(decision, "budget_values")
    assert not hasattr(decision, "execution_commands")
    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "hardware")
    assert not hasattr(decision, "scheduler")
    assert not hasattr(decision, "optimization")
    assert not hasattr(decision, "execution_state")
    assert not hasattr(decision, "retry_state")


def test_provider_and_hardware_independence():
    """Verify routing layer has no hardcoded provider or hardware references."""
    engine = RuntimeRouting()
    
    # Simple reflection check (though source code audit is better)
    engine_dir = dir(engine)
    for attr in engine_dir:
        assert "gemini" not in attr.lower()
        assert "openai" not in attr.lower()
        assert "cuda" not in attr.lower()
        assert "gpu" not in attr.lower()


def test_fallback_contract_structure():
    """
    Verify RoutingDecision contains the architectural fallback contract.
    """
    decision = RoutingDecision(
        routing_identifier="contract-test",
        routing_status="ESTABLISHED",
        primary_route_identifier="primary-a",
        fallback_route_identifier="fallback-b",
        routing_rationale="Verified fallback contract"
    )
    
    # Verify both primary and fallback route identifiers exist
    assert hasattr(decision, "primary_route_identifier")
    assert hasattr(decision, "fallback_route_identifier")
    assert decision.primary_route_identifier == "primary-a"
    assert decision.fallback_route_identifier == "fallback-b"


def test_routing_decision_reusability_contract():
    """
    Verify RoutingDecision represents a reusable artifact for future layers
    (RuntimeScheduler, RuntimeExecution).
    This is an architectural unit test ensuring the artifact matches the schema.
    """
    decision = RoutingDecision(
        routing_identifier="reusable",
        routing_status="ESTABLISHED",
        primary_route_identifier="primary",
        fallback_route_identifier="fallback",
        routing_rationale="Verified reusable"
    )
    
    # These attributes are all that future layers need to read routing decisions.
    assert hasattr(decision, "routing_identifier")
    assert hasattr(decision, "routing_status")
    assert hasattr(decision, "primary_route_identifier")
    assert hasattr(decision, "fallback_route_identifier")
    assert hasattr(decision, "routing_rationale")
    assert hasattr(decision, "routing_assumptions")
    assert hasattr(decision, "routing_metadata")
