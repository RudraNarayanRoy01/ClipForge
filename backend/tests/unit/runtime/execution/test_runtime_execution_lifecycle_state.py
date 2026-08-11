import pytest
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock

from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.core.scheduling_model import SchedulingStatus
from src.runtime.execution.runtime_execution_lifecycle_state import RuntimeExecutionLifecycleState
from src.runtime.execution.runtime_execution_transition_engine import RuntimeExecutionTransitionEngine


def test_initial_state_defaults_to_prepared():
    """Verify construction produces PREPARED by default."""
    state = RuntimeExecutionLifecycleState()
    assert state.current_status == RuntimeExecutionStatus.PREPARED


def test_state_identity_ignores_dependency_engine():
    """Verify that state equality is based on status, not engine identity."""
    engine1 = RuntimeExecutionTransitionEngine()
    engine2 = RuntimeExecutionTransitionEngine()
    
    state1 = RuntimeExecutionLifecycleState(
        current_status=RuntimeExecutionStatus.PREPARED,
        _engine=engine1
    )
    state2 = RuntimeExecutionLifecycleState(
        current_status=RuntimeExecutionStatus.PREPARED,
        _engine=engine2
    )
    
    assert state1 == state2
    assert state1 is not state2
    assert hash(state1) == hash(state2)


def test_state_is_immutable():
    """Verify the state is a frozen dataclass and returns a new object on transition."""
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    
    with pytest.raises(FrozenInstanceError):
        state.current_status = RuntimeExecutionStatus.READY
        
    new_state = state.transition_to(RuntimeExecutionStatus.READY)
    
    # Verify new object returned and previous unchanged
    assert state.current_status == RuntimeExecutionStatus.PREPARED
    assert new_state.current_status == RuntimeExecutionStatus.READY
    assert state is not new_state


def test_valid_path_prepared_to_completed():
    """Verify a full valid lifecycle path."""
    s1 = RuntimeExecutionLifecycleState()
    
    s2 = s1.transition_to(RuntimeExecutionStatus.READY)
    assert s2.current_status == RuntimeExecutionStatus.READY
    
    s3 = s2.transition_to(RuntimeExecutionStatus.EXECUTING)
    assert s3.current_status == RuntimeExecutionStatus.EXECUTING
    
    s4 = s3.transition_to(RuntimeExecutionStatus.COMPLETED)
    assert s4.current_status == RuntimeExecutionStatus.COMPLETED


def test_valid_path_prepared_to_failed():
    """Verify a full valid lifecycle path resulting in failure."""
    s1 = RuntimeExecutionLifecycleState()
    s2 = s1.transition_to(RuntimeExecutionStatus.READY)
    s3 = s2.transition_to(RuntimeExecutionStatus.EXECUTING)
    s4 = s3.transition_to(RuntimeExecutionStatus.FAILED)
    
    assert s4.current_status == RuntimeExecutionStatus.FAILED


def test_invalid_transitions_propagate_value_error():
    """Verify invalid transitions bubble up the ValueError from the Engine."""
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    
    # Skips
    with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
        state.transition_to(RuntimeExecutionStatus.EXECUTING)
        
    with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
        state.transition_to(RuntimeExecutionStatus.COMPLETED)
        
    # Self transitions
    with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
        state.transition_to(RuntimeExecutionStatus.PREPARED)


def test_terminal_state_regressions_rejected():
    """Verify regressions from terminal states are rejected."""
    completed = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.COMPLETED)
    with pytest.raises(ValueError):
        completed.transition_to(RuntimeExecutionStatus.READY)
        
    failed = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.FAILED)
    with pytest.raises(ValueError):
        failed.transition_to(RuntimeExecutionStatus.EXECUTING)
        
    aborted = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.ABORTED)
    with pytest.raises(ValueError):
        aborted.transition_to(RuntimeExecutionStatus.PREPARED)


def test_aborted_semantics_preserved():
    """Verify ABORTED behavior continues to delegate to the engine properly."""
    executing = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.EXECUTING)
    with pytest.raises(ValueError):
        # Incoming to aborted is invalid in the certified matrix
        executing.transition_to(RuntimeExecutionStatus.ABORTED)
        
    ready = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.READY)
    with pytest.raises(ValueError):
        ready.transition_to(RuntimeExecutionStatus.ABORTED)


def test_outcome_separation():
    """Verify RuntimeExecutionOutcome is completely rejected."""
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.EXECUTING)
    
    with pytest.raises(ValueError):
        state.transition_to(RuntimeExecutionOutcome.SUCCESS)
        
    with pytest.raises(ValueError):
        state.transition_to(RuntimeExecutionOutcome.FAILED)


def test_scheduling_separation():
    """Verify SchedulingStatus is completely rejected."""
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    
    with pytest.raises(ValueError):
        # It should reject SchedulingStatus.READY even though names collide
        state.transition_to(SchedulingStatus.READY)
        
    with pytest.raises(ValueError):
        state.transition_to(SchedulingStatus.QUEUED)


def test_delegates_to_engine():
    """Verify the state component accurately delegates to the engine instance without duplication."""
    mock_engine = MagicMock(spec=RuntimeExecutionTransitionEngine)
    mock_engine.transition.return_value = RuntimeExecutionStatus.READY
    
    state = RuntimeExecutionLifecycleState(
        current_status=RuntimeExecutionStatus.PREPARED,
        _engine=mock_engine
    )
    
    new_state = state.transition_to(RuntimeExecutionStatus.READY)
    
    mock_engine.transition.assert_called_once_with(
        RuntimeExecutionStatus.PREPARED,
        RuntimeExecutionStatus.READY
    )
    
    assert new_state.current_status == RuntimeExecutionStatus.READY


def test_engine_continuity_across_transitions():
    """Verify that engine dependency is preserved across state replacements."""
    engine = RuntimeExecutionTransitionEngine()
    s1 = RuntimeExecutionLifecycleState(_engine=engine)
    s2 = s1.transition_to(RuntimeExecutionStatus.READY)
    
    assert s1._engine is engine
    assert s2._engine is engine


def test_state_inequality():
    """Verify PREPARED != READY even when the same engine instance is used."""
    engine = RuntimeExecutionTransitionEngine()
    s1 = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED, _engine=engine)
    s2 = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.READY, _engine=engine)
    
    assert s1 != s2


def test_state_repr_purity():
    """Verify the engine dependency does not appear in repr(state)."""
    engine = RuntimeExecutionTransitionEngine()
    state = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED, _engine=engine)
    
    rep = repr(state)
    assert "current_status=" in rep
    assert "_engine=" not in rep
    assert "RuntimeExecutionTransitionEngine" not in rep


def test_original_state_preservation():
    """Verify original states are not mutated after multiple transitions."""
    s1 = RuntimeExecutionLifecycleState(RuntimeExecutionStatus.PREPARED)
    s2 = s1.transition_to(RuntimeExecutionStatus.READY)
    s3 = s2.transition_to(RuntimeExecutionStatus.EXECUTING)
    
    assert s1.current_status == RuntimeExecutionStatus.PREPARED
    assert s2.current_status == RuntimeExecutionStatus.READY
    assert s3.current_status == RuntimeExecutionStatus.EXECUTING
