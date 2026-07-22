import pytest
from datetime import datetime, timezone
import time
from src.application.render_execution_lifecycle import (
    RenderExecutionId,
    RenderExecutionState,
    RenderExecutionLifecycle,
    InvalidStateTransitionError
)

def test_initial_state():
    lifecycle = RenderExecutionLifecycle()
    metadata = lifecycle.metadata
    
    assert isinstance(metadata.id, RenderExecutionId)
    assert metadata.state == RenderExecutionState.QUEUED
    assert isinstance(metadata.creation_time, datetime)
    assert metadata.start_time is None
    assert metadata.completion_time is None
    assert metadata.elapsed_duration_seconds is None
    assert not lifecycle.is_terminal

def test_valid_successful_transition_path():
    lifecycle = RenderExecutionLifecycle()
    
    # QUEUED -> STARTING
    metadata_starting = lifecycle.transition_to_starting()
    assert metadata_starting.state == RenderExecutionState.STARTING
    assert metadata_starting.id == lifecycle.metadata.id
    
    # STARTING -> RUNNING
    metadata_running = lifecycle.transition_to_running()
    assert metadata_running.state == RenderExecutionState.RUNNING
    assert metadata_running.start_time is not None
    
    # Let time pass slightly to test elapsed_duration
    time.sleep(0.01)
    assert metadata_running.elapsed_duration_seconds > 0
    
    # RUNNING -> COMPLETED
    metadata_completed = lifecycle.transition_to_completed()
    assert metadata_completed.state == RenderExecutionState.COMPLETED
    assert metadata_completed.completion_time is not None
    assert metadata_completed.elapsed_duration_seconds is not None
    assert lifecycle.is_terminal

def test_valid_failed_transition_path():
    lifecycle = RenderExecutionLifecycle()
    lifecycle.transition_to_starting()
    
    metadata_failed = lifecycle.transition_to_failed()
    assert metadata_failed.state == RenderExecutionState.FAILED
    assert metadata_failed.completion_time is not None
    assert lifecycle.is_terminal

def test_valid_cancelled_transition_path():
    lifecycle = RenderExecutionLifecycle()
    
    # Cancel directly from queued
    metadata_cancelled = lifecycle.transition_to_cancelled()
    assert metadata_cancelled.state == RenderExecutionState.CANCELLED
    assert metadata_cancelled.completion_time is not None
    assert lifecycle.is_terminal
    
def test_invalid_transitions_rejected():
    lifecycle = RenderExecutionLifecycle()
    
    # Cannot jump QUEUED -> RUNNING
    with pytest.raises(InvalidStateTransitionError):
        lifecycle.transition_to_running()
        
    # Cannot jump QUEUED -> COMPLETED
    with pytest.raises(InvalidStateTransitionError):
        lifecycle.transition_to_completed()
        
    # Cannot fail from QUEUED
    with pytest.raises(InvalidStateTransitionError):
        lifecycle.transition_to_failed()
        
    lifecycle.transition_to_starting()
    
    # Cannot jump STARTING -> COMPLETED
    with pytest.raises(InvalidStateTransitionError):
        lifecycle.transition_to_completed()

def test_terminal_state_immutability():
    lifecycle = RenderExecutionLifecycle()
    lifecycle.transition_to_cancelled()
    
    with pytest.raises(InvalidStateTransitionError):
        lifecycle.transition_to_starting()
        
    with pytest.raises(InvalidStateTransitionError):
        lifecycle.transition_to_cancelled()

def test_metadata_immutability():
    lifecycle = RenderExecutionLifecycle()
    metadata_v1 = lifecycle.metadata
    
    metadata_v2 = lifecycle.transition_to_starting()
    
    assert metadata_v1.state == RenderExecutionState.QUEUED
    assert metadata_v2.state == RenderExecutionState.STARTING
    assert metadata_v1 is not metadata_v2
