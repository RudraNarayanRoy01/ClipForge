from datetime import datetime
import pytest

from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_lifecycle_state import RuntimeExecutionLifecycleState
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.execution.runtime_execution_terminal_consistency_validator import RuntimeExecutionTerminalConsistencyValidator


from unittest.mock import MagicMock

@pytest.fixture
def identity():
    # Note: The validator strictly performs a semantic combination check.
    # It does not guarantee or verify identity continuity between state and result.
    return MagicMock(spec=RuntimeExecutionIdentity)


@pytest.fixture
def validator():
    return RuntimeExecutionTerminalConsistencyValidator()


def _create_result(identity, outcome):
    return RuntimeExecutionResult(
        identity=identity,
        outcome=outcome,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0,
        failure_reason="Test reason" if outcome == RuntimeExecutionOutcome.FAILED else None
    )


def test_valid_combinations(validator, identity):
    # COMPLETED + SUCCESS
    state_success = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.COMPLETED)
    result_success = _create_result(identity, RuntimeExecutionOutcome.SUCCESS)
    assert validator.is_consistent(state_success, result_success) is True

    # FAILED + FAILED
    state_failed = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.FAILED)
    result_failed = _create_result(identity, RuntimeExecutionOutcome.FAILED)
    assert validator.is_consistent(state_failed, result_failed) is True


def test_contradictory_combinations(validator, identity):
    # COMPLETED + FAILED
    state_completed = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.COMPLETED)
    result_failed = _create_result(identity, RuntimeExecutionOutcome.FAILED)
    assert validator.is_consistent(state_completed, result_failed) is False

    # FAILED + SUCCESS
    state_failed = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.FAILED)
    result_success = _create_result(identity, RuntimeExecutionOutcome.SUCCESS)
    assert validator.is_consistent(state_failed, result_success) is False


def test_active_state_protection(validator, identity):
    # PREPARED, READY, EXECUTING with any result should be False
    active_states = [
        RuntimeExecutionStatus.PREPARED,
        RuntimeExecutionStatus.READY,
        RuntimeExecutionStatus.EXECUTING
    ]
    outcomes = [
        RuntimeExecutionOutcome.SUCCESS,
        RuntimeExecutionOutcome.FAILED,
        RuntimeExecutionOutcome.CANCELLED
    ]

    for status in active_states:
        state = RuntimeExecutionLifecycleState(current_status=status)
        for outcome in outcomes:
            result = _create_result(identity, outcome)
            assert validator.is_consistent(state, result) is False


def test_aborted_semantics(validator, identity):
    # ABORTED + any outcome should be False
    state_aborted = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.ABORTED)
    outcomes = [
        RuntimeExecutionOutcome.SUCCESS,
        RuntimeExecutionOutcome.FAILED,
        RuntimeExecutionOutcome.CANCELLED
    ]

    for outcome in outcomes:
        result = _create_result(identity, outcome)
        assert validator.is_consistent(state_aborted, result) is False


def test_cancelled_semantics(validator, identity):
    # Any state + CANCELLED outcome should be False
    states = [
        RuntimeExecutionStatus.PREPARED,
        RuntimeExecutionStatus.READY,
        RuntimeExecutionStatus.EXECUTING,
        RuntimeExecutionStatus.COMPLETED,
        RuntimeExecutionStatus.FAILED,
        RuntimeExecutionStatus.ABORTED
    ]
    result_cancelled = _create_result(identity, RuntimeExecutionOutcome.CANCELLED)

    for status in states:
        state = RuntimeExecutionLifecycleState(current_status=status)
        assert validator.is_consistent(state, result_cancelled) is False


def test_invalid_input_types(validator, identity):
    state = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.COMPLETED)
    result = _create_result(identity, RuntimeExecutionOutcome.SUCCESS)

    # Missing state
    assert validator.is_consistent(None, result) is False
    # Missing result
    assert validator.is_consistent(state, None) is False
    # Enums instead of objects
    assert validator.is_consistent(RuntimeExecutionStatus.COMPLETED, result) is False
    assert validator.is_consistent(state, RuntimeExecutionOutcome.SUCCESS) is False
    # Random types
    assert validator.is_consistent("state", "result") is False


def test_immutability_and_identity_preservation(validator, identity):
    state = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.COMPLETED)
    result = _create_result(identity, RuntimeExecutionOutcome.SUCCESS)
    
    # Keep original ids
    state_id = id(state)
    result_id = id(result)

    # Perform validation
    assert validator.is_consistent(state, result) is True
    
    # Assert identities remain exactly the same
    assert id(state) == state_id
    assert id(result) == result_id
    
    # Assert values didn't mutate
    assert state.current_status == RuntimeExecutionStatus.COMPLETED
    assert result.outcome == RuntimeExecutionOutcome.SUCCESS


def test_statelessness(validator, identity):
    state_completed = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.COMPLETED)
    result_success = _create_result(identity, RuntimeExecutionOutcome.SUCCESS)
    
    state_failed = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.FAILED)
    result_failed = _create_result(identity, RuntimeExecutionOutcome.FAILED)

    # Repeated calls should produce the same deterministic results
    assert validator.is_consistent(state_completed, result_success) is True
    assert validator.is_consistent(state_failed, result_failed) is True
    assert validator.is_consistent(state_completed, result_success) is True
    assert validator.is_consistent(state_completed, result_failed) is False
    assert validator.is_consistent(state_failed, result_success) is False
