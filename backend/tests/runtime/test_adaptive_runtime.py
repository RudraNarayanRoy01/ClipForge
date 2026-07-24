import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.adaptive_runtime import (
    AdaptiveRuntime,
    AdaptationDecision,
    StageAdaptationDecision,
    AdaptationStatus
)
from src.runtime.core.execution_engine import (
    ExecutionResult,
    StageExecutionResult,
    ExecutionStatus
)
from src.runtime.core.context import RuntimeContext


def test_adaptation_decision_immutability():
    """Ensure AdaptationDecision cannot be modified after creation."""
    decision = AdaptationDecision(session_id="test-session")
    
    with pytest.raises(FrozenInstanceError):
        decision.session_id = "new-session"  # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        decision.status = AdaptationStatus.ADAPT  # type: ignore


def test_stage_adaptation_decision_immutability():
    """Ensure StageAdaptationDecision cannot be modified after creation."""
    decision = StageAdaptationDecision(
        stage_identifier="stage-1",
        stage_name="Test Stage",
        status=AdaptationStatus.NO_CHANGE
    )
    
    with pytest.raises(FrozenInstanceError):
        decision.status = AdaptationStatus.ADAPT  # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        decision.stage_name = "New Name"  # type: ignore


def test_runtime_context_exposes_adaptive_runtime():
    """Ensure RuntimeContext owns and exposes AdaptiveRuntime."""
    context = RuntimeContext()
    
    # Verify the subsystem exists
    assert context.adaptive_runtime is not None
    assert isinstance(context.adaptive_runtime, AdaptiveRuntime)


def test_adaptive_runtime_consumes_execution_result():
    """Ensure AdaptiveRuntime consumes ExecutionResult and produces AdaptationDecision."""
    adaptive_runtime = AdaptiveRuntime()
    
    # Create an immutable execution result mock
    execution_result = ExecutionResult(
        session_id="session-123",
        stage_results=[
            StageExecutionResult(
                stage_identifier="stage-1",
                stage_name="Extraction",
                status=ExecutionStatus.COMPLETED
            ),
            StageExecutionResult(
                stage_identifier="stage-2",
                stage_name="Analysis",
                status=ExecutionStatus.FAILED
            )
        ],
        status=ExecutionStatus.FAILED
    )
    
    # Consume result
    adaptation_decision = adaptive_runtime.evaluate_execution(execution_result)
    
    # Verify output
    assert isinstance(adaptation_decision, AdaptationDecision)
    assert adaptation_decision.session_id == "session-123"
    assert adaptation_decision.status == AdaptationStatus.ADAPT
    assert len(adaptation_decision.stage_decisions) == 2
    
    # Verify stage 1 decision
    stage_1_decision = adaptation_decision.stage_decisions[0]
    assert stage_1_decision.stage_identifier == "stage-1"
    assert stage_1_decision.status == AdaptationStatus.NO_CHANGE
    
    # Verify stage 2 decision
    stage_2_decision = adaptation_decision.stage_decisions[1]
    assert stage_2_decision.stage_identifier == "stage-2"
    assert stage_2_decision.status == AdaptationStatus.ADAPT
    
    # Verify ExecutionResult remains completely unchanged
    assert execution_result.session_id == "session-123"
    assert execution_result.status == ExecutionStatus.FAILED
    assert len(execution_result.stage_results) == 2


def test_adaptation_decision_contains_adaptation_information_only():
    """
    Ensure Adaptation artifacts do not contain monitoring, optimization,
    learning, scheduling, provider, or allocation information.
    """
    decision = AdaptationDecision(session_id="test")
    stage_decision = StageAdaptationDecision(
        stage_identifier="s1",
        stage_name="s",
        status=AdaptationStatus.DEFER
    )
    
    # Assert absence of prohibited properties (using hasattr to enforce architectural rules)
    assert not hasattr(decision, "metrics")
    assert not hasattr(decision, "monitoring")
    assert not hasattr(decision, "optimization")
    assert not hasattr(decision, "learning")
    assert not hasattr(decision, "scheduling")
    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "allocation")
    assert not hasattr(decision, "hardware")
    
    assert not hasattr(stage_decision, "metrics")
    assert not hasattr(stage_decision, "monitoring")
    assert not hasattr(stage_decision, "optimization")
    assert not hasattr(stage_decision, "benchmarks")
