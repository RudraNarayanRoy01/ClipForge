from types import MappingProxyType
from typing import Dict, Set
from .runtime_execution_scheduler_metadata import RuntimeExecutionSchedulerMetadata

class ExecutionSchedulerMetadataFactory:
    """
    ONLY performs structural construction.

    Performs NO:

    Execution
    Scheduling
    Monitoring
    Telemetry
    Optimization
    Provider Loading
    Hardware Management
    Routing
    Planning
    """
    
    @staticmethod
    def create(
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionSchedulerMetadata:
        return RuntimeExecutionSchedulerMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=frozenset(tags)
        )
