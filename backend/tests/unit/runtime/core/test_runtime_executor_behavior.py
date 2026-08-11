import pytest
import time
from datetime import datetime
from unittest.mock import patch
from types import MappingProxyType

from src.runtime.core.executor import RuntimeExecutor
from src.runtime.core.scheduling_model import (
    SchedulingDecision,
    SchedulingIdentity,
    SchedulingStatus,
    SchedulingPolicy,
    SchedulingStrategy,
    SchedulingPriority,
    QueueClassification
)
from src.runtime.core.execution_model import ExecutionIdentity

from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus

from src.runtime.execution.runtime_execution_descriptor import RuntimeExecutionDescriptor
from src.runtime.execution.runtime_execution_metadata import RuntimeExecutionMetadata
from src.runtime.execution.runtime_execution_snapshot import RuntimeExecutionSnapshot


@pytest.fixture
def scheduling_decision():
    exec_id = ExecutionIdentity(execution_id="exec_123", created_at=time.time())
    sched_id = SchedulingIdentity(
        schedule_id="sch_456",
        created_at=time.time(),
        execution_identity=exec_id
    )
    return SchedulingDecision(
        identity=sched_id,
        execution_identity=exec_id,
        status=SchedulingStatus.READY,
        priority=SchedulingPriority.NORMAL,
        policy=SchedulingPolicy.IMMEDIATE,
        strategy=SchedulingStrategy.FIFO,
        queue_classification=QueueClassification.BACKGROUND,
        scheduling_timestamp=time.time(),
        scheduling_reasoning="test"
    )

@pytest.fixture
def runtime_identity():
    descriptor = RuntimeExecutionDescriptor(
        execution_id="exec_123",
        runtime_id="rt_456",
        bootstrap_id="boot_789",
        version="1.0",
        schema_version="1.0"
    )
    metadata = RuntimeExecutionMetadata(
        name="test_execution",
        description="A test execution",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        tags=frozenset(["test"]),
        annotations=MappingProxyType({"env": "test"}),
        metadata_version="1.0"
    )
    snapshot = RuntimeExecutionSnapshot(
        execution_hash="hash1",
        identity_hash="hash2",
        descriptor_hash="hash3",
        metadata_hash="hash4",
        state_hash="hash5",
        composition_hash="hash6"
    )
    return RuntimeExecutionIdentity(
        descriptor=descriptor,
        metadata=metadata,
        status=RuntimeExecutionStatus.PREPARED,
        snapshot=snapshot
    )


def test_executor_success(scheduling_decision, runtime_identity):
    executor = RuntimeExecutor()
    
    result = executor.execute(scheduling_decision, runtime_identity)
    
    assert isinstance(result, RuntimeExecutionResult)
    assert result.outcome == RuntimeExecutionOutcome.SUCCESS
    assert result.failure_reason is None
    assert result.identity is runtime_identity
    
    assert isinstance(result.started_at, datetime)
    assert isinstance(result.completed_at, datetime)
    assert result.completed_at >= result.started_at
    assert result.duration_seconds >= 0.0


def test_executor_failure(scheduling_decision, runtime_identity):
    executor = RuntimeExecutor()
    
    with patch.object(executor, "_execute_attempt", side_effect=RuntimeError("Test error")):
        result = executor.execute(scheduling_decision, runtime_identity)
        
        assert isinstance(result, RuntimeExecutionResult)
        assert result.outcome == RuntimeExecutionOutcome.FAILED
        assert result.failure_reason == "Execution failed: RuntimeError - Test error"
        assert result.identity is runtime_identity
        
        # Verify raw exception is NOT present in the result
        assert not hasattr(result, "exception")
        assert not hasattr(result, "traceback")
        assert "RuntimeError" not in str(result.metadata)
        
        assert isinstance(result.started_at, datetime)
        assert isinstance(result.completed_at, datetime)
        assert result.completed_at >= result.started_at
        assert result.duration_seconds >= 0.0


def test_executor_missing_decision(runtime_identity):
    executor = RuntimeExecutor()
    
    with patch.object(executor, "_execute_attempt") as mock_execute:
        with pytest.raises(ValueError, match="scheduling_decision is required"):
            executor.execute(None, runtime_identity)
            
        mock_execute.assert_not_called()


def test_executor_missing_identity(scheduling_decision):
    executor = RuntimeExecutor()
    
    with patch.object(executor, "_execute_attempt") as mock_execute:
        with pytest.raises(ValueError, match="identity is required"):
            executor.execute(scheduling_decision, None)
            
        mock_execute.assert_not_called()
