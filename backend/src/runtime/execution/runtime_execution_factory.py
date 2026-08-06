from .runtime_execution import RuntimeExecution
from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_validator import RuntimeExecutionValidator

class RuntimeExecutionFactory:
    @staticmethod
    def create_execution(
        identifier: str,
        identity: RuntimeExecutionIdentity
    ) -> RuntimeExecution:
        execution = RuntimeExecution(
            identifier=identifier,
            identity=identity
        )
        RuntimeExecutionValidator.validate_execution(execution)
        return execution
