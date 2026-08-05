"""
Injection Graph Factory.

SRP-compliant factory for generating the RuntimeInjectionGraph.
"""
from types import MappingProxyType
from typing import Mapping, Tuple

from .injection_descriptor import InjectionDescriptor
from .runtime_injection_binding import RuntimeInjectionBinding
from .runtime_injection_graph import RuntimeInjectionGraph


class InjectionGraphFactory:
    """Creates the immutable graph topology artifact."""
    
    def create(
        self,
        bindings: Tuple[RuntimeInjectionBinding, ...],
        adjacency: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> RuntimeInjectionGraph:
        """Constructs the canonical graph from raw bindings and adjacency lists."""
        
        # Calculate lookups
        binding_lookup = {b.service_id: b for b in bindings}
        
        interface_lookup = {}
        implementation_lookup = {}
        for b in bindings:
            interface_lookup.setdefault(b.interface_id, []).append(b)
            implementation_lookup.setdefault(b.implementation_id, []).append(b)
            
        # Convert to immutable structures
        frozen_interface_lookup = {k: tuple(v) for k, v in interface_lookup.items()}
        frozen_implementation_lookup = {k: tuple(v) for k, v in implementation_lookup.items()}

        # Calculate reverse adjacency, roots, leaves
        reverse_adjacency = {}
        has_dependencies = set()
        depended_upon = set()
        
        for service_id, descriptors in adjacency.items():
            if descriptors:
                has_dependencies.add(service_id)
            for desc in descriptors:
                dep_id = desc.dependency_service
                depended_upon.add(dep_id)
                reverse_adjacency.setdefault(dep_id, []).append(service_id)
                
        frozen_reverse_adjacency = {k: tuple(sorted(v)) for k, v in reverse_adjacency.items()}
        
        all_interfaces = {b.interface_id for b in bindings}
        roots = tuple(sorted(all_interfaces - depended_upon))
        leaves = tuple(sorted(all_interfaces - has_dependencies))

        return RuntimeInjectionGraph(
            bindings=bindings,
            adjacency=MappingProxyType(dict(adjacency)),
            reverse_adjacency=MappingProxyType(frozen_reverse_adjacency),
            roots=roots,
            leaves=leaves,
            binding_lookup=MappingProxyType(binding_lookup),
            interface_lookup=MappingProxyType(frozen_interface_lookup),
            implementation_lookup=MappingProxyType(frozen_implementation_lookup)
        )
