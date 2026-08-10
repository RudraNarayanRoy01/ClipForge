from .runtime_execution_dispatcher_descriptor import RuntimeExecutionDispatcherDescriptor

class ExecutionDispatcherDescriptorFactory:
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
        session_id: str,
        state_id: str,
        dispatcher_id: str,
        version: str,
        schema_version: str
    ) -> RuntimeExecutionDispatcherDescriptor:
        return RuntimeExecutionDispatcherDescriptor(
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
            session_id=session_id,
            state_id=state_id,
            dispatcher_id=dispatcher_id,
            version=version,
            schema_version=schema_version
        )
