import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from .bootstrap_configuration import BootstrapConfiguration
from .bootstrap_context import BootstrapContext
from .bootstrap_result import BootstrapResult
from .runtime_state import RuntimeState
from .bootstrap_exceptions import (
    BootstrapInitializationException,
    BootstrapValidationException,
)


class BootstrapStage(ABC):
    """
    Abstract interface for pipeline stages, allowing clean future extension.
    Stages must execute synchronously and assume previous stages succeeded.
    Implementations should perform a specific initialization or validation duty
    without assuming provider availability or managing threading.
    """
    @abstractmethod
    def execute(self, context: BootstrapContext) -> None:
        """Executes the specific stage responsibility against the provided context."""
        pass


class CoreInitializationStage(BootstrapStage):
    """Handles minimal foundational core initialization."""
    def execute(self, context: BootstrapContext) -> None:
        try:
            if context.configuration.startup_logging:
                context.bootstrap_metadata["logging_initialized"] = True
            
            components = context.execution_context.setdefault("initialized_components", [])
            components.extend(["BootstrapContext", "BootstrapConfiguration"])
        except Exception as e:
            raise BootstrapInitializationException(f"CoreInitializationStage failed: {e}")


class CoreValidationStage(BootstrapStage):
    """Validates core initialization success."""
    def execute(self, context: BootstrapContext) -> None:
        try:
            if context.configuration.validation_enabled:
                components = context.execution_context.get("initialized_components", [])
                if not components:
                    raise ValueError("No components were initialized.")
                
                if context.configuration.strict_bootstrap_mode:
                    if "BootstrapContext" not in components:
                        raise ValueError("Core bootstrap context missing in strict mode.")
                        
                context.bootstrap_metadata["validation_passed"] = True
        except Exception as e:
            raise BootstrapValidationException(f"CoreValidationStage failed: {e}")


class BootstrapPipeline:
    """
    Modular bootstrap workflow.
    Executes a series of extensible initialization and validation stages.
    """

    def __init__(self):
        self._initialization_stages: List[BootstrapStage] = [
            CoreInitializationStage()
        ]
        self._validation_stages: List[BootstrapStage] = [
            CoreValidationStage()
        ]
        
    def register_initialization_stage(self, stage: BootstrapStage) -> None:
        self._initialization_stages.append(stage)
        
    def register_validation_stage(self, stage: BootstrapStage) -> None:
        self._validation_stages.append(stage)

    def create_context(self, configuration: BootstrapConfiguration) -> BootstrapContext:
        """Creates the initial BootstrapContext."""
        return BootstrapContext(
            configuration=configuration,
            environment=dict(os.environ),
            bootstrap_metadata={"schema_version": "1.0"},
            execution_context={"initialized_components": []}
        )

    def initialize_runtime(self, context: BootstrapContext) -> None:
        """Executes all registered initialization stages."""
        for stage in self._initialization_stages:
            stage.execute(context)

    def validate_runtime(self, context: BootstrapContext) -> None:
        """Executes all registered validation stages."""
        for stage in self._validation_stages:
            stage.execute(context)

    def finalize_startup(self, context: BootstrapContext, state: RuntimeState, duration: float, failures: list = None) -> BootstrapResult:
        """Produces the immutable BootstrapResult."""
        failures = failures or []
        success = state == RuntimeState.READY and not failures
        
        components = context.execution_context.get("initialized_components", []) if context else []
        diagnostics = context.bootstrap_metadata if context else {}
        
        return BootstrapResult(
            success=success,
            runtime_state=state,
            duration=duration,
            warnings=[],
            failures=failures,
            initialized_components=components,
            diagnostics=diagnostics
        )
