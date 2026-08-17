import pytest
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.route_decision import RouteDecision
from src.runtime.core.policy_decision import PolicyDecision
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.intent import ExecutionIntent

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
    boundary = RuntimeExecutionBoundary()
    assert isinstance(boundary, RuntimeExecutionBoundary)

def test_runtime_execution_boundary_produces_admission():
    """Verify that the boundary produces a pre-execution admission artifact, not an execution result."""
    boundary = RuntimeExecutionBoundary()
    target = create_mock_target()
    
    result = boundary.execute(target)
    
    assert isinstance(result, ExecutionAdmission)
    assert not hasattr(result, 'is_success')  # Must not claim success

def test_runtime_execution_boundary_preserves_target_identity():
    boundary = RuntimeExecutionBoundary()
    target = create_mock_target()
    
    result = boundary.execute(target)
    
    assert result.execution_target is target

def test_runtime_execution_boundary_rejects_invalid_input():
    boundary = RuntimeExecutionBoundary()
    
    with pytest.raises(TypeError):
        boundary.execute("not-a-target")
