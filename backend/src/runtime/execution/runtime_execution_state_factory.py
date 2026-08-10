from .execution_state_descriptor_factory import ExecutionStateDescriptorFactory
from .execution_state_metadata_factory import ExecutionStateMetadataFactory
from .execution_state_statistics_builder import ExecutionStateStatisticsBuilder
from .execution_state_snapshot_factory import ExecutionStateSnapshotFactory
from .execution_state_factory import ExecutionStateFactory

class RuntimeExecutionStateFactory:
    """Facade for the Runtime Execution State Factory"""
    
    create_state = ExecutionStateFactory.create
    create_descriptor = ExecutionStateDescriptorFactory.create
    create_metadata = ExecutionStateMetadataFactory.create
    build_statistics = ExecutionStateStatisticsBuilder.build
    create_snapshot = ExecutionStateSnapshotFactory.create
