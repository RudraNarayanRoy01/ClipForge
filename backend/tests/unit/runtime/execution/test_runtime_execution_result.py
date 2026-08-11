import pytest
from datetime import datetime, timedelta
from types import MappingProxyType
from dataclasses import FrozenInstanceError

from src.runtime.execution import (
    RuntimeExecutionResult,
    RuntimeExecutionOutcome,
    RuntimeExecutionIdentity,
    RuntimeExecutionDescriptor,
    ExecutionMetadataFactory,
    ExecutionSnapshotFactory,
)
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus

@pytest.fixture
def identity():
    desc = RuntimeExecutionDescriptor("exec-1", "run-2", "boot-3", "1.0", "1.0")
    meta = ExecutionMetadataFactory.create_metadata("Test Execution")
    status = RuntimeExecutionStatus.READY
    snap = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp")
    return RuntimeExecutionIdentity(desc, meta, status, snap)

def test_valid_success_result(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=5)
    
    res = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=start,
        completed_at=end,
        duration_seconds=5.0,
        metadata=MappingProxyType({"provider": "test"})
    )
    
    assert res.identity == identity
    assert res.outcome == RuntimeExecutionOutcome.SUCCESS
    assert res.failure_reason is None
    assert res.duration_seconds == 5.0
    assert res.metadata["provider"] == "test"

def test_valid_failed_result(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=2)
    
    res = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.FAILED,
        started_at=start,
        completed_at=end,
        duration_seconds=2.0,
        failure_reason="Timeout connecting to provider"
    )
    
    assert res.outcome == RuntimeExecutionOutcome.FAILED
    assert res.failure_reason == "Timeout connecting to provider"

def test_valid_cancelled_result(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    res_no_reason = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.CANCELLED,
        started_at=start,
        completed_at=end,
        duration_seconds=1.0,
    )
    
    assert res_no_reason.outcome == RuntimeExecutionOutcome.CANCELLED
    assert res_no_reason.failure_reason is None
    
    res_with_reason = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.CANCELLED,
        started_at=start,
        completed_at=end,
        duration_seconds=1.0,
        failure_reason="User aborted"
    )
    
    assert res_with_reason.outcome == RuntimeExecutionOutcome.CANCELLED
    assert res_with_reason.failure_reason == "User aborted"

def test_negative_duration_rejected(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    with pytest.raises(ValueError, match="negative"):
        RuntimeExecutionResult(
            identity=identity,
            outcome=RuntimeExecutionOutcome.SUCCESS,
            started_at=start,
            completed_at=end,
            duration_seconds=-1.0
        )

def test_completed_at_before_started_at_rejected(identity):
    start = datetime.utcnow()
    end = start - timedelta(seconds=1)
    
    with pytest.raises(ValueError, match="before"):
        RuntimeExecutionResult(
            identity=identity,
            outcome=RuntimeExecutionOutcome.SUCCESS,
            started_at=start,
            completed_at=end,
            duration_seconds=1.0
        )

def test_success_with_failure_reason_rejected(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    with pytest.raises(ValueError, match="SUCCESS outcome must not contain a failure_reason"):
        RuntimeExecutionResult(
            identity=identity,
            outcome=RuntimeExecutionOutcome.SUCCESS,
            started_at=start,
            completed_at=end,
            duration_seconds=1.0,
            failure_reason="Should not exist"
        )

def test_failed_missing_failure_reason_rejected(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    with pytest.raises(ValueError, match="FAILED outcome must contain a non-empty failure_reason"):
        RuntimeExecutionResult(
            identity=identity,
            outcome=RuntimeExecutionOutcome.FAILED,
            started_at=start,
            completed_at=end,
            duration_seconds=1.0
        )

def test_failed_empty_failure_reason_rejected(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    with pytest.raises(ValueError, match="FAILED outcome must contain a non-empty failure_reason"):
        RuntimeExecutionResult(
            identity=identity,
            outcome=RuntimeExecutionOutcome.FAILED,
            started_at=start,
            completed_at=end,
            duration_seconds=1.0,
            failure_reason="   "
        )

def test_metadata_immutability(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    res = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=start,
        completed_at=end,
        duration_seconds=1.0,
        metadata=MappingProxyType({"key": "value"})
    )
    
    with pytest.raises(TypeError):
        res.metadata["key"] = "new_value"

def test_result_immutability(identity):
    start = datetime.utcnow()
    end = start + timedelta(seconds=1)
    
    res = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=start,
        completed_at=end,
        duration_seconds=1.0
    )
    
    with pytest.raises(FrozenInstanceError):
        res.duration_seconds = 2.0
