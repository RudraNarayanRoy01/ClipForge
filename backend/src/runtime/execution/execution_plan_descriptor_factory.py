from .runtime_execution_plan_descriptor import RuntimeExecutionPlanDescriptor

class ExecutionPlanDescriptorFactory:
    
    @classmethod
    def create(cls, 
               execution_id: str,
               runtime_id: str,
               graph_id: str,
               plan_id: str,
               version: str,
               schema_version: str) -> RuntimeExecutionPlanDescriptor:
        return RuntimeExecutionPlanDescriptor(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            version=version,
            schema_version=schema_version
        )
