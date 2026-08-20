import pytest
from unittest.mock import Mock

from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.runtime.invocation.runtime_pipeline import RuntimePipeline
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_engine import ExecutionEngine
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.execution_result import ExecutionResult

def test_facade_invokes_pipeline_boundary_and_engine_in_order():
    """Test that the facade passes the exact objects between boundaries in order."""
    # 1. Setup mocks
    mock_pipeline = Mock(spec=RuntimePipeline)
    mock_boundary = Mock(spec=RuntimeExecutionBoundary)
    mock_engine = Mock(spec=ExecutionEngine)
    
    # Setup stubs for data passing
    sentinel_intent = Mock(spec=ExecutionIntent)
    sentinel_context = Mock(spec=PlanningContext)
    sentinel_targets = []
    
    sentinel_target = Mock(spec=ExecutionTarget)
    sentinel_admission = Mock(spec=ExecutionAdmission)
    sentinel_result = Mock(spec=ExecutionResult)
    
    mock_pipeline.process.return_value = sentinel_target
    mock_boundary.execute.return_value = sentinel_admission
    mock_engine.execute.return_value = sentinel_result
    
    # 2. Execute
    facade = RuntimeInvocationFacade(
        pipeline=mock_pipeline,
        boundary=mock_boundary,
        engine=mock_engine
    )
    
    result = facade.invoke(
        intent=sentinel_intent,
        planning_context=sentinel_context,
        available_targets=sentinel_targets
    )
    
    # 3. Verify ordering and identity
    # Pipeline is invoked with correct args
    mock_pipeline.process.assert_called_once_with(
        intent=sentinel_intent,
        planning_context=sentinel_context,
        available_targets=sentinel_targets
    )
    
    # Boundary is invoked with exact target from pipeline
    mock_boundary.execute.assert_called_once_with(
        target=sentinel_target,
        intent=sentinel_intent
    )
    
    # Engine is invoked with exact admission from boundary
    mock_engine.execute.assert_called_once_with(
        admission=sentinel_admission
    )
    
    # Result is exact result from engine
    assert result is sentinel_result

def test_facade_raises_value_error_if_pipeline_returns_no_target():
    """Test that the facade rejects execution if decision pipeline yields no target."""
    mock_pipeline = Mock(spec=RuntimePipeline)
    mock_boundary = Mock(spec=RuntimeExecutionBoundary)
    mock_engine = Mock(spec=ExecutionEngine)
    
    mock_pipeline.process.return_value = None
    
    facade = RuntimeInvocationFacade(
        pipeline=mock_pipeline,
        boundary=mock_boundary,
        engine=mock_engine
    )
    
    with pytest.raises(ValueError, match="No compatible execution target found by decision pipeline."):
        facade.invoke(
            intent=Mock(spec=ExecutionIntent),
            planning_context=Mock(spec=PlanningContext),
            available_targets=[]
        )
        
    mock_boundary.execute.assert_not_called()
    mock_engine.execute.assert_not_called()
