import hashlib
from .runtime_execution_descriptor import RuntimeExecutionDescriptor
from .runtime_execution_metadata import RuntimeExecutionMetadata
from .runtime_execution_state import RuntimeExecutionState
from .runtime_execution_snapshot import RuntimeExecutionSnapshot

class ExecutionSnapshotFactory:
    @staticmethod
    def _hash_string(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def create_snapshot(
        descriptor: RuntimeExecutionDescriptor,
        metadata: RuntimeExecutionMetadata,
        state: RuntimeExecutionState,
        composition_hash: str
    ) -> RuntimeExecutionSnapshot:
        descriptor_hash = ExecutionSnapshotFactory._hash_string(
            f"{descriptor.execution_id}:{descriptor.runtime_id}:{descriptor.bootstrap_id}:{descriptor.version}:{descriptor.schema_version}"
        )
        tags_str = ",".join(sorted(metadata.tags))
        annotations_str = ",".join(f"{k}={v}" for k, v in sorted(metadata.annotations.items()))
        metadata_hash = ExecutionSnapshotFactory._hash_string(
            f"{metadata.name}:{metadata.description}:{metadata.created_at.isoformat()}:{metadata.updated_at.isoformat()}:{tags_str}:{annotations_str}:{metadata.metadata_version}"
        )
        state_hash = ExecutionSnapshotFactory._hash_string(f"{state.stage.name}")
        
        identity_hash = ExecutionSnapshotFactory._hash_string(
            f"{descriptor_hash}:{metadata_hash}:{state_hash}"
        )
        
        execution_hash = ExecutionSnapshotFactory._hash_string(
            f"{identity_hash}:{composition_hash}"
        )
        
        return RuntimeExecutionSnapshot(
            execution_hash=execution_hash,
            identity_hash=identity_hash,
            descriptor_hash=descriptor_hash,
            metadata_hash=metadata_hash,
            state_hash=state_hash,
            composition_hash=composition_hash
        )
