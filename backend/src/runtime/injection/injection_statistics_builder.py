"""
Injection Statistics Builder.

Pure computation for generating InjectionStatistics and RuntimeInjectionGraphStatistics.
No Runtime awareness, no mutation.
"""
from typing import Mapping, Tuple

from .injection_descriptor import InjectionDescriptor
from .injection_statistics import InjectionStatistics
from .runtime_injection_binding import RuntimeInjectionBinding
from .runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics


class InjectionStatisticsBuilder:
    """
    Computes purely observational statistics from the injection graph structure.
    """

    def build(
        self,
        bindings: Tuple[RuntimeInjectionBinding, ...],
        injection_graph: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> InjectionStatistics:
        """
        Computes the statistics without evaluating quality or executing logic.
        """
        total_bindings = len(bindings)
        
        singleton_bindings = sum(1 for b in bindings if b.lifetime == "SINGLETON")
        transient_bindings = sum(1 for b in bindings if b.lifetime == "TRANSIENT")
        scoped_bindings = sum(1 for b in bindings if b.lifetime == "SCOPED")

        interface_count = len({b.interface_id for b in bindings})
        implementation_count = len({b.implementation_id for b in bindings})

        required_deps = 0
        optional_deps = 0
        edge_count = 0

        for descriptors in injection_graph.values():
            for desc in descriptors:
                edge_count += 1
                if desc.optional:
                    optional_deps += 1
                else:
                    required_deps += 1

        # Calculate roots and leaves
        all_services = {b.interface_id for b in bindings}
        vertex_count = len(all_services)
        
        # Services that are depended upon
        depended_upon = {desc.dependency_service for desc_list in injection_graph.values() for desc in desc_list}
        
        # Services that have dependencies
        has_dependencies = {svc for svc, desc_list in injection_graph.items() if desc_list}

        root_count = len(all_services - depended_upon)
        leaf_count = len(all_services - has_dependencies)

        # Depth
        graph_depth = self._calculate_maximum_depth(all_services - depended_upon, injection_graph)

        # Width
        graph_width = self._calculate_maximum_width(all_services - depended_upon, injection_graph)

        # Degree calculations
        in_degrees = {svc: 0 for svc in all_services}
        out_degrees = {svc: 0 for svc in all_services}
        for src, descriptors in injection_graph.items():
            out_degrees[src] += len(descriptors)
            for desc in descriptors:
                if desc.dependency_service in in_degrees:
                    in_degrees[desc.dependency_service] += 1
                    
        degrees = [in_degrees[svc] + out_degrees[svc] for svc in all_services]
        max_degree = max(degrees) if degrees else 0
        min_degree = min(degrees) if degrees else 0
        avg_degree = sum(degrees) / len(degrees) if degrees else 0.0

        # Connected components (undirected)
        connected_components = self._calculate_connected_components(all_services, injection_graph)

        graph_statistics = RuntimeInjectionGraphStatistics(
            edge_count=edge_count,
            vertex_count=vertex_count,
            root_count=root_count,
            leaf_count=leaf_count,
            connected_components=connected_components,
            graph_depth=graph_depth,
            graph_width=graph_width,
            average_degree=avg_degree,
            maximum_degree=max_degree,
            minimum_degree=min_degree
        )

        return InjectionStatistics(
            binding_count=total_bindings,
            interface_count=interface_count,
            implementation_count=implementation_count,
            singleton_bindings=singleton_bindings,
            transient_bindings=transient_bindings,
            scoped_bindings=scoped_bindings,
            optional_dependency_count=optional_deps,
            required_dependency_count=required_deps,
            graph_statistics=graph_statistics
        )

    def _calculate_maximum_depth(
        self, roots: set[str], injection_graph: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> int:
        if not roots:
            return 0
            
        def get_depth(node: str) -> int:
            neighbors = [desc.dependency_service for desc in injection_graph.get(node, ())]
            if not neighbors:
                return 1
            return 1 + max((get_depth(n) for n in neighbors), default=0)

        return max((get_depth(root) for root in roots), default=0)
        
    def _calculate_maximum_width(
        self, roots: set[str], injection_graph: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> int:
        if not roots:
            return 0
        
        levels = {}
        def traverse(node: str, level: int):
            levels[level] = levels.get(level, 0) + 1
            neighbors = [desc.dependency_service for desc in injection_graph.get(node, ())]
            for n in neighbors:
                traverse(n, level + 1)
                
        for root in roots:
            traverse(root, 0)
            
        return max(levels.values()) if levels else 0

    def _calculate_connected_components(
        self, vertices: set[str], injection_graph: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> int:
        # Undirected graph for connected components
        adj = {v: set() for v in vertices}
        for src, descriptors in injection_graph.items():
            if src in adj:
                for desc in descriptors:
                    if desc.dependency_service in adj:
                        adj[src].add(desc.dependency_service)
                        adj[desc.dependency_service].add(src)
                        
        visited = set()
        components = 0
        
        for v in vertices:
            if v not in visited:
                components += 1
                stack = [v]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        stack.extend(adj[node] - visited)
                        
        return components
