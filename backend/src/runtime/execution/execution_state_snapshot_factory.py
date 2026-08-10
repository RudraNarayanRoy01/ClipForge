import hashlib
from types import MappingProxyType
from typing import Any
from .runtime_execution_state_descriptor import RuntimeExecutionStateDescriptor
from .runtime_execution_state_metadata import RuntimeExecutionStateMetadata
from .runtime_execution_state_statistics import RuntimeExecutionStateStatistics
from .runtime_execution_state_snapshot import RuntimeExecutionStateSnapshot
from .runtime_execution_session import RuntimeExecutionSession

class ExecutionStateSnapshotFactory:
    @staticmethod
    def create(
        descriptor: RuntimeExecutionStateDescriptor,
        metadata: RuntimeExecutionStateMetadata,
        statistics: RuntimeExecutionStateStatistics,
        runtime_execution_session: RuntimeExecutionSession,
        session_lookup: MappingProxyType[str, RuntimeExecutionSession],
        descriptor_lookup: MappingProxyType[str, Any],
        state_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionStateSnapshot:
        def compute_hash(data: str) -> str:
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
            
        def compute_dict_hash(d: dict) -> str:
            sorted_items = sorted(d.items(), key=lambda item: item[0])
            joined_items = "|".join([f"{k}:{v}" for k, v in sorted_items])
            return compute_hash(joined_items)
            
        descriptor_hash = compute_hash(f"{descriptor.execution_id}|{descriptor.runtime_id}|{descriptor.graph_id}|{descriptor.plan_id}|{descriptor.context_id}|{descriptor.composition_id}|{descriptor.builder_id}|{descriptor.lifecycle_id}|{descriptor.scheduler_id}|{descriptor.engine_id}|{descriptor.session_id}|{descriptor.state_id}|{descriptor.version}|{descriptor.schema_version}")
        
        session_hash = compute_hash(runtime_execution_session.identifier) if runtime_execution_session else compute_hash("")
        session_lookup_hash = compute_dict_hash({k: "1" for k in session_lookup.keys()})
        descriptor_lookup_hash = compute_dict_hash({k: "1" for k in descriptor_lookup.keys()})
        state_lookup_hash = compute_dict_hash({k: "1" for k in state_lookup.keys()})
        
        labels_hash = compute_dict_hash(dict(metadata.labels))
        annotations_hash = compute_dict_hash(dict(metadata.annotations))
        tags_hash = compute_hash("|".join(sorted(metadata.tags)))
        metadata_hash = compute_hash(f"{labels_hash}|{annotations_hash}|{tags_hash}")
        
        statistics_hash = compute_hash(f"{statistics.session_count}|{statistics.session_lookup_count}|{statistics.descriptor_lookup_count}|{statistics.state_lookup_count}")
        
        state_hash = compute_hash(f"{descriptor_hash}|{session_hash}|{session_lookup_hash}|{descriptor_lookup_hash}|{state_lookup_hash}|{metadata_hash}|{statistics_hash}")
        
        return RuntimeExecutionStateSnapshot(
            descriptor_hash=descriptor_hash,
            session_hash=session_hash,
            session_lookup_hash=session_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            state_lookup_hash=state_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            state_hash=state_hash
        )
