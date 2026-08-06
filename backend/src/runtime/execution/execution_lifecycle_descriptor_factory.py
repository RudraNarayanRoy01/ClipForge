from .runtime_execution_lifecycle_descriptor import RuntimeExecutionLifecycleDescriptor

class ExecutionLifecycleDescriptorFactory:
    """
    ONLY performs structural construction.
    Performs NO:
    - Execution
    - Scheduling
    - Lifecycle Behaviour
    - Monitoring
    - Telemetry
    - Optimization
    - Provider Loading
    - Hardware Management
    - Routing
    - Planning
    """
    
    @staticmethod
    def create(
        execution_id: str,
        runtime_id: str,
        graph_id: str,
        plan_id: str,
        context_id: str,
        composition_id: str,
        builder_id: str,
        lifecycle_id: str,
        version: str,
        schema_version: str
    ) -> RuntimeExecutionLifecycleDescriptor:
        return RuntimeExecutionLifecycleDescriptor(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            composition_id=composition_id,
            builder_id=builder_id,
            lifecycle_id=lifecycle_id,
            version=version,
            schema_version=schema_version
        )
