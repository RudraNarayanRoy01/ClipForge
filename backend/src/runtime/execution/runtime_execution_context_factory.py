import uuid
from typing import Tuple, Dict, Set
from .runtime_execution_variable import RuntimeExecutionVariable
from .runtime_execution_binding import RuntimeExecutionBinding
from .runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor
from .runtime_execution_context import RuntimeExecutionContext
from .execution_context_factory import ExecutionContextFactory

class RuntimeExecutionContextFactory:
    """
    Constructs the root Runtime Execution Context structurally.
    
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
        descriptor: RuntimeExecutionContextDescriptor,
        variables: Tuple[RuntimeExecutionVariable, ...],
        bindings: Tuple[RuntimeExecutionBinding, ...],
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionContext:
        
        identifier = str(uuid.uuid4())
        
        identity = ExecutionContextFactory.create(
            descriptor=descriptor,
            variables=variables,
            bindings=bindings,
            labels=labels,
            annotations=annotations,
            tags=tags
        )
        
        return RuntimeExecutionContext(
            identifier=identifier,
            identity=identity
        )
