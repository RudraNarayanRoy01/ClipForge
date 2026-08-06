from .runtime_execution_composition_descriptor import RuntimeExecutionCompositionDescriptor

class ExecutionCompositionDescriptorFactory:
    """
    Performs ONLY structural construction.
    
    NEVER performs:
    - execution
    - lifecycle
    - scheduling
    - provider loading
    - telemetry
    - monitoring
    - optimization
    - planning
    """
    @staticmethod
    def create(
        execution_id: str,
        runtime_id: str,
        graph_id: str,
        plan_id: str,
        context_id: str,
        composition_id: str,
        version: str = "1.0.0",
        schema_version: str = "1.0.0"
    ) -> RuntimeExecutionCompositionDescriptor:
        return RuntimeExecutionCompositionDescriptor(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            composition_id=composition_id,
            version=version,
            schema_version=schema_version
        )
