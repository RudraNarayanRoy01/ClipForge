from .runtime_execution import RuntimeExecution
from .runtime_execution_metadata import RuntimeExecutionMetadata
from .runtime_execution_state import RuntimeExecutionState
from .runtime_execution_exceptions import ExecutionValidationException, ExecutionMetadataException, ExecutionStateException
from .execution_stage import ExecutionStage

class RuntimeExecutionValidator:
    """
    Validator validates ONLY:
    - RuntimeExecutionDescriptor
    - RuntimeExecutionMetadata
    - RuntimeExecutionState

    Validator MUST NOT validate:
    - Execution Graph
    - Execution Plan
    - Execution Context
    - Runtime Lifecycle
    - Providers
    - Scheduler
    - Monitoring
    - Telemetry
    - Optimization

    Pure structural validation only.
    """
    @staticmethod
    def validate_execution(execution: RuntimeExecution) -> None:
        if not execution:
            raise ExecutionValidationException("Execution cannot be None.")
        if not execution.identifier or not isinstance(execution.identifier, str) or not execution.identifier.strip():
            raise ExecutionValidationException("Execution must have a valid identifier.")
        if not execution.identity:
            raise ExecutionValidationException("Execution must have a valid identity.")
        RuntimeExecutionValidator.validate_metadata(execution.identity.metadata)
        RuntimeExecutionValidator.validate_state(execution.identity.state)

    @staticmethod
    def validate_metadata(metadata: RuntimeExecutionMetadata) -> None:
        if not metadata:
            raise ExecutionMetadataException("Metadata cannot be None.")
        if not metadata.name or not isinstance(metadata.name, str) or not metadata.name.strip():
            raise ExecutionMetadataException("Metadata name must be a valid string.")
        if metadata.tags is None:
            raise ExecutionMetadataException("Metadata tags cannot be None.")
        if metadata.annotations is None:
            raise ExecutionMetadataException("Metadata annotations cannot be None.")

    @staticmethod
    def validate_state(state: RuntimeExecutionState) -> None:
        if not state:
            raise ExecutionStateException("State cannot be None.")
        if not isinstance(state.stage, ExecutionStage):
            raise ExecutionStateException("State stage must be a valid ExecutionStage.")
