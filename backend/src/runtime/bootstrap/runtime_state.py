from enum import Enum, auto
from typing import Dict, List, Optional


class RuntimeState(Enum):
    """
    Deterministic states of the Runtime lifecycle.
    Only strictly defined transitions between these states are permitted.
    """
    CREATED = auto()
    BOOTSTRAPPING = auto()
    INITIALIZING = auto()
    VALIDATING = auto()
    READY = auto()
    SHUTTING_DOWN = auto()
    STOPPED = auto()
    FAILED = auto()


class RuntimeStateMachine:
    """
    Isolates Runtime transition rules and state management.
    Ensures that only legal transitions are permitted.
    """

    _TRANSITIONS: Dict[RuntimeState, List[RuntimeState]] = {
        RuntimeState.CREATED: [RuntimeState.BOOTSTRAPPING, RuntimeState.FAILED],
        RuntimeState.BOOTSTRAPPING: [RuntimeState.INITIALIZING, RuntimeState.FAILED],
        RuntimeState.INITIALIZING: [RuntimeState.VALIDATING, RuntimeState.FAILED],
        RuntimeState.VALIDATING: [RuntimeState.READY, RuntimeState.FAILED],
        RuntimeState.READY: [RuntimeState.SHUTTING_DOWN, RuntimeState.FAILED],
        RuntimeState.SHUTTING_DOWN: [RuntimeState.STOPPED, RuntimeState.FAILED],
        RuntimeState.STOPPED: [],
        RuntimeState.FAILED: [],
    }

    def __init__(self):
        self._state = RuntimeState.CREATED

    @property
    def current_state(self) -> RuntimeState:
        return self._state

    def transition(self, target_state: RuntimeState) -> None:
        """
        Attempts a transition to the target state.
        Raises InvalidRuntimeStateTransitionException if illegal.
        """
        from .bootstrap_exceptions import InvalidRuntimeStateTransitionException
        
        allowed = self._TRANSITIONS.get(self._state, [])
        if target_state not in allowed:
            raise InvalidRuntimeStateTransitionException(self._state, target_state)
            
        self._state = target_state

    def force_fail(self) -> None:
        """Forces the machine into the FAILED state to guarantee safety upon unexpected errors."""
        if self._state != RuntimeState.FAILED:
            self._state = RuntimeState.FAILED

    def reset(self) -> None:
        """
        Resets the state machine back to CREATED.
        Only permitted from terminal states (STOPPED, FAILED, or READY for restart).
        """
        from .bootstrap_exceptions import InvalidRuntimeStateTransitionException
        if self._state in (RuntimeState.READY, RuntimeState.STOPPED, RuntimeState.FAILED):
            self._state = RuntimeState.CREATED
        else:
            raise InvalidRuntimeStateTransitionException(
                self._state, 
                RuntimeState.CREATED, 
                "Cannot restart from an active transitional state"
            )
