from .runtime_execution_builder import RuntimeExecutionBuilder
from .runtime_execution_builder_identity import RuntimeExecutionBuilderIdentity
from .runtime_execution_builder_validator import RuntimeExecutionBuilderValidator

class RuntimeExecutionBuilderFactory:
    """
    ONLY performs structural construction.
    Performs NO Execution, Scheduling, Lifecycle, Telemetry, Monitoring, Optimization, Provider Loading, Hardware Management, Routing, Planning.
    """
    
    @staticmethod
    def create(
        identifier: str,
        identity: RuntimeExecutionBuilderIdentity
    ) -> RuntimeExecutionBuilder:
        builder = RuntimeExecutionBuilder(
            identifier=identifier,
            identity=identity
        )
        RuntimeExecutionBuilderValidator.validate(builder)
        return builder
