from .execution_scheduler_factory import ExecutionSchedulerFactory
from .execution_scheduler_descriptor_factory import ExecutionSchedulerDescriptorFactory
from .execution_scheduler_metadata_factory import ExecutionSchedulerMetadataFactory
from .execution_scheduler_statistics_builder import ExecutionSchedulerStatisticsBuilder
from .execution_scheduler_snapshot_factory import ExecutionSchedulerSnapshotFactory

class RuntimeExecutionSchedulerFactory:
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
    
    # Facade for backward compatibility or unified access
    create_scheduler = ExecutionSchedulerFactory.create
    create_descriptor = ExecutionSchedulerDescriptorFactory.create
    create_metadata = ExecutionSchedulerMetadataFactory.create
    build_statistics = ExecutionSchedulerStatisticsBuilder.build
    create_snapshot = ExecutionSchedulerSnapshotFactory.create
