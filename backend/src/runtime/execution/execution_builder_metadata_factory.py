from types import MappingProxyType
from typing import Dict, Set

from .runtime_execution_builder_metadata import RuntimeExecutionBuilderMetadata

class ExecutionBuilderMetadataFactory:
    """
    ONLY performs structural construction.
    Performs NO Execution, Scheduling, Lifecycle, Telemetry, Monitoring, Optimization, Provider Loading, Hardware Management, Routing, Planning.
    """
    
    @staticmethod
    def create(
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionBuilderMetadata:
        return RuntimeExecutionBuilderMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=frozenset(tags)
        )
