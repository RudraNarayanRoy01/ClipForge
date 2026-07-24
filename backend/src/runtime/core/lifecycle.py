from enum import Enum, auto
from typing import List

from ..contracts.lifecycle_aware import ILifecycleAware


class RuntimeLifecycleState(Enum):
    """
    Represents the complete lifecycle of the Adaptive AI Runtime.
    """
    UNINITIALIZED = auto()
    BOOTSTRAPPING = auto()
    INITIALIZED = auto()
    SHUTTING_DOWN = auto()
    SHUTDOWN = auto()


class RuntimeLifecycleCoordinator:
    """
    Architectural coordinator for the Runtime lifecycle.
    
    Responsible for transitioning between lifecycle states and notifying
    registered ILifecycleAware components. It does NOT manage execution logic.
    """

    def __init__(self) -> None:
        self._state = RuntimeLifecycleState.UNINITIALIZED
        self._components: List[ILifecycleAware] = []

    @property
    def current_state(self) -> RuntimeLifecycleState:
        return self._state

    def register_component(self, component: ILifecycleAware) -> None:
        """Register a component to receive lifecycle notifications."""
        if component not in self._components:
            self._components.append(component)

    def transition_to(self, target_state: RuntimeLifecycleState) -> None:
        """
        Transition the Runtime to a new state and notify components.
        
        Note: In a mature implementation, this would enforce valid state 
        machine transitions (e.g., cannot go from SHUTDOWN to INITIALIZED).
        """
        self._state = target_state

        if self._state == RuntimeLifecycleState.BOOTSTRAPPING:
            self._notify_bootstrap()
        elif self._state == RuntimeLifecycleState.INITIALIZED:
            self._notify_initialize()
        elif self._state == RuntimeLifecycleState.SHUTTING_DOWN:
            self._notify_shutdown()
        # SHUTDOWN and UNINITIALIZED typically don't have explicit notification phases

    def _notify_bootstrap(self) -> None:
        for component in self._components:
            component.on_bootstrap()

    def _notify_initialize(self) -> None:
        for component in self._components:
            component.on_initialize()

    def _notify_shutdown(self) -> None:
        for component in reversed(self._components):
            component.on_shutdown()
