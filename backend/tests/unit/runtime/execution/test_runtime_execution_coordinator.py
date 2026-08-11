import pytest
from unittest.mock import Mock

from src.runtime.core.executor import RuntimeExecutor
from src.runtime.core.scheduling_model import SchedulingDecision, SchedulingStatus
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_coordinator import RuntimeExecutionCoordinator


def test_coordinator_accepted_decision_invokes_executor():
    """Test 1: Accepted decision invokes Executor."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    mock_result = Mock(spec=RuntimeExecutionResult)
    mock_executor.execute.return_value = mock_result
    
    result = coordinator.coordinate(mock_decision, mock_identity)
    
    mock_executor.execute.assert_called_once()
    assert result is mock_result


def test_coordinator_exact_scheduling_decision_propagation():
    """Test 2: Exact SchedulingDecision propagation."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    coordinator.coordinate(mock_decision, mock_identity)
    
    # Assert exact reference
    args, kwargs = mock_executor.execute.call_args
    assert kwargs.get('scheduling_decision') is mock_decision


def test_coordinator_exact_identity_propagation():
    """Test 3: Exact Identity propagation."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    coordinator.coordinate(mock_decision, mock_identity)
    
    # Assert exact reference
    args, kwargs = mock_executor.execute.call_args
    assert kwargs.get('identity') is mock_identity


def test_coordinator_result_preservation():
    """Test 4: Result preservation."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    mock_result = Mock(spec=RuntimeExecutionResult)
    mock_executor.execute.return_value = mock_result
    
    returned_result = coordinator.coordinate(mock_decision, mock_identity)
    
    assert returned_result is mock_result


@pytest.mark.parametrize("status", [
    SchedulingStatus.QUEUED,
    SchedulingStatus.DEFERRED,
    SchedulingStatus.BLOCKED,
    SchedulingStatus.REJECTED
])
def test_coordinator_non_executable_decision(status):
    """Test 5: Non-executable decision produces no result and does not call executor."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = status
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    returned_result = coordinator.coordinate(mock_decision, mock_identity)
    
    assert returned_result is None
    mock_executor.execute.assert_not_called()


def test_coordinator_failed_result_preservation():
    """Test 6: FAILED result preservation."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    mock_result = Mock(spec=RuntimeExecutionResult)
    mock_result.outcome = RuntimeExecutionOutcome.FAILED
    mock_executor.execute.return_value = mock_result
    
    returned_result = coordinator.coordinate(mock_decision, mock_identity)
    
    assert returned_result is mock_result
    assert returned_result.outcome == RuntimeExecutionOutcome.FAILED


def test_coordinator_success_result_preservation():
    """Test 7: SUCCESS result preservation."""
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    mock_result = Mock(spec=RuntimeExecutionResult)
    mock_result.outcome = RuntimeExecutionOutcome.SUCCESS
    mock_executor.execute.return_value = mock_result
    
    returned_result = coordinator.coordinate(mock_decision, mock_identity)
    
    assert returned_result is mock_result
    assert returned_result.outcome == RuntimeExecutionOutcome.SUCCESS


def test_coordinator_no_duplicate_failure_translation():
    """
    Test 8: No duplicate failure translation occurs.
    The Coordinator simply passes exceptions upstream if the Executor raises them,
    it does not catch them and manufacture results.
    """
    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)
    
    mock_decision = Mock(spec=SchedulingDecision)
    mock_decision.status = SchedulingStatus.READY
    mock_identity = Mock(spec=RuntimeExecutionIdentity)
    
    expected_exception = RuntimeError("Executor failure")
    mock_executor.execute.side_effect = expected_exception
    
    with pytest.raises(RuntimeError) as exc_info:
        coordinator.coordinate(mock_decision, mock_identity)
        
    assert exc_info.value is expected_exception


def test_coordinator_architectural_dependency():
    """
    Test 9: Architectural dependency test.
    Ensure Coordinator has no Application/Infrastructure/Provider imports.
    """
    import ast
    import pathlib
    
    coordinator_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent / "src" / "runtime" / "execution" / "runtime_execution_coordinator.py"
    with open(coordinator_path, "r") as f:
        tree = ast.parse(f.read())
        
    forbidden_modules = ["application", "infrastructure", "provider", "ffmpeg", "moviepy", "http", "requests", "api", "ui"]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_modules:
                    assert forbidden not in alias.name.lower(), f"Forbidden module {forbidden} imported."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in forbidden_modules:
                    assert forbidden not in node.module.lower(), f"Forbidden module {forbidden} imported."


def test_coordinator_real_scheduling_decision_and_identity():
    """
    Test 10 & 11: Real SchedulingDecision and RuntimeExecutionIdentity test.
    Constructs actual objects using canonical classes and verifies they reach
    the executor identically.
    """
    import time
    from datetime import datetime
    from src.runtime.core.scheduling_model import (
        SchedulingDecision, SchedulingIdentity, SchedulingPriority, 
        SchedulingPolicy, SchedulingStrategy, QueueClassification, SchedulingStatus
    )
    from src.runtime.core.execution_model import ExecutionIdentity
    from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
    from src.runtime.execution.runtime_execution_descriptor import RuntimeExecutionDescriptor
    from src.runtime.execution.runtime_execution_metadata import RuntimeExecutionMetadata
    from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
    from src.runtime.execution.runtime_execution_snapshot import RuntimeExecutionSnapshot
    from types import MappingProxyType

    mock_executor = Mock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor=mock_executor)

    # Construct real SchedulingDecision
    real_decision = SchedulingDecision(
        identity=SchedulingIdentity(
            schedule_id="sched-123",
            created_at=time.time(),
            execution_identity=ExecutionIdentity(
                execution_id="exec-123",
                created_at=time.time()
            )
        ),
        execution_identity=ExecutionIdentity(
            execution_id="exec-123",
            created_at=time.time()
        ),
        status=SchedulingStatus.READY,  # Eligible status
        priority=SchedulingPriority.NORMAL,
        policy=SchedulingPolicy.IMMEDIATE,
        strategy=SchedulingStrategy.FIFO,
        queue_classification=QueueClassification.BACKGROUND,
        scheduling_timestamp=time.time(),
        scheduling_reasoning="Unit test execution"
    )

    # Construct real RuntimeExecutionIdentity
    real_identity = RuntimeExecutionIdentity(
        descriptor=RuntimeExecutionDescriptor(
            execution_id="exec-123",
            runtime_id="rt-123",
            bootstrap_id="boot-123",
            version="1.0",
            schema_version="1.0"
        ),
        metadata=RuntimeExecutionMetadata(
            name="test-exec",
            description="test description",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=frozenset(["test"]),
            annotations=MappingProxyType({}),
            metadata_version="1.0"
        ),
        status=RuntimeExecutionStatus.READY,
        snapshot=RuntimeExecutionSnapshot(
            execution_hash="exec_hash",
            identity_hash="id_hash",
            descriptor_hash="desc_hash",
            metadata_hash="meta_hash",
            state_hash="state_hash",
            composition_hash="comp_hash"
        )
    )

    coordinator.coordinate(real_decision, real_identity)

    # Verify identical instances reached the executor
    args, kwargs = mock_executor.execute.call_args
    assert kwargs.get('scheduling_decision') is real_decision
    assert kwargs.get('identity') is real_identity
