import dataclasses
import pytest

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.policy_decision import PolicyDecision


def test_policy_decision_construction_and_identity():
    intent = ExecutionIntent(
        capability_id="test-capability",
        payload={"dummy": "data"}
    )
    result = PlanningResult(
        intent=intent,
        strategy="balanced_planning"
    )

    decision = PolicyDecision(
        planning_result=result,
        is_approved=True,
        policy_mode="balanced",
        fallback_allowed=True,
        constraints=("test_constraint",)
    )

    assert decision.planning_result is result
    assert decision.is_approved is True
    assert decision.policy_mode == "balanced"
    assert decision.fallback_allowed is True
    assert decision.constraints == ("test_constraint",)


def test_policy_decision_defaults():
    intent = ExecutionIntent(
        capability_id="test-capability",
        payload={}
    )
    result = PlanningResult(
        intent=intent,
        strategy="balanced_planning"
    )

    decision = PolicyDecision(
        planning_result=result,
        is_approved=False,
        policy_mode="custom",
        fallback_allowed=False
    )

    assert decision.constraints == ()


def test_policy_decision_immutability():
    intent = ExecutionIntent(
        capability_id="test-capability",
        payload={}
    )
    result = PlanningResult(
        intent=intent,
        strategy="balanced_planning"
    )

    decision = PolicyDecision(
        planning_result=result,
        is_approved=True,
        policy_mode="balanced",
        fallback_allowed=True
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.is_approved = False

    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.policy_mode = "changed"

    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.fallback_allowed = False

    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.constraints = ("new_constraint",)
