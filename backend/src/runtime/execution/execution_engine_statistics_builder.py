from typing import Any, Dict

from .runtime_execution_engine_statistics import RuntimeExecutionEngineStatistics
from .runtime_execution_scheduler import RuntimeExecutionScheduler

class ExecutionEngineStatisticsBuilder:
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
    def build(
        runtime_execution_scheduler: RuntimeExecutionScheduler,
        scheduler_lookup: Dict[str, RuntimeExecutionScheduler],
        descriptor_lookup: Dict[str, Any],
        engine_lookup: Dict[str, Any]
    ) -> RuntimeExecutionEngineStatistics:
        return RuntimeExecutionEngineStatistics(
            scheduler_count=1 if runtime_execution_scheduler else 0,
            scheduler_lookup_count=len(scheduler_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            engine_lookup_count=len(engine_lookup)
        )
