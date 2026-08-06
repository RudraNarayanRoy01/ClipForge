from .runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor

class ExecutionContextDescriptorFactory:
    """
    Constructs context descriptors structurally.
    
    Performs NO:
    - Execution
    - Scheduling
    - Provider Loading
    - Lifecycle
    - Optimization
    - Telemetry
    - Monitoring
    - Planning
    """
    @staticmethod
    def create(
        execution_id: str,
        runtime_id: str,
        graph_id: str,
        plan_id: str,
        context_id: str,
        version: str,
        schema_version: str
    ) -> RuntimeExecutionContextDescriptor:
        return RuntimeExecutionContextDescriptor(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            version=version,
            schema_version=schema_version
        )
