import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.runtime_policy import PolicyDecision
from src.runtime.core.runtime_constraint_engine import ConstraintDecision, RuntimeConstraintEngine
from src.runtime.core.context import RuntimeContext


def test_constraint_decision_immutability():
    """Verify ConstraintDecision is immutable."""
    decision = ConstraintDecision(
        constraint_identifier="test",
        constraint_status="ESTABLISHED",
        constraint_rationale="Test rationale"
    )
    
    with pytest.raises(FrozenInstanceError):
        decision.constraint_identifier = "mutated"
        
    with pytest.raises(FrozenInstanceError):
        decision.constraint_status = "mutated"


def test_runtime_constraint_engine_consumes_policy_decision():
    """Verify RuntimeConstraintEngine consumes PolicyDecision and produces ConstraintDecision."""
    engine = RuntimeConstraintEngine()
    policy_decision = PolicyDecision(
        policy_identifier="test-policy",
        approval_status="APPROVED",
        evaluation_rationale="Permitted"
    )
    
    constraint_decision = engine.evaluate(policy_decision)
    
    assert isinstance(constraint_decision, ConstraintDecision)
    assert constraint_decision.constraint_status == "ESTABLISHED"
    assert "evaluator" in constraint_decision.constraint_metadata
    assert constraint_decision.constraint_metadata["evaluator"] == "RuntimeConstraintEngine"
    assert constraint_decision.constraint_metadata["evaluated_policy"] == "test-policy"


def test_runtime_constraint_engine_handles_unapproved_policy():
    """Verify RuntimeConstraintEngine properly handles unapproved PolicyDecision."""
    engine = RuntimeConstraintEngine()
    policy_decision = PolicyDecision(
        policy_identifier="test-policy",
        approval_status="DENIED",
        evaluation_rationale="Rejected"
    )
    
    constraint_decision = engine.evaluate(policy_decision)
    
    assert isinstance(constraint_decision, ConstraintDecision)
    assert constraint_decision.constraint_status == "UNSATISFIABLE"


def test_runtime_context_ownership():
    """Verify RuntimeContext owns RuntimeConstraintEngine."""
    context = RuntimeContext()
    
    assert hasattr(context, "runtime_constraint_engine")
    assert isinstance(context.runtime_constraint_engine, RuntimeConstraintEngine)


def test_constraint_decision_purity():
    """Verify ConstraintDecision does not contain execution, budget, routing, or provider information."""
    decision = ConstraintDecision(
        constraint_identifier="test",
        constraint_status="ESTABLISHED",
        constraint_rationale="Test rationale"
    )
    
    # Assert restricted fields do NOT exist
    assert not hasattr(decision, "budget")
    assert not hasattr(decision, "routing")
    assert not hasattr(decision, "execution_commands")
    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "hardware")
    assert not hasattr(decision, "scheduler")
    assert not hasattr(decision, "optimization")


def test_provider_and_hardware_independence():
    """Verify constraint layer has no hardcoded provider or hardware references."""
    engine = RuntimeConstraintEngine()
    
    # Simple reflection check (though source code audit is better)
    engine_dir = dir(engine)
    for attr in engine_dir:
        assert "gemini" not in attr.lower()
        assert "openai" not in attr.lower()
        assert "cuda" not in attr.lower()
        assert "gpu" not in attr.lower()


def test_constraint_reusability_contract():
    """
    Verify ConstraintDecision represents a reusable artifact for future layers
    (Budget, Routing, Scheduler, Execution).
    This is an architectural unit test ensuring the artifact matches the schema.
    """
    decision = ConstraintDecision(
        constraint_identifier="reusable",
        constraint_status="ESTABLISHED",
        constraint_rationale="Verified reusable"
    )
    
    # These attributes are all that future layers need to read constraints.
    assert hasattr(decision, "constraint_identifier")
    assert hasattr(decision, "constraint_status")
    assert hasattr(decision, "constraint_rationale")
    assert hasattr(decision, "constraint_assumptions")
    assert hasattr(decision, "constraint_metadata")
