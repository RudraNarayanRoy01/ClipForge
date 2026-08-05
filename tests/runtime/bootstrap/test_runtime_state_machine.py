import pytest
from backend.src.runtime.bootstrap.runtime_state import RuntimeState, RuntimeStateMachine
from backend.src.runtime.bootstrap.bootstrap_exceptions import InvalidRuntimeStateTransitionException

def test_state_machine_initialization():
    machine = RuntimeStateMachine()
    assert machine.current_state == RuntimeState.CREATED

def test_state_machine_valid_transitions():
    machine = RuntimeStateMachine()
    machine.transition(RuntimeState.BOOTSTRAPPING)
    assert machine.current_state == RuntimeState.BOOTSTRAPPING
    
    machine.transition(RuntimeState.INITIALIZING)
    assert machine.current_state == RuntimeState.INITIALIZING
    
    machine.transition(RuntimeState.VALIDATING)
    assert machine.current_state == RuntimeState.VALIDATING
    
    machine.transition(RuntimeState.READY)
    assert machine.current_state == RuntimeState.READY
    
    machine.transition(RuntimeState.SHUTTING_DOWN)
    assert machine.current_state == RuntimeState.SHUTTING_DOWN
    
    machine.transition(RuntimeState.STOPPED)
    assert machine.current_state == RuntimeState.STOPPED

def test_state_machine_invalid_transition():
    machine = RuntimeStateMachine()
    with pytest.raises(InvalidRuntimeStateTransitionException):
        machine.transition(RuntimeState.READY)
    assert machine.current_state == RuntimeState.CREATED

def test_state_machine_force_fail():
    machine = RuntimeStateMachine()
    machine.transition(RuntimeState.BOOTSTRAPPING)
    machine.force_fail()
    assert machine.current_state == RuntimeState.FAILED
    
    # Repeated calls shouldn't do anything
    machine.force_fail()
    assert machine.current_state == RuntimeState.FAILED

def test_state_machine_reset():
    machine = RuntimeStateMachine()
    machine.force_fail()
    machine.reset()
    assert machine.current_state == RuntimeState.CREATED
    
    machine.transition(RuntimeState.BOOTSTRAPPING)
    with pytest.raises(InvalidRuntimeStateTransitionException):
        machine.reset()
