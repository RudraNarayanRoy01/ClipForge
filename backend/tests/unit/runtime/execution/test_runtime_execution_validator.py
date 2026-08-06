import pytest
from src.runtime.execution import (
    RuntimeExecution,
    RuntimeExecutionIdentity,
    RuntimeExecutionDescriptor,
    RuntimeExecutionMetadata,
    RuntimeExecutionState,
    RuntimeExecutionSnapshot,
    ExecutionStage,
    RuntimeExecutionValidator,
    ExecutionValidationException,
    ExecutionMetadataException,
    ExecutionStateException
)
from types import MappingProxyType
from datetime import datetime, timezone

def test_valid_execution():
    descriptor = RuntimeExecutionDescriptor("exec-1", "runtime-1", "boot-1", "1.0.0", "1.0.0")
    metadata = RuntimeExecutionMetadata("Test Exec", "Desc", datetime.now(timezone.utc), datetime.now(timezone.utc), frozenset(["tag1"]), MappingProxyType({"k": "v"}), "1.0.0")
    state = RuntimeExecutionState(ExecutionStage.UNINITIALIZED)
    snapshot = RuntimeExecutionSnapshot("hash_exec", "hash_ident", "hash_desc", "hash_meta", "hash_state", "hash_comp")
    
    identity = RuntimeExecutionIdentity(descriptor, metadata, state, snapshot)
    execution = RuntimeExecution("exec-1", identity)
    
    RuntimeExecutionValidator.validate_execution(execution) # Should not raise

def test_invalid_execution_no_identifier():
    descriptor = RuntimeExecutionDescriptor("exec-1", "runtime-1", "boot-1", "1.0.0", "1.0.0")
    metadata = RuntimeExecutionMetadata("Test Exec", "Desc", datetime.now(timezone.utc), datetime.now(timezone.utc), frozenset(["tag1"]), MappingProxyType({"k": "v"}), "1.0.0")
    state = RuntimeExecutionState(ExecutionStage.UNINITIALIZED)
    snapshot = RuntimeExecutionSnapshot("hash_exec", "hash_ident", "hash_desc", "hash_meta", "hash_state", "hash_comp")
    
    identity = RuntimeExecutionIdentity(descriptor, metadata, state, snapshot)
    execution = RuntimeExecution("", identity)
    with pytest.raises(ExecutionValidationException):
        RuntimeExecutionValidator.validate_execution(execution)

def test_invalid_metadata():
    with pytest.raises(ExecutionMetadataException):
        RuntimeExecutionValidator.validate_metadata(None)
    
    metadata = RuntimeExecutionMetadata("", "Desc", datetime.now(timezone.utc), datetime.now(timezone.utc), frozenset(["tag1"]), MappingProxyType({"k": "v"}), "1.0.0")
    with pytest.raises(ExecutionMetadataException):
        RuntimeExecutionValidator.validate_metadata(metadata)

def test_invalid_state():
    with pytest.raises(ExecutionStateException):
        RuntimeExecutionValidator.validate_state(None)
    
    state = RuntimeExecutionState("INVALID")
    with pytest.raises(ExecutionStateException):
        RuntimeExecutionValidator.validate_state(state)
