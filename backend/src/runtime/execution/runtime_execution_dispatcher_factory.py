from .execution_dispatcher_descriptor_factory import ExecutionDispatcherDescriptorFactory
from .execution_dispatcher_metadata_factory import ExecutionDispatcherMetadataFactory
from .execution_dispatcher_statistics_builder import ExecutionDispatcherStatisticsBuilder
from .execution_dispatcher_snapshot_factory import ExecutionDispatcherSnapshotFactory
from .execution_dispatcher_factory import ExecutionDispatcherFactory

class RuntimeExecutionDispatcherFactory:
    """Facade for the Runtime Execution Dispatcher Factory"""
    
    create_dispatcher = ExecutionDispatcherFactory.create
    create_descriptor = ExecutionDispatcherDescriptorFactory.create
    create_metadata = ExecutionDispatcherMetadataFactory.create
    build_statistics = ExecutionDispatcherStatisticsBuilder.build
    create_snapshot = ExecutionDispatcherSnapshotFactory.create
