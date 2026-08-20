import hashlib
from types import MappingProxyType
from typing import Any
from .runtime_execution_session_descriptor import RuntimeExecutionSessionDescriptor
from .runtime_execution_session_metadata import RuntimeExecutionSessionMetadata
from .runtime_execution_session_statistics import RuntimeExecutionSessionStatistics
from .runtime_execution_session_snapshot import RuntimeExecutionSessionSnapshot
class ExecutionSessionSnapshotFactory:
    @staticmethod
    def create(
        descriptor: RuntimeExecutionSessionDescriptor,
        metadata: RuntimeExecutionSessionMetadata,
        statistics: RuntimeExecutionSessionStatistics,
        descriptor_lookup: MappingProxyType[str, Any],
        session_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionSessionSnapshot:
        def compute_hash(data: str) -> str:
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
            
        def compute_dict_hash(d: dict) -> str:
            sorted_items = sorted(d.items(), key=lambda item: item[0])
            joined_items = "|".join([f"{k}:{v}" for k, v in sorted_items])
            return compute_hash(joined_items)
            
        descriptor_hash = compute_hash(f"{descriptor.execution_id}|{descriptor.runtime_id}|{descriptor.graph_id}|{descriptor.plan_id}|{descriptor.context_id}|{descriptor.composition_id}|{descriptor.builder_id}|{descriptor.lifecycle_id}|{descriptor.scheduler_id}|{descriptor.session_id}|{descriptor.version}|{descriptor.schema_version}")
        

        descriptor_lookup_hash = compute_dict_hash({k: "1" for k in descriptor_lookup.keys()})
        session_lookup_hash = compute_dict_hash({k: "1" for k in session_lookup.keys()})
        
        labels_hash = compute_dict_hash(dict(metadata.labels))
        annotations_hash = compute_dict_hash(dict(metadata.annotations))
        tags_hash = compute_hash("|".join(sorted(metadata.tags)))
        metadata_hash = compute_hash(f"{labels_hash}|{annotations_hash}|{tags_hash}")
        
        statistics_hash = compute_hash(f"{statistics.descriptor_lookup_count}|{statistics.session_lookup_count}")
        
        session_hash = compute_hash(f"{descriptor_hash}|{descriptor_lookup_hash}|{session_lookup_hash}|{metadata_hash}|{statistics_hash}")
        
        return RuntimeExecutionSessionSnapshot(
            descriptor_hash=descriptor_hash,

            descriptor_lookup_hash=descriptor_lookup_hash,
            session_lookup_hash=session_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            session_hash=session_hash
        )
