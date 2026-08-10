from .execution_session_descriptor_factory import ExecutionSessionDescriptorFactory
from .execution_session_metadata_factory import ExecutionSessionMetadataFactory
from .execution_session_statistics_builder import ExecutionSessionStatisticsBuilder
from .execution_session_snapshot_factory import ExecutionSessionSnapshotFactory
from .execution_session_factory import ExecutionSessionFactory

class RuntimeExecutionSessionFactory:
    """Facade for the Runtime Execution Session Factory"""
    
    create_session = ExecutionSessionFactory.create
    create_descriptor = ExecutionSessionDescriptorFactory.create
    create_metadata = ExecutionSessionMetadataFactory.create
    build_statistics = ExecutionSessionStatisticsBuilder.build
    create_snapshot = ExecutionSessionSnapshotFactory.create
