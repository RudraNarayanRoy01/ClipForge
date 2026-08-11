"""Tests for the Runtime Execution Lifecycle contract."""
from datetime import datetime
from unittest.mock import MagicMock
import pytest

from src.runtime.core.scheduling_model import SchedulingStatus, SchedulingDecision
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_session import RuntimeExecutionSession
from src.runtime.execution.runtime_execution_state import RuntimeExecutionState
from src.runtime.execution.runtime_execution_coordinator import RuntimeExecutionCoordinator
from src.runtime.core.executor import RuntimeExecutor
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.execution.runtime_execution_session_identity import RuntimeExecutionSessionIdentity
from src.runtime.execution.runtime_execution_state_identity import RuntimeExecutionStateIdentity
from src.runtime.core.execution_model import ExecutionIdentity
from src.runtime.execution.runtime_execution_descriptor import RuntimeExecutionDescriptor
from src.runtime.execution.runtime_execution_metadata import RuntimeExecutionMetadata
from src.runtime.execution.runtime_execution_snapshot import RuntimeExecutionSnapshot
import dataclasses

from types import MappingProxyType

def create_mock_execution_identity() -> RuntimeExecutionIdentity:
    """Helper to construct a valid RuntimeExecutionIdentity for testing contracts."""
    descriptor = RuntimeExecutionDescriptor(
        execution_id="exec_1",
        runtime_id="rt_1",
        bootstrap_id="bs_1",
        version="1.0",
        schema_version="1.0"
    )
    metadata = RuntimeExecutionMetadata(
        name="test_name",
        description="test_desc",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        tags=frozenset(),
        annotations=MappingProxyType({}),
        metadata_version="1.0"
    )
    snapshot = RuntimeExecutionSnapshot(
        execution_hash="h1",
        identity_hash="h2",
        descriptor_hash="h3",
        metadata_hash="h4",
        state_hash="h5",
        composition_hash="h6"
    )
    return RuntimeExecutionIdentity(
        descriptor=descriptor,
        metadata=metadata,
        status=RuntimeExecutionStatus.READY,
        snapshot=snapshot
    )

def create_mock_scheduling_decision(status: SchedulingStatus) -> SchedulingDecision:
    """Helper to construct a valid SchedulingDecision for testing contracts."""
    decision = MagicMock(spec=SchedulingDecision)
    decision.status = status
    decision.execution_identity = MagicMock(spec=ExecutionIdentity)
    return decision

def test_scheduling_vs_execution_status_separation():
    """
    Contract 1: SchedulingStatus and RuntimeExecutionStatus are distinct.
    They do not share elements.
    """
    # READY is conceptually shared but they belong to different enums.
    # The enums themselves are completely separate classes.
    assert issubclass(SchedulingStatus, str)
    assert issubclass(RuntimeExecutionStatus, str)
    assert SchedulingStatus is not RuntimeExecutionStatus

def test_execution_status_vs_outcome_separation():
    """
    Contract 2: RuntimeExecutionStatus and RuntimeExecutionOutcome are distinct concepts.
    One represents lifecycle state, the other represents terminal factual outcome.
    """
    exec_statuses = set(s.value for s in RuntimeExecutionStatus)
    outcomes = set(o.value for o in RuntimeExecutionOutcome)
    
    assert "FAILED" in exec_statuses
    assert "FAILED" in outcomes
    # They share FAILED conceptually but they are distinct types.
    assert issubclass(RuntimeExecutionStatus, str)
    assert issubclass(RuntimeExecutionOutcome, str)
    assert RuntimeExecutionStatus is not RuntimeExecutionOutcome

def test_runtime_execution_outcome_is_canonical():
    """
    Contract 3 & 4: RuntimeExecutionOutcome contains exactly SUCCESS, FAILED, CANCELLED.
    REJECTED and ABORTED do not exist in RuntimeExecutionOutcome.
    """
    outcomes = set(o.value for o in RuntimeExecutionOutcome)
    assert outcomes == {"SUCCESS", "FAILED", "CANCELLED"}
    assert "REJECTED" not in outcomes
    assert "ABORTED" not in outcomes

def test_session_and_state_are_passive():
    """
    Contract 5 & 6: Session and State remain passive. 
    They are structurally frozen and have no behavior.
    """
    session_id = MagicMock(spec=RuntimeExecutionSessionIdentity)
    session = RuntimeExecutionSession(identifier="sess_1", identity=session_id)
    
    state_id = MagicMock(spec=RuntimeExecutionStateIdentity)
    state = RuntimeExecutionState(identifier="state_1", identity=state_id)
    
    # Assert they are data structures only, lacking execute/coordinate methods
    assert not hasattr(session, "execute")
    assert not hasattr(session, "coordinate")
    assert not hasattr(session, "transition")
    
    assert not hasattr(state, "execute")
    assert not hasattr(state, "coordinate")
    assert not hasattr(state, "transition")
    
    # Assert immutability (frozen dataclasses)
    with pytest.raises(dataclasses.FrozenInstanceError):
        session.identifier = "new_sess"
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.identifier = "new_state"

def test_coordinator_handoff_for_ready():
    """
    Contract 7, 10: Coordinator is only the handoff boundary.
    For READY status, exact propagation occurs.
    """
    executor = MagicMock(spec=RuntimeExecutor)
    identity = create_mock_execution_identity()
    ready_decision = create_mock_scheduling_decision(SchedulingStatus.READY)
    
    expected_result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0
    )
    executor.execute.return_value = expected_result
    
    coordinator = RuntimeExecutionCoordinator(executor)
    result = coordinator.coordinate(ready_decision, identity)
    
    assert result is expected_result
    executor.execute.assert_called_once_with(
        scheduling_decision=ready_decision,
        identity=identity
    )
    
    # Assert exact identity propagation
    kwargs = executor.execute.call_args[1]
    assert kwargs["scheduling_decision"] is ready_decision
    assert kwargs["identity"] is identity

def test_coordinator_prevents_non_ready_execution():
    """
    Contract 11: Non-READY decisions do not reach the executor.
    """
    executor = MagicMock(spec=RuntimeExecutor)
    coordinator = RuntimeExecutionCoordinator(executor)
    identity = create_mock_execution_identity()
    
    non_ready_statuses = [
        SchedulingStatus.REJECTED,
        SchedulingStatus.QUEUED,
        SchedulingStatus.DEFERRED,
        SchedulingStatus.BLOCKED
    ]
    
    for status in non_ready_statuses:
        decision = create_mock_scheduling_decision(status)
        empty_result = coordinator.coordinate(decision, identity)
        assert empty_result is None
        executor.execute.assert_not_called()

def test_executor_is_execution_owner():
    """
    Contract 8: Executor remains execution owner. 
    It translates the attempt into a RuntimeExecutionResult.
    """
    executor = RuntimeExecutor()
    identity = create_mock_execution_identity()
    decision = create_mock_scheduling_decision(SchedulingStatus.READY)
    
    result = executor.execute(decision, identity)
    assert isinstance(result, RuntimeExecutionResult)
    assert result.outcome == RuntimeExecutionOutcome.SUCCESS

def test_runtime_execution_result_is_immutable():
    """
    Contract 9: RuntimeExecutionResult remains immutable.
    """
    identity = create_mock_execution_identity()
    result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0
    )
    
    # Assert frozen dataclass behavior
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.outcome = RuntimeExecutionOutcome.FAILED

def test_aborted_vs_cancelled_distinction():
    """
    Contract 13: ABORTED is explicitly distinguished from CANCELLED.
    They belong to different enum boundaries and are not equivalent.
    """
    # They should not share the same string representation or enum membership.
    assert "ABORTED" not in [o.value for o in RuntimeExecutionOutcome]
    assert "CANCELLED" not in [s.value for s in RuntimeExecutionStatus]
    
    aborted_status = RuntimeExecutionStatus.ABORTED
    cancelled_outcome = RuntimeExecutionOutcome.CANCELLED
    
    # Ensure they are distinct types and values
    assert aborted_status != cancelled_outcome
    assert not isinstance(aborted_status, type(cancelled_outcome))

def test_completed_vs_success_distinction():
    """
    Contract 14: COMPLETED is explicitly distinguished from SUCCESS.
    They belong to different enum boundaries and are not equivalent.
    """
    assert "COMPLETED" not in [o.value for o in RuntimeExecutionOutcome]
    assert "SUCCESS" not in [s.value for s in RuntimeExecutionStatus]
    
    completed_status = RuntimeExecutionStatus.COMPLETED
    success_outcome = RuntimeExecutionOutcome.SUCCESS
    
    assert completed_status != success_outcome
    assert not isinstance(completed_status, type(success_outcome))

def test_conceptual_transition_contract():
    """
    Contract 15: The conceptual lifecycle terminology is correct.
    This tests the documented vocabulary without implementing a state machine.
    """
    statuses = set(s.value for s in RuntimeExecutionStatus)
    
    # Pre-execution structural preparation
    assert "PREPARED" in statuses
    # Pre-execution readiness
    assert "READY" in statuses
    # Execution active
    assert "EXECUTING" in statuses
    
    # Terminal statuses
    terminal_statuses = {"COMPLETED", "FAILED", "ABORTED"}
    for ts in terminal_statuses:
        assert ts in statuses

