from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionGraphSnapshot:
    descriptor_hash: str
    node_hash: str
    edge_hash: str
    graph_hash: str
    lookup_hash: str
    metadata_hash: str
    graph_statistics_hash: str
    snapshot_hash: str
