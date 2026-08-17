import pytest
import dataclasses
from src.runtime.core.planning_context import PlanningContext

def test_planning_context_default_construction():
    context = PlanningContext()
    assert context.quality_preference == "balanced"
    assert context.latency_preference == "standard"
    assert context.cost_preference == "balanced"
    assert context.locality_preference == "agnostic"
    assert context.constraints == ()

def test_planning_context_field_preservation():
    context = PlanningContext(
        quality_preference="quality",
        latency_preference="low",
        cost_preference="economy",
        locality_preference="local",
        constraints=("require_secure_enclave", "prefer_green_energy")
    )
    assert context.quality_preference == "quality"
    assert context.latency_preference == "low"
    assert context.cost_preference == "economy"
    assert context.locality_preference == "local"
    assert context.constraints == ("require_secure_enclave", "prefer_green_energy")

def test_planning_context_structural_immutability():
    context = PlanningContext()
    # Explicitly test that every field is frozen using the exact expected exception type
    with pytest.raises(dataclasses.FrozenInstanceError):
        context.quality_preference = "high"
        
    with pytest.raises(dataclasses.FrozenInstanceError):
        context.latency_preference = "low"
        
    with pytest.raises(dataclasses.FrozenInstanceError):
        context.cost_preference = "economy"
        
    with pytest.raises(dataclasses.FrozenInstanceError):
        context.locality_preference = "local"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        context.constraints = ("new_constraint",)

def test_planning_context_constraints_semantics():
    # Verify that the default is ()
    context = PlanningContext()
    assert context.constraints == ()
    assert isinstance(context.constraints, tuple)
    
    # Verify that supplied tuple values and ordering are preserved exactly
    custom_constraints = ("first_constraint", "second_constraint", "third_constraint")
    context_custom = PlanningContext(constraints=custom_constraints)
    assert context_custom.constraints == custom_constraints
    assert context_custom.constraints[0] == "first_constraint"
    assert context_custom.constraints[2] == "third_constraint"
    
    # Verify no mutable collection is exposed (tuple has no append)
    assert not hasattr(context_custom.constraints, "append")

def test_planning_context_distinction_from_intent_and_result():
    context = PlanningContext()
    # Ensure it lacks fields belonging to ExecutionIntent
    assert not hasattr(context, "intent")
    assert not hasattr(context, "capability_id")
    assert not hasattr(context, "payload")
    assert not hasattr(context, "output_contract")
    # Ensure it lacks fields belonging to PlanningResult
    assert not hasattr(context, "strategy")
    assert not hasattr(context, "requirements")

def test_planning_context_infrastructure_neutrality():
    context = PlanningContext()
    # Ensure no infrastructure fields slipped in
    assert not hasattr(context, "provider")
    assert not hasattr(context, "model")
    assert not hasattr(context, "hardware")
    assert not hasattr(context, "gpu")
    assert not hasattr(context, "cuda")
    assert not hasattr(context, "queue")
    assert not hasattr(context, "scheduler")
    assert not hasattr(context, "executor")
    assert not hasattr(context, "telemetry")
    assert not hasattr(context, "metrics")

