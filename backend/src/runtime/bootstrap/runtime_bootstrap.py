import time
from typing import Optional, List

from .runtime_state import RuntimeState, RuntimeStateMachine
from .bootstrap_configuration import BootstrapConfiguration
from .bootstrap_context import BootstrapContext
from .bootstrap_result import BootstrapResult
from .bootstrap_pipeline import BootstrapPipeline
from .bootstrap_exceptions import (
    RuntimeBootstrapException,
    BootstrapInitializationException,
    BootstrapValidationException,
    BootstrapShutdownException,
    InvalidRuntimeStateTransitionException,
)
from .runtime_events import (
    RuntimeEvent,
    RuntimeCreated,
    BootstrapStarted,
    InitializationStarted,
    ValidationStarted,
    RuntimeReady,
    ShutdownStarted,
    RuntimeStopped,
    BootstrapFailed,
)


class RuntimeBootstrap:
    """
    The Runtime Bootstrap Engine.
    Orchestrates the Runtime lifecycle from creation into a deterministic READY state.
    It strictly isolates orchestration from the internal transition validation rules.
    """

    def __init__(self, configuration: Optional[BootstrapConfiguration] = None):
        self._state_machine = RuntimeStateMachine()
        self._configuration = configuration or BootstrapConfiguration()
        self._context: Optional[BootstrapContext] = None
        self._pipeline = BootstrapPipeline()
        self._events: List[RuntimeEvent] = []
        # Publish the initial creation event
        self._publish(RuntimeCreated,
            configuration_summary={
                "startup_timeout": self._configuration.startup_timeout,
                "strict_mode": self._configuration.strict_bootstrap_mode
            }
        )

    def _publish(self, event_class: type[RuntimeEvent], **kwargs) -> None:
        """
        Instantiates and publishes a structured lifecycle event immutably.
        Ensures the runtime identifier is attached if available.
        """
        if self._context:
            kwargs.setdefault('runtime_identifier', self._context.runtime_identifier)
            
        event = event_class(**kwargs)
        self._events.append(event)

    def state(self) -> RuntimeState:
        """Returns the current state of the Runtime."""
        return self._state_machine.current_state

    def bootstrap(self) -> BootstrapResult:
        """
        Executes the full bootstrap sequence.
        Returns an immutable BootstrapResult.
        """
        start_time = time.monotonic()
        try:
            self._state_machine.transition(RuntimeState.BOOTSTRAPPING)
            self._publish(BootstrapStarted)
            
            self._context = self._pipeline.create_context(self._configuration)
            
            self.initialize()
            self.validate()
            
            duration = time.monotonic() - start_time
            self._publish(RuntimeReady,
                duration=duration,
                initialized_components=self._context.execution_context.get("initialized_components", [])
            )
            return self._pipeline.finalize_startup(self._context, self._state_machine.current_state, duration)
            
        except RuntimeBootstrapException as e:
            self._force_fail(str(e))
            raise
        except Exception as e:
            self._force_fail(str(e))
            raise RuntimeBootstrapException(
                f"Unexpected bootstrap failure: {str(e)}", 
                state=self._state_machine.current_state, 
                reason=str(e)
            )

    def _force_fail(self, reason: str) -> None:
        """Forces failure safely and emits a failure event."""
        self._state_machine.force_fail()
        diagnostics = self._context.bootstrap_metadata if self._context else {}
        self._publish(BootstrapFailed,
            reason=reason,
            state=self._state_machine.current_state.name,
            diagnostics=diagnostics
        )

    def initialize(self) -> None:
        """Initializes the Runtime using the pipeline."""
        if self._state_machine.current_state != RuntimeState.BOOTSTRAPPING:
            raise InvalidRuntimeStateTransitionException(self._state_machine.current_state, RuntimeState.INITIALIZING)
            
        try:
            self._state_machine.transition(RuntimeState.INITIALIZING)
            self._publish(InitializationStarted)
            
            if self._context is None:
                raise BootstrapInitializationException("Context is not initialized", state=self._state_machine.current_state)
            self._pipeline.initialize_runtime(self._context)
        except Exception as e:
            if not isinstance(e, InvalidRuntimeStateTransitionException):
                raise BootstrapInitializationException(f"Initialization failed: {str(e)}", state=self._state_machine.current_state, reason=str(e))
            raise

    def validate(self) -> None:
        """Validates the initialized Runtime using the pipeline."""
        if self._state_machine.current_state != RuntimeState.INITIALIZING:
            raise InvalidRuntimeStateTransitionException(self._state_machine.current_state, RuntimeState.VALIDATING)
            
        try:
            self._state_machine.transition(RuntimeState.VALIDATING)
            self._publish(ValidationStarted)
            
            if self._context is None:
                raise BootstrapValidationException("Context is not initialized", state=self._state_machine.current_state)
            self._pipeline.validate_runtime(self._context)
            
            self._state_machine.transition(RuntimeState.READY)
        except Exception as e:
            if not isinstance(e, InvalidRuntimeStateTransitionException):
                raise BootstrapValidationException(f"Validation failed: {str(e)}", state=self._state_machine.current_state, reason=str(e))
            raise

    def shutdown(self) -> None:
        """Shuts down the Runtime safely."""
        try:
            self._state_machine.transition(RuntimeState.SHUTTING_DOWN)
            self._publish(ShutdownStarted)
            
            # Future: Execute shutdown pipeline logic here
            
            self._state_machine.transition(RuntimeState.STOPPED)
            self._publish(RuntimeStopped)
            self._context = None
        except Exception as e:
            if not isinstance(e, InvalidRuntimeStateTransitionException):
                self._force_fail(str(e))
                raise BootstrapShutdownException(f"Shutdown failed: {str(e)}", state=self._state_machine.current_state, reason=str(e))
            raise

    def restart(self) -> BootstrapResult:
        """
        Restarts the Runtime from READY, STOPPED, or FAILED states.
        """
        if self._state_machine.current_state == RuntimeState.READY:
            try:
                self.shutdown()
            except BootstrapShutdownException:
                pass  # Ignore shutdown errors during restart
            
        self._state_machine.reset()
        self._events.clear()
        
        # Re-publish CREATED event for the new lifecycle
        self._publish(RuntimeCreated,
            configuration_summary={
                "startup_timeout": self._configuration.startup_timeout,
                "strict_mode": self._configuration.strict_bootstrap_mode
            }
        )
        return self.bootstrap()
