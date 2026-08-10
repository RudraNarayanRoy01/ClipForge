import hashlib
from types import MappingProxyType
from typing import Any
from .runtime_execution_dispatcher_descriptor import RuntimeExecutionDispatcherDescriptor
from .runtime_execution_dispatcher_metadata import RuntimeExecutionDispatcherMetadata
from .runtime_execution_dispatcher_statistics import RuntimeExecutionDispatcherStatistics
from .runtime_execution_dispatcher_snapshot import RuntimeExecutionDispatcherSnapshot
from .runtime_execution_state import RuntimeExecutionState

class ExecutionDispatcherSnapshotFactory:
    @staticmethod
    def create(
        descriptor: RuntimeExecutionDispatcherDescriptor,
        metadata: RuntimeExecutionDispatcherMetadata,
        statistics: RuntimeExecutionDispatcherStatistics,
        runtime_execution_state: RuntimeExecutionState,
        state_lookup: MappingProxyType[str, Any],
        descriptor_lookup: MappingProxyType[str, Any],
        dispatcher_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionDispatcherSnapshot:
        def compute_hash(data: str) -> str:
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
            
        def compute_dict_hash(d: dict) -> str:
            sorted_items = sorted(d.items(), key=lambda item: item[0])
            joined_items = "|".join([f"{k}:{v}" for k, v in sorted_items])
            return compute_hash(joined_items)
            
        descriptor_hash = compute_hash(f"{descriptor.execution_id}|{descriptor.runtime_id}|{descriptor.graph_id}|{descriptor.plan_id}|{descriptor.context_id}|{descriptor.composition_id}|{descriptor.builder_id}|{descriptor.lifecycle_id}|{descriptor.scheduler_id}|{descriptor.engine_id}|{descriptor.session_id}|{descriptor.state_id}|{descriptor.dispatcher_id}|{descriptor.version}|{descriptor.schema_version}")
        
        state_hash = compute_hash(runtime_execution_state.identifier) if runtime_execution_state else compute_hash("")
        state_lookup_hash = compute_dict_hash({k: "1" for k in state_lookup.keys()})
        descriptor_lookup_hash = compute_dict_hash({k: "1" for k in descriptor_lookup.keys()})
        dispatcher_lookup_hash = compute_dict_hash({k: "1" for k in dispatcher_lookup.keys()})
        
        labels_hash = compute_dict_hash(dict(metadata.labels))
        annotations_hash = compute_dict_hash(dict(metadata.annotations))
        tags_hash = compute_hash("|".join(sorted(metadata.tags)))
        metadata_hash = compute_hash(f"{labels_hash}|{annotations_hash}|{tags_hash}")
        
        statistics_hash = compute_hash(f"{statistics.state_count}|{statistics.state_lookup_count}|{statistics.descriptor_lookup_count}|{statistics.dispatcher_lookup_count}")
        
        dispatcher_hash = compute_hash(f"{descriptor_hash}|{state_hash}|{state_lookup_hash}|{descriptor_lookup_hash}|{dispatcher_lookup_hash}|{metadata_hash}|{statistics_hash}")
        
        return RuntimeExecutionDispatcherSnapshot(
            descriptor_hash=descriptor_hash,
            state_hash=state_hash,
            state_lookup_hash=state_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            dispatcher_lookup_hash=dispatcher_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            dispatcher_hash=dispatcher_hash
        )
