from .runtime_execution_engine_descriptor import RuntimeExecutionEngineDescriptor

class ExecutionEngineDescriptorFactory:
    """
    ONLY performs structural construction.

    Performs NO:

    Execution
    Scheduling
    Providers
    Monitoring
    Telemetry
    Optimization
    Routing
    Planning
    Hardware
    Dependency Injection
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
        scheduler_id: str,
        engine_id: str,
        version: str,
        schema_version: str
    ) -> RuntimeExecutionEngineDescriptor:
        return RuntimeExecutionEngineDescriptor(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            composition_id=composition_id,
            builder_id=builder_id,
            lifecycle_id=lifecycle_id,
            scheduler_id=scheduler_id,
            engine_id=engine_id,
            version=version,
            schema_version=schema_version
        )
