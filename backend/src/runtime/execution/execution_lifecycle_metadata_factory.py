from types import MappingProxyType
from typing import Dict, Set

from .runtime_execution_lifecycle_metadata import RuntimeExecutionLifecycleMetadata

class ExecutionLifecycleMetadataFactory:
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
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionLifecycleMetadata:
        return RuntimeExecutionLifecycleMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=frozenset(tags)
        )
