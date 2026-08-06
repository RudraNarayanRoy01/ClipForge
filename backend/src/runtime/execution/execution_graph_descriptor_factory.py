import uuid
from .runtime_execution_graph_descriptor import RuntimeExecutionGraphDescriptor
from .execution_graph_id_factory import ExecutionGraphIdFactory
from .execution_id_factory import ExecutionIdFactory

class ExecutionGraphDescriptorFactory:
    """
    Creates immutable metadata.
    
    Performs NO:
    - execution
    - scheduling
    - provider loading
    - lifecycle
    - dependency injection
    - orchestration
    - planning
    - monitoring
    - optimization
    """
    @staticmethod
    def create_descriptor(
        execution_id: str = None,
        runtime_id: str = None,
        graph_id: str = None,
        version: str = "1.0.0",
        schema_version: str = "1.0"
    ) -> RuntimeExecutionGraphDescriptor:
        return RuntimeExecutionGraphDescriptor(
            execution_id=execution_id or f"exec-{uuid.uuid4()}",
            runtime_id=runtime_id or f"runtime-{uuid.uuid4()}",
            graph_id=graph_id or ExecutionGraphIdFactory.generate_graph_id(),
            version=version,
            schema_version=schema_version
        )
