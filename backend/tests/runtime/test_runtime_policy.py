import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.runtime_planning import PlanningDecision
from src.runtime.core.runtime_policy import PolicyDecision, RuntimePolicy
from src.runtime.core.context import RuntimeContext

def test_policy_decision_immutability():
    """Verify that PolicyDecision is immutable."""
    decision = PolicyDecision(
        policy_identifier="test-policy",
        approval_status="APPROVED",
        evaluation_rationale="test rationale"
    )
    with pytest.raises(FrozenInstanceError):
        decision.approval_status = "DENIED"
    with pytest.raises(FrozenInstanceError):
        decision.evaluation_rationale = "changed rationale"

def test_runtime_policy_produces_policy_decision():
    """Verify RuntimePolicy consumes PlanningDecision and produces PolicyDecision."""
    policy = RuntimePolicy()
    planning_decision = PlanningDecision(
        session_id="test-session",
        planning_objective="test-objective",
        planning_rationale="test-rationale"
    )
    decision = policy.evaluate(planning_decision)
    assert isinstance(decision, PolicyDecision)
    assert decision.approval_status == "APPROVED"
    assert "architecturally permitted" in decision.evaluation_rationale

def test_runtime_context_ownership():
    """Verify RuntimeContext owns RuntimePolicy."""
    context = RuntimeContext()
    assert isinstance(context.runtime_policy, RuntimePolicy)

def test_provider_and_hardware_independence():
    """Verify no provider or hardware details exist in the interface."""
    decision = PolicyDecision(
        policy_identifier="test-policy",
        approval_status="APPROVED",
        evaluation_rationale="test rationale"
    )
    assert not hasattr(decision, 'provider')
    assert not hasattr(decision, 'hardware')
    assert not hasattr(decision, 'gemini')
    assert not hasattr(decision, 'cuda')
    assert not hasattr(decision, 'provider_selection')
    assert not hasattr(decision, 'hardware_decisions')

def test_policy_decision_purity():
    """Verify PolicyDecision doesn't embed PlanningDecision or other future concepts."""
    decision = PolicyDecision(
        policy_identifier="test-policy",
        approval_status="APPROVED",
        evaluation_rationale="test rationale",
        policy_metadata={"test": "data"}
    )
    assert not hasattr(decision, 'planning_decision')
    assert not hasattr(decision, 'budget')
    assert not hasattr(decision, 'constraint')
    assert not hasattr(decision, 'routing')
    assert not hasattr(decision, 'scheduling')
    assert not hasattr(decision, 'execution_commands')
    assert not hasattr(decision, 'resource_allocation')

def test_dependency_direction():
    """Verify invalid PlanningDecision results in DENIED PolicyDecision."""
    policy = RuntimePolicy()
    planning_decision = PlanningDecision(
        session_id="invalid",
        planning_objective="test",
        planning_rationale="test"
    )
    decision = policy.evaluate(planning_decision)
    assert isinstance(decision, PolicyDecision)
    assert decision.approval_status == "DENIED"
    assert "Invalid" in decision.evaluation_rationale

def test_policy_decision_reusability():
    """Verify that PolicyDecision can be theoretically reused without mutation."""
    decision = PolicyDecision(
        policy_identifier="test-policy",
        approval_status="APPROVED",
        evaluation_rationale="test rationale",
        evaluation_assumptions=["Test Assumption"]
    )
    
    # Simulate consumption by multiple theoretical future subsystems (Constraint Engine, Budget Planner, etc.)
    consumer_a_assumptions = list(decision.evaluation_assumptions)
    consumer_b_assumptions = list(decision.evaluation_assumptions)
    
    consumer_a_assumptions.append("Constraint Check Passed")
    consumer_b_assumptions.append("Budget Check Passed")
    
    # Ensure the original decision remains unchanged and reusable
    assert decision.evaluation_assumptions == ["Test Assumption"]
    assert len(decision.evaluation_assumptions) == 1
