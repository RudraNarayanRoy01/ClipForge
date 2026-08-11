import pytest
import time
from datetime import datetime
from types import MappingProxyType
from unittest.mock import patch

from src.runtime.core.executor import RuntimeExecutor
from src.runtime.execution.runtime_execution_coordinator import RuntimeExecutionCoordinator
from src.runtime.execution.runtime_execution_lifecycle_state import RuntimeExecutionLifecycleState
from src.runtime.execution.runtime_execution_terminal_consistency_validator import RuntimeExecutionTerminalConsistencyValidator
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.execution.runtime_execution_descriptor import RuntimeExecutionDescriptor
from src.runtime.execution.runtime_execution_metadata import RuntimeExecutionMetadata
from src.runtime.execution.runtime_execution_snapshot import RuntimeExecutionSnapshot
from src.runtime.core.scheduling_model import (
    SchedulingDecision, SchedulingIdentity, SchedulingPriority,
    SchedulingPolicy, SchedulingStrategy, QueueClassification, SchedulingStatus
)
from src.runtime.core.execution_model import ExecutionIdentity

@pytest.fixture
def valid_identity() -> RuntimeExecutionIdentity:
    """Fixture providing a realistic execution identity domain model."""
    return RuntimeExecutionIdentity(
        descriptor=RuntimeExecutionDescriptor(
            execution_id="exec-123",
            runtime_id="rt-123",
            bootstrap_id="boot-123",
            version="1.0",
            schema_version="1.0"
        ),
        metadata=RuntimeExecutionMetadata(
            name="test-integration-execution",
            description="Integration test execution metadata",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=frozenset(["integration", "test"]),
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

@pytest.fixture
def ready_decision() -> SchedulingDecision:
    """Fixture providing a realistic ready scheduling decision."""
    return SchedulingDecision(
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
        status=SchedulingStatus.READY,
        priority=SchedulingPriority.NORMAL,
        policy=SchedulingPolicy.IMMEDIATE,
        strategy=SchedulingStrategy.FIFO,
        queue_classification=QueueClassification.BACKGROUND,
        scheduling_timestamp=time.time(),
        scheduling_reasoning="Lifecycle integration scenario"
    )

def test_successful_execution_lifecycle_composition(valid_identity, ready_decision):
    """
    SCENARIO 1 — SUCCESSFUL LIFECYCLE COMPOSITION
    Proves the complete successful cross-boundary lifecycle without an orchestrator.
    """
    # 1. State creation (starts as PREPARED)
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    
    # 2. Transition PREPARED -> READY
    state = state.transition_to(RuntimeExecutionStatus.READY)
    
    # 3. Transition READY -> EXECUTING
    state = state.transition_to(RuntimeExecutionStatus.EXECUTING)
    
    # 4. Handoff to Coordinator -> Executor
    executor = RuntimeExecutor()
    coordinator = RuntimeExecutionCoordinator(executor=executor)
    
    # Real execution attempt
    result = coordinator.coordinate(ready_decision, valid_identity)
    
    # 5. Verify SUCCESS Result
    assert isinstance(result, RuntimeExecutionResult)
    assert result.outcome == RuntimeExecutionOutcome.SUCCESS
    
    # 6. Transition EXECUTING -> COMPLETED
    state = state.transition_to(RuntimeExecutionStatus.COMPLETED)
    
    # 7. Terminal Consistency Validation
    validator = RuntimeExecutionTerminalConsistencyValidator()
    assert validator.is_consistent(state, result) is True


def test_failed_execution_lifecycle_composition(valid_identity, ready_decision):
    """
    SCENARIO 2 — FAILED EXECUTION COMPOSITION
    Proves the actual production execution-failure path using the real RuntimeExecutor.
    """
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    state = state.transition_to(RuntimeExecutionStatus.READY)
    state = state.transition_to(RuntimeExecutionStatus.EXECUTING)
    
    executor = RuntimeExecutor()
    coordinator = RuntimeExecutionCoordinator(executor=executor)
    
    # Induce an execution failure to trigger the real executor catch block
    with patch.object(executor, '_execute_attempt', side_effect=RuntimeError("Simulated execution failure")):
        result = coordinator.coordinate(ready_decision, valid_identity)
        
    # Verify the executor caught the exception and produced a FAILED outcome
    assert isinstance(result, RuntimeExecutionResult)
    assert result.outcome == RuntimeExecutionOutcome.FAILED
    
    # Transition EXECUTING -> FAILED
    state = state.transition_to(RuntimeExecutionStatus.FAILED)
    
    # Terminal Consistency Validation
    validator = RuntimeExecutionTerminalConsistencyValidator()
    assert validator.is_consistent(state, result) is True


def test_scheduling_rejection_is_distinct_from_lifecycle_violation(valid_identity, ready_decision):
    """
    SCENARIO 3 — SCHEDULING / LIFECYCLE FAILURE SEPARATION
    Proves two distinct failure boundaries that do not produce execution failures.
    """
    # 3A - Scheduling Rejection
    rejected_decision = SchedulingDecision(
        identity=ready_decision.identity,
        execution_identity=ready_decision.execution_identity,
        status=SchedulingStatus.REJECTED,
        priority=ready_decision.priority,
        policy=ready_decision.policy,
        strategy=ready_decision.strategy,
        queue_classification=ready_decision.queue_classification,
        scheduling_timestamp=ready_decision.scheduling_timestamp,
        scheduling_reasoning="Rejected for test"
    )
    
    executor = RuntimeExecutor()
    coordinator = RuntimeExecutionCoordinator(executor=executor)
    
    with patch.object(executor, 'execute') as mock_execute:
        result = coordinator.coordinate(rejected_decision, valid_identity)
        
    assert result is None
    mock_execute.assert_not_called()
    
    # 3B - Lifecycle Contract Violation
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    original_state = state
    original_status = state.current_status
    
    # Attempting to skip READY
    with pytest.raises(ValueError):
        state.transition_to(RuntimeExecutionStatus.EXECUTING)
        
    assert state is original_state
    assert state.current_status == original_status


def test_terminal_protection_and_state_immutability_compose():
    """
    SCENARIO 4 — TERMINAL PROTECTION + IMMUTABLE STATE COMPOSITION
    Proves state composition maintains immutability and terminal protection via TransitionEngine.
    """
    prepared_state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    ready_state = prepared_state.transition_to(RuntimeExecutionStatus.READY)
    executing_state = ready_state.transition_to(RuntimeExecutionStatus.EXECUTING)
    completed_state = executing_state.transition_to(RuntimeExecutionStatus.COMPLETED)
    
    # 1. State objects remain unchanged
    assert prepared_state is not ready_state
    assert ready_state is not executing_state
    assert executing_state is not completed_state
    
    assert prepared_state.current_status == RuntimeExecutionStatus.PREPARED
    assert ready_state.current_status == RuntimeExecutionStatus.READY
    assert executing_state.current_status == RuntimeExecutionStatus.EXECUTING
    assert completed_state.current_status == RuntimeExecutionStatus.COMPLETED
    
    # 2. Terminal lifecycle state cannot be re-entered or regressed (COMPLETED)
    with pytest.raises(ValueError):
        completed_state.transition_to(RuntimeExecutionStatus.COMPLETED)
    with pytest.raises(ValueError):
        completed_state.transition_to(RuntimeExecutionStatus.EXECUTING)

    # 3. Terminal lifecycle state cannot be re-entered or regressed (FAILED)
    failed_state = executing_state.transition_to(RuntimeExecutionStatus.FAILED)
    with pytest.raises(ValueError):
        failed_state.transition_to(RuntimeExecutionStatus.FAILED)
    with pytest.raises(ValueError):
        failed_state.transition_to(RuntimeExecutionStatus.READY)


def test_status_outcome_separation_and_identity_propagation(valid_identity, ready_decision):
    """
    SCENARIO 5 — SEMANTIC SEPARATION + IDENTITY PROPAGATION
    Proves semantics and identity dimensions are distinct.
    """
    # Part A - Status vs Outcome type separation
    assert isinstance(RuntimeExecutionStatus.ABORTED, RuntimeExecutionStatus)
    assert isinstance(RuntimeExecutionOutcome.CANCELLED, RuntimeExecutionOutcome)
    
    # Part B - No ABORTED/CANCELLED implicit mapping
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.ABORTED)
    result = RuntimeExecutionResult(
        identity=valid_identity,
        outcome=RuntimeExecutionOutcome.CANCELLED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=0.0,
        failure_reason=None,
        metadata=MappingProxyType({})
    )
    
    validator = RuntimeExecutionTerminalConsistencyValidator()
    assert validator.is_consistent(state, result) is False
    
    # Part C - Identity Propagation
    executor = RuntimeExecutor()
    coordinator = RuntimeExecutionCoordinator(executor=executor)
    
    returned_result = coordinator.coordinate(ready_decision, valid_identity)
    
    # Asserts that the identity passed into the coordinator execution path 
    # is the EXACT identity carried by the resulting execution result.
    assert returned_result.identity is valid_identity
