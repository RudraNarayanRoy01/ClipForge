import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.runtime_constraint_engine import ConstraintDecision
from src.runtime.core.runtime_budget_planner import BudgetDecision, RuntimeBudgetPlanner
from src.runtime.core.context import RuntimeContext


def test_budget_decision_immutability():
    """Verify BudgetDecision is immutable."""
    decision = BudgetDecision(
        budget_identifier="test",
        budget_status="ESTABLISHED",
        budget_rationale="Test rationale"
    )
    
    with pytest.raises(FrozenInstanceError):
        decision.budget_identifier = "mutated"
        
    with pytest.raises(FrozenInstanceError):
        decision.budget_status = "mutated"


def test_runtime_budget_planner_consumes_constraint_decision():
    """Verify RuntimeBudgetPlanner consumes ConstraintDecision and produces BudgetDecision."""
    engine = RuntimeBudgetPlanner()
    constraint_decision = ConstraintDecision(
        constraint_identifier="test-constraint",
        constraint_status="ESTABLISHED",
        constraint_rationale="Permitted"
    )
    
    budget_decision = engine.evaluate(constraint_decision)
    
    assert isinstance(budget_decision, BudgetDecision)
    assert budget_decision.budget_status == "ESTABLISHED"
    assert "evaluator" in budget_decision.budget_metadata
    assert budget_decision.budget_metadata["evaluator"] == "RuntimeBudgetPlanner"
    assert budget_decision.budget_metadata["evaluated_constraint"] == "test-constraint"


def test_runtime_budget_planner_handles_unestablished_constraint():
    """Verify RuntimeBudgetPlanner properly handles unestablished ConstraintDecision."""
    engine = RuntimeBudgetPlanner()
    constraint_decision = ConstraintDecision(
        constraint_identifier="test-constraint",
        constraint_status="UNSATISFIABLE",
        constraint_rationale="Rejected"
    )
    
    budget_decision = engine.evaluate(constraint_decision)
    
    assert isinstance(budget_decision, BudgetDecision)
    assert budget_decision.budget_status == "UNAVAILABLE"


def test_runtime_context_ownership():
    """Verify RuntimeContext owns RuntimeBudgetPlanner."""
    context = RuntimeContext()
    
    assert hasattr(context, "runtime_budget_planner")
    assert isinstance(context.runtime_budget_planner, RuntimeBudgetPlanner)


def test_budget_decision_purity():
    """Verify BudgetDecision does not contain execution, scheduling, routing, or provider information."""
    decision = BudgetDecision(
        budget_identifier="test",
        budget_status="ESTABLISHED",
        budget_rationale="Test rationale"
    )
    
    # Assert restricted fields do NOT exist
    assert not hasattr(decision, "routing")
    assert not hasattr(decision, "execution_commands")
    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "hardware")
    assert not hasattr(decision, "scheduler")
    assert not hasattr(decision, "optimization")
    assert not hasattr(decision, "constraint_definitions")
    assert not hasattr(decision, "resource_allocation")
    assert not hasattr(decision, "execution_state")


def test_provider_and_hardware_independence():
    """Verify budget layer has no hardcoded provider or hardware references."""
    engine = RuntimeBudgetPlanner()
    
    # Simple reflection check (though source code audit is better)
    engine_dir = dir(engine)
    for attr in engine_dir:
        assert "gemini" not in attr.lower()
        assert "openai" not in attr.lower()
        assert "cuda" not in attr.lower()
        assert "gpu" not in attr.lower()


def test_budget_reusability_contract():
    """
    Verify BudgetDecision represents a reusable artifact for future layers
    (Routing, Scheduler, Execution).
    This is an architectural unit test ensuring the artifact matches the schema.
    """
    decision = BudgetDecision(
        budget_identifier="reusable",
        budget_status="ESTABLISHED",
        budget_rationale="Verified reusable"
    )
    
    # These attributes are all that future layers need to read budgets.
    assert hasattr(decision, "budget_identifier")
    assert hasattr(decision, "budget_status")
    assert hasattr(decision, "budget_rationale")
    assert hasattr(decision, "budget_assumptions")
    assert hasattr(decision, "budget_metadata")
