from typing import Dict, Set
from types import MappingProxyType
from .runtime_execution_context_metadata import RuntimeExecutionContextMetadata

class ExecutionContextMetadataFactory:
    """
    Constructs immutable metadata structurally.
    
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
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionContextMetadata:
        return RuntimeExecutionContextMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=frozenset(tags)
        )
