import pytest
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.route_decision import RouteDecision
from src.runtime.core.policy_decision import PolicyDecision
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.execution_workload import ExecutionWorkload
from src.runtime.execution.workload_normalization_extension import WorkloadNormalizationExtensionPoint
from unittest.mock import MagicMock

def create_mock_target() -> ExecutionTarget:
    intent = ExecutionIntent(
        capability_id="cap-1",
        payload={"data": "test"}
    )
    planning_result = PlanningResult(
        intent=intent,
        strategy="strategy"
    )
    policy_decision = PolicyDecision(
        planning_result=planning_result,
        is_approved=True,
        policy_mode="strict",
        fallback_allowed=False
    )
    route_decision = RouteDecision(
        policy_decision=policy_decision,
        execution_class="local",
        is_routed=True,
        fallback_allowed=False
    )
    return ExecutionTarget(
        route_decision=route_decision,
        target_id="target-1",
        target_class="local",
        provider="dummy",
        model="dummy-model",
        compute_class="standard"
    )

def test_runtime_execution_boundary_construction():
    registry = MagicMock(spec=WorkloadNormalizationExtensionPoint)
    boundary = RuntimeExecutionBoundary(normalizer_registry=registry)
    assert isinstance(boundary, RuntimeExecutionBoundary)

def test_runtime_execution_boundary_produces_admission():
    """Verify that the boundary produces a pre-execution admission artifact, not an execution result."""
    registry = MagicMock(spec=WorkloadNormalizationExtensionPoint)
    normalizer = MagicMock()
    workload = MagicMock(spec=ExecutionWorkload)
    
    registry.get_normalizer.return_value = normalizer
    normalizer.normalize.return_value = workload
    boundary = RuntimeExecutionBoundary(normalizer_registry=registry)

    target = create_mock_target()
    intent = target.route_decision.policy_decision.planning_result.intent

    result = boundary.execute(target, intent)

    assert isinstance(result, ExecutionAdmission)
    assert not hasattr(result, 'outcome')  # Must not claim success or outcome
    assert not hasattr(result, 'is_success')
    assert result.execution_workload is workload
    registry.get_normalizer.assert_called_once_with(intent.capability_id)
    normalizer.normalize.assert_called_once_with(intent)

def test_runtime_execution_boundary_preserves_target_identity():
    registry = MagicMock(spec=WorkloadNormalizationExtensionPoint)
    normalizer = MagicMock()
    registry.get_normalizer.return_value = normalizer
    boundary = RuntimeExecutionBoundary(normalizer_registry=registry)

    target = create_mock_target()
    intent = target.route_decision.policy_decision.planning_result.intent

    result = boundary.execute(target, intent)

    assert result.execution_target is target

def test_runtime_execution_boundary_rejects_invalid_input():
    boundary = RuntimeExecutionBoundary(normalizer_registry=MagicMock())

    intent = ExecutionIntent(capability_id="c", payload="p")
    target = create_mock_target()

    with pytest.raises(TypeError):
        boundary.execute("not-a-target", intent) # type: ignore

    with pytest.raises(TypeError):
        boundary.execute(target, "not-an-intent") # type: ignore
