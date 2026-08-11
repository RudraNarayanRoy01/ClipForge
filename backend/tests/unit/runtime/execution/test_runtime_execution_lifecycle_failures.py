"""Tests for the Runtime Execution Lifecycle Failure Semantics contract."""
from datetime import datetime
from unittest.mock import MagicMock
import pytest

from src.runtime.core.scheduling_model import SchedulingStatus, SchedulingDecision
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_coordinator import RuntimeExecutionCoordinator
from src.runtime.core.executor import RuntimeExecutor
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.core.execution_model import ExecutionIdentity
from src.runtime.execution.runtime_execution_descriptor import RuntimeExecutionDescriptor
from src.runtime.execution.runtime_execution_metadata import RuntimeExecutionMetadata
from src.runtime.execution.runtime_execution_snapshot import RuntimeExecutionSnapshot
from src.runtime.execution.runtime_execution_lifecycle_state import RuntimeExecutionLifecycleState
from src.runtime.execution.runtime_execution_transition_engine import RuntimeExecutionTransitionEngine
from src.runtime.execution.runtime_execution_terminal_consistency_validator import RuntimeExecutionTerminalConsistencyValidator
from types import MappingProxyType

def create_mock_execution_identity() -> RuntimeExecutionIdentity:
    descriptor = RuntimeExecutionDescriptor(
        execution_id="exec_1",
        runtime_id="rt_1",
        bootstrap_id="bs_1",
        version="1.0",
        schema_version="1.0"
    )
    metadata = RuntimeExecutionMetadata(
        name="test",
        description="desc",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        tags=frozenset(),
        annotations=MappingProxyType({}),
        metadata_version="1.0"
    )
    snapshot = RuntimeExecutionSnapshot("h1", "h2", "h3", "h4", "h5", "h6")
    return RuntimeExecutionIdentity(
        descriptor=descriptor,
        metadata=metadata,
        status=RuntimeExecutionStatus.READY,
        snapshot=snapshot
    )

def create_mock_scheduling_decision(status: SchedulingStatus) -> SchedulingDecision:
    decision = MagicMock(spec=SchedulingDecision)
    decision.status = status
    decision.execution_identity = MagicMock(spec=ExecutionIdentity)
    return decision


# A. Scheduling failure separation
def test_scheduling_rejection_separation():
    """Prove that REJECTED scheduling decisions short-circuit execution and don't produce results."""
    executor = MagicMock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor)
    identity = create_mock_execution_identity()
    decision = create_mock_scheduling_decision(SchedulingStatus.REJECTED)
    
    result = coordinator.coordinate(decision, identity)
    
    assert result is None
    executor.execute.assert_not_called()


# B. Lifecycle contract violation
def test_lifecycle_contract_violation_raises_value_error():
    """Prove that illegal lifecycle transitions strictly raise ValueError."""
    engine = RuntimeExecutionTransitionEngine()
    
    invalid_transitions = [
        (RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.READY),
        (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.ABORTED, RuntimeExecutionStatus.READY),
    ]
    
    for start, target in invalid_transitions:
        with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
            engine.transition(start, target)


# C. Execution failure separation
def test_execution_failure_separation():
    """Prove that Executor catches exceptions and natively returns a FAILED result."""
    executor = RuntimeExecutor()
    
    # NOTE: Patching `_execute_attempt` is an intentional test seam used to 
    # induce a genuine execution-attempt failure while preserving the actual 
    # production RuntimeExecutor failure-handling path.
    original_execute_attempt = executor._execute_attempt
    executor._execute_attempt = MagicMock(side_effect=RuntimeError("simulated domain error"))
    
    try:
        identity = create_mock_execution_identity()
        decision = create_mock_scheduling_decision(SchedulingStatus.READY)
        
        result = executor.execute(decision, identity)
        
        assert isinstance(result, RuntimeExecutionResult)
        assert result.outcome == RuntimeExecutionOutcome.FAILED
        assert "simulated domain error" in result.failure_reason
    finally:
        executor._execute_attempt = original_execute_attempt


# D. Terminal-state protection
def test_terminal_state_protection():
    """Prove that terminal states cannot regress or progress to active states."""
    engine = RuntimeExecutionTransitionEngine()
    
    terminal_regressions = [
        (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.READY),
        (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.READY),
        (RuntimeExecutionStatus.ABORTED, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.ABORTED, RuntimeExecutionStatus.READY),
    ]
    
    for start, target in terminal_regressions:
        with pytest.raises(ValueError):
            engine.transition(start, target)


# E. Duplicate terminalization
def test_duplicate_terminalization():
    """Prove that terminal states cannot transition to themselves."""
    engine = RuntimeExecutionTransitionEngine()
    
    duplicate_transitions = [
        (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.COMPLETED),
        (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.FAILED),
        (RuntimeExecutionStatus.ABORTED, RuntimeExecutionStatus.ABORTED),
    ]
    
    for start, target in duplicate_transitions:
        with pytest.raises(ValueError):
            engine.transition(start, target)


# F. Result creation boundary
def test_result_creation_boundary():
    """Prove that a lifecycle contract violation does NOT synthesize a result."""
    engine = RuntimeExecutionTransitionEngine()
    
    result = None
    with pytest.raises(ValueError) as excinfo:
        result = engine.transition(RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.EXECUTING)
        
    # Prove that the transition operation stopped and no result was ever assigned
    assert result is None
    # Prove the exception itself is just a standard exception, not a masquerading result
    assert not isinstance(excinfo.value, RuntimeExecutionResult)


# G. Terminal consistency separation
def test_terminal_consistency_separation():
    """Prove that TerminalConsistencyValidator continues to observe state/result consistency."""
    validator = RuntimeExecutionTerminalConsistencyValidator()
    
    identity = create_mock_execution_identity()
    failed_result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.FAILED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0,
        failure_reason="test",
        metadata=MappingProxyType({})
    )
    
    # State vs Result consistency check
    valid_state = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.FAILED)
    invalid_state = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.COMPLETED)
    
    assert validator.is_consistent(valid_state, failed_result) is True
    assert validator.is_consistent(invalid_state, failed_result) is False


# H. ABORTED/CANCELLED separation
def test_aborted_cancelled_separation():
    """Prove that ABORTED and CANCELLED remain distinct concepts."""
    aborted_status = RuntimeExecutionStatus.ABORTED
    cancelled_outcome = RuntimeExecutionOutcome.CANCELLED
    
    assert aborted_status != cancelled_outcome
    assert type(aborted_status) is not type(cancelled_outcome)


# I. Non-mutation
def test_non_mutation_on_violation():
    """Prove that invalid transitions leave the state unmodified."""
    initial_state = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.READY)
    state_id_before = id(initial_state)
    
    with pytest.raises(ValueError):
        # READY -> COMPLETED is invalid
        initial_state.transition_to(RuntimeExecutionStatus.COMPLETED)
        
    # The original state object is intact
    assert id(initial_state) == state_id_before
    # The original state remains READY
    assert initial_state.current_status == RuntimeExecutionStatus.READY


# J. Determinism
def test_determinism_of_failures():
    """Prove that identical illegal transitions produce identical semantic failures."""
    engine = RuntimeExecutionTransitionEngine()
    
    for _ in range(5):
        with pytest.raises(ValueError) as excinfo:
            engine.transition(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.EXECUTING)
            
        assert "Invalid Runtime Execution transition" in str(excinfo.value)
