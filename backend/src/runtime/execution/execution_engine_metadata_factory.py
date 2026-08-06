from types import MappingProxyType
from typing import Dict, Set

from .runtime_execution_engine_metadata import RuntimeExecutionEngineMetadata

class ExecutionEngineMetadataFactory:
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
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionEngineMetadata:
        return RuntimeExecutionEngineMetadata(
            labels=MappingProxyType(dict(labels)),
            annotations=MappingProxyType(dict(annotations)),
            tags=frozenset(tags)
        )
