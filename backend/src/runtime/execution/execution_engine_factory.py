from types import MappingProxyType
from typing import Any

from .runtime_execution_engine import RuntimeExecutionEngine
from .runtime_execution_engine_identity import RuntimeExecutionEngineIdentity
from .runtime_execution_engine_descriptor import RuntimeExecutionEngineDescriptor
from .runtime_execution_engine_metadata import RuntimeExecutionEngineMetadata
from .runtime_execution_engine_statistics import RuntimeExecutionEngineStatistics
from .runtime_execution_engine_snapshot import RuntimeExecutionEngineSnapshot
from .runtime_execution_scheduler import RuntimeExecutionScheduler

class ExecutionEngineFactory:
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
        identifier: str,
        descriptor: RuntimeExecutionEngineDescriptor,
        metadata: RuntimeExecutionEngineMetadata,
        statistics: RuntimeExecutionEngineStatistics,
        snapshot: RuntimeExecutionEngineSnapshot,
        runtime_execution_scheduler: RuntimeExecutionScheduler,
        scheduler_lookup: MappingProxyType[str, RuntimeExecutionScheduler],
        descriptor_lookup: MappingProxyType[str, Any],
        engine_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionEngine:
        
        identity = RuntimeExecutionEngineIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            runtime_execution_scheduler=runtime_execution_scheduler,
            scheduler_lookup=scheduler_lookup,
            descriptor_lookup=descriptor_lookup,
            engine_lookup=engine_lookup
        )
        
        return RuntimeExecutionEngine(
            identifier=identifier,
            identity=identity
        )
