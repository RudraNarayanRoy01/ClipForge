import pytest
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.core.scheduling_model import SchedulingStatus
from src.runtime.execution.runtime_execution_transition_validator import RuntimeExecutionTransitionValidator

@pytest.fixture
def validator():
    return RuntimeExecutionTransitionValidator()

def test_valid_transitions(validator):
    """Test explicitly certified valid transitions."""
    assert validator.is_valid(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY) is True
    assert validator.is_valid(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.EXECUTING) is True
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.COMPLETED) is True
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.FAILED) is True

def test_invalid_skipped_transitions(validator):
    """Test that skipping lifecycle stages is invalid."""
    assert validator.is_valid(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.EXECUTING) is False
    assert validator.is_valid(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.COMPLETED) is False
    assert validator.is_valid(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.FAILED) is False
    assert validator.is_valid(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.COMPLETED) is False
    assert validator.is_valid(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.FAILED) is False

def test_invalid_regressions(validator):
    """Test that backward transitions in active execution are invalid."""
    assert validator.is_valid(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.PREPARED) is False
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.READY) is False
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.PREPARED) is False

def test_terminal_state_regressions(validator):
    """Test that terminal states cannot transition to active states."""
    terminal_states = [
        RuntimeExecutionStatus.COMPLETED,
        RuntimeExecutionStatus.FAILED,
        RuntimeExecutionStatus.ABORTED,
    ]
    active_states = [
        RuntimeExecutionStatus.PREPARED,
        RuntimeExecutionStatus.READY,
        RuntimeExecutionStatus.EXECUTING,
    ]
    
    for term in terminal_states:
        for active in active_states:
            assert validator.is_valid(term, active) is False

def test_terminal_state_cross_transitions(validator):
    """Test that terminal states cannot transition to other terminal states."""
    assert validator.is_valid(RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.FAILED) is False
    assert validator.is_valid(RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.COMPLETED) is False

def test_self_transitions(validator):
    """Test that idempotent state assignment is structurally invalid."""
    for status in RuntimeExecutionStatus:
        assert validator.is_valid(status, status) is False

def test_aborted_transitions(validator):
    """Test that ABORTED permits no incoming or outgoing transitions."""
    for status in RuntimeExecutionStatus:
        if status != RuntimeExecutionStatus.ABORTED:
            # Outgoing from ABORTED
            assert validator.is_valid(RuntimeExecutionStatus.ABORTED, status) is False
            # Incoming to ABORTED
            assert validator.is_valid(status, RuntimeExecutionStatus.ABORTED) is False

def test_outcome_separation(validator):
    """Test that RuntimeExecutionOutcome is strictly rejected as lifecycle status."""
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionOutcome.SUCCESS) is False
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionOutcome.FAILED) is False
    assert validator.is_valid(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionOutcome.CANCELLED) is False

def test_scheduling_separation(validator):
    """Test that SchedulingStatus is strictly rejected as lifecycle status."""
    assert validator.is_valid(RuntimeExecutionStatus.PREPARED, SchedulingStatus.READY) is False
    assert validator.is_valid(SchedulingStatus.READY, RuntimeExecutionStatus.EXECUTING) is False
    assert validator.is_valid(SchedulingStatus.QUEUED, RuntimeExecutionStatus.EXECUTING) is False

def test_none_handling(validator):
    """Test that None (initialization semantics) is not supported as a transition."""
    assert validator.is_valid(None, RuntimeExecutionStatus.PREPARED) is False
    assert validator.is_valid(RuntimeExecutionStatus.PREPARED, None) is False
    assert validator.is_valid(None, None) is False

def test_invalid_types(validator):
    """Test that other random types are rejected gracefully without exceptions."""
    assert validator.is_valid("PREPARED", "READY") is False
    assert validator.is_valid(1, 2) is False
    assert validator.is_valid(object(), object()) is False
