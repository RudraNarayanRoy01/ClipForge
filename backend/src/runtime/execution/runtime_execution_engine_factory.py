from .execution_engine_factory import ExecutionEngineFactory
from .execution_engine_descriptor_factory import ExecutionEngineDescriptorFactory
from .execution_engine_metadata_factory import ExecutionEngineMetadataFactory
from .execution_engine_statistics_builder import ExecutionEngineStatisticsBuilder
from .execution_engine_snapshot_factory import ExecutionEngineSnapshotFactory

class RuntimeExecutionEngineFactory:
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
    
    # Facade for backward compatibility or unified access
    create_engine = ExecutionEngineFactory.create
    create_descriptor = ExecutionEngineDescriptorFactory.create
    create_metadata = ExecutionEngineMetadataFactory.create
    build_statistics = ExecutionEngineStatisticsBuilder.build
    create_snapshot = ExecutionEngineSnapshotFactory.create
