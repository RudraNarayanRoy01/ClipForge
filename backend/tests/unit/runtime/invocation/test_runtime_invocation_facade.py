import pytest
from unittest.mock import Mock, call

from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.runtime.invocation.runtime_pipeline import RuntimePipeline
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_engine import ExecutionEngine
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_target import ExecutionTarget, TargetDescription
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.execution_result import ExecutionResult, ExecutionOutcome
from src.runtime.execution.workload_normalizer import WorkloadNormalizationError
from src.runtime.execution.workload_normalization_extension import NormalizerResolutionError
from src.runtime.core.providers import RuntimeProviderRegistry

def _create_mock_registry():
    mock_registry = Mock(spec=RuntimeProviderRegistry)
    
    # Create two dummy provider registrations
    reg1 = Mock()
    reg1.descriptor.identity.identifier = "provider_a"
    reg1.descriptor.category.value = "local"
    
    reg2 = Mock()
    reg2.descriptor.identity.identifier = "provider_b"
    reg2.descriptor.category.value = "remote"
    
    mock_registry.enumerate_providers.return_value = [reg1, reg2]
    return mock_registry

def test_facade_invokes_pipeline_boundary_and_engine_in_order():
    """Test that the facade passes the exact objects between boundaries in order."""
    # 1. Setup mocks
    mock_pipeline = Mock(spec=RuntimePipeline)
    mock_boundary = Mock(spec=RuntimeExecutionBoundary)
    mock_engine = Mock(spec=ExecutionEngine)
    mock_registry = _create_mock_registry()
    
    # Setup stubs for data passing
    sentinel_intent = Mock(spec=ExecutionIntent)
    sentinel_context = Mock(spec=PlanningContext)
    
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
        engine=mock_engine,
        provider_registry=mock_registry
    )
    
    result = facade.invoke(
        intent=sentinel_intent,
        planning_context=sentinel_context
    )
    
    # 3. Verify ordering and identity
    # Pipeline is invoked with correct args and constructed targets
    expected_targets = [
        TargetDescription(target_id="provider_a", target_class="local", provider="provider_a"),
        TargetDescription(target_id="provider_b", target_class="remote", provider="provider_b")
    ]
    mock_pipeline.process.assert_called_once_with(
        intent=sentinel_intent,
        planning_context=sentinel_context,
        available_targets=expected_targets
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

def test_facade_returns_rejected_if_pipeline_returns_no_target():
    """Test that the facade rejects execution if decision pipeline yields no target."""
    mock_pipeline = Mock(spec=RuntimePipeline)
    mock_boundary = Mock(spec=RuntimeExecutionBoundary)
    mock_engine = Mock(spec=ExecutionEngine)
    mock_registry = _create_mock_registry()
    
    mock_pipeline.process.return_value = None
    
    facade = RuntimeInvocationFacade(
        pipeline=mock_pipeline,
        boundary=mock_boundary,
        engine=mock_engine,
        provider_registry=mock_registry
    )
    
    result = facade.invoke(
        intent=Mock(spec=ExecutionIntent),
        planning_context=Mock(spec=PlanningContext)
    )
        
    assert isinstance(result, ExecutionResult)
    assert result.outcome == ExecutionOutcome.REJECTED
    assert result.execution_target is None
    assert "No compatible execution target" in result.error_message
    
    mock_boundary.execute.assert_not_called()
    mock_engine.execute.assert_not_called()


def test_facade_returns_rejected_if_boundary_fails_normalization():
    mock_pipeline = Mock(spec=RuntimePipeline)
    mock_boundary = Mock(spec=RuntimeExecutionBoundary)
    mock_engine = Mock(spec=ExecutionEngine)
    mock_registry = _create_mock_registry()
    
    sentinel_target = Mock(spec=ExecutionTarget)
    mock_pipeline.process.return_value = sentinel_target
    mock_boundary.execute.side_effect = WorkloadNormalizationError("Bad workload")
    
    facade = RuntimeInvocationFacade(
        pipeline=mock_pipeline,
        boundary=mock_boundary,
        engine=mock_engine,
        provider_registry=mock_registry
    )
    
    result = facade.invoke(
        intent=Mock(spec=ExecutionIntent),
        planning_context=Mock(spec=PlanningContext)
    )
    
    assert isinstance(result, ExecutionResult)
    assert result.outcome == ExecutionOutcome.REJECTED
    assert result.execution_target is sentinel_target
    assert "Bad workload" in result.error_message
    
    mock_engine.execute.assert_not_called()


def test_facade_returns_rejected_if_boundary_fails_resolution():
    mock_pipeline = Mock(spec=RuntimePipeline)
    mock_boundary = Mock(spec=RuntimeExecutionBoundary)
    mock_engine = Mock(spec=ExecutionEngine)
    mock_registry = _create_mock_registry()
    
    sentinel_target = Mock(spec=ExecutionTarget)
    mock_pipeline.process.return_value = sentinel_target
    mock_boundary.execute.side_effect = NormalizerResolutionError("No normalizer")
    
    facade = RuntimeInvocationFacade(
        pipeline=mock_pipeline,
        boundary=mock_boundary,
        engine=mock_engine,
        provider_registry=mock_registry
    )
    
    result = facade.invoke(
        intent=Mock(spec=ExecutionIntent),
        planning_context=Mock(spec=PlanningContext)
    )
    
    assert isinstance(result, ExecutionResult)
    assert result.outcome == ExecutionOutcome.REJECTED
    assert result.execution_target is sentinel_target
    assert "No normalizer" in result.error_message
    
    mock_engine.execute.assert_not_called()
