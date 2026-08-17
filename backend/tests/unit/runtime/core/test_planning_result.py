import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_result import PlanningResult


def create_dummy_intent() -> ExecutionIntent:
    return ExecutionIntent(capability_id="test.capability", payload={"data": "test"})


def test_construction_and_preservation():
    """Test 1: Construction & Tests 2, 3, 4, 5: Preservation"""
    intent = create_dummy_intent()
    strategy = "remote"
    requirements = ("requires_gpu",)
    constraints = {"max_cost": 10.0}

    result = PlanningResult(
        intent=intent,
        strategy=strategy,
        requirements=requirements,
        constraints=constraints
    )

    assert result.intent is intent
    assert result.strategy == strategy
    assert result.requirements == requirements
    assert result.constraints == constraints


def test_default_collections():
    """Test 6 & 7: Default Requirements and Constraints"""
    intent = create_dummy_intent()
    result = PlanningResult(intent=intent, strategy="local")

    assert result.requirements == ()
    assert result.constraints == {}


def test_structural_immutability():
    """Test 8: Structural Immutability"""
    intent = create_dummy_intent()
    result = PlanningResult(intent=intent, strategy="local")

    with pytest.raises(FrozenInstanceError):
        result.strategy = "remote"

    with pytest.raises(FrozenInstanceError):
        result.requirements = ("new_req",)

    with pytest.raises(FrozenInstanceError):
        result.constraints = {"new": "constraint"}

    with pytest.raises(FrozenInstanceError):
        result.intent = create_dummy_intent()


def test_execution_intent_distinction():
    """Test 9: ExecutionIntent Distinction"""
    intent = create_dummy_intent()
    result = PlanningResult(intent=intent, strategy="local")

    # Verify distinct type
    assert not isinstance(result, ExecutionIntent)
    # Verify it does not inherit or replace but contains
    assert isinstance(result.intent, ExecutionIntent)

