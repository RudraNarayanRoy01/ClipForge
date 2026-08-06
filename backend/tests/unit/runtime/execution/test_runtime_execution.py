import pytest
from src.runtime.execution import (
    RuntimeExecution,
    RuntimeExecutionIdentity,
    RuntimeExecutionDescriptor,
    RuntimeExecutionMetadata,
    RuntimeExecutionState,
    RuntimeExecutionSnapshot,
    ExecutionStage
)
from types import MappingProxyType
from datetime import datetime, timezone

def test_runtime_execution_creation():
    descriptor = RuntimeExecutionDescriptor("exec-1", "runtime-1", "boot-1", "1.0.0", "1.0.0")
    metadata = RuntimeExecutionMetadata("Test Exec", "Desc", datetime.now(timezone.utc), datetime.now(timezone.utc), frozenset(["tag1"]), MappingProxyType({"k": "v"}), "1.0.0")
    state = RuntimeExecutionState(ExecutionStage.UNINITIALIZED)
    snapshot = RuntimeExecutionSnapshot("hash_exec", "hash_ident", "hash_desc", "hash_meta", "hash_state", "hash_comp")
    
    identity = RuntimeExecutionIdentity(descriptor, metadata, state, snapshot)
    execution = RuntimeExecution("exec-1", identity)
    
    assert execution.identifier == "exec-1"
    assert execution.identity == identity
    assert execution.identity.descriptor == descriptor
    assert execution.identity.metadata == metadata
    assert execution.identity.state == state
    assert execution.identity.snapshot == snapshot

def test_runtime_execution_immutability():
    descriptor = RuntimeExecutionDescriptor("exec-1", "runtime-1", "boot-1", "1.0.0", "1.0.0")
    metadata = RuntimeExecutionMetadata("Test Exec", "Desc", datetime.now(timezone.utc), datetime.now(timezone.utc), frozenset(["tag1"]), MappingProxyType({"k": "v"}), "1.0.0")
    state = RuntimeExecutionState(ExecutionStage.UNINITIALIZED)
    snapshot = RuntimeExecutionSnapshot("hash_exec", "hash_ident", "hash_desc", "hash_meta", "hash_state", "hash_comp")
    
    identity = RuntimeExecutionIdentity(descriptor, metadata, state, snapshot)
    execution = RuntimeExecution("exec-1", identity)
    
    with pytest.raises(Exception): # FrozenInstanceError or AttributeError
        execution.identifier = "new-id"
