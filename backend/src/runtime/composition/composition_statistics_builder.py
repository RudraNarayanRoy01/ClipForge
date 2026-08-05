from backend.src.runtime.registry.registry_snapshot import RegistrySnapshot
from backend.src.runtime.dependency.dependency_snapshot import DependencySnapshot
from .composition_statistics import CompositionStatistics

class CompositionStatisticsBuilder:
    """
    Builder for computing structural Runtime Composition statistics.
    
    Responsibilities:
    - Compute Runtime statistics
    - Compute component count
    - Compute dependency count
    - Compute root count
    - Compute leaf count
    - Compute disconnected count
    """
    
    @staticmethod
    def build(registry_snapshot: RegistrySnapshot, graph_snapshot: DependencySnapshot) -> CompositionStatistics:
        """
        Computes immutable statistics from the registry and graph snapshots.
        """
        component_count = len(registry_snapshot.components) if registry_snapshot and registry_snapshot.components else 0
        dependency_count = len(graph_snapshot.edges) if graph_snapshot and graph_snapshot.edges else 0
        root_count = len(graph_snapshot.root_nodes) if graph_snapshot and graph_snapshot.root_nodes else 0
        leaf_count = len(graph_snapshot.leaf_nodes) if graph_snapshot and graph_snapshot.leaf_nodes else 0
        disconnected_count = graph_snapshot.statistics.isolated_node_count if graph_snapshot and graph_snapshot.statistics else 0

        return CompositionStatistics(
            component_count=component_count,
            dependency_count=dependency_count,
            root_count=root_count,
            leaf_count=leaf_count,
            disconnected_count=disconnected_count
        )
