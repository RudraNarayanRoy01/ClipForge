"""
Runtime Injection Graph.

Canonical artifact owning the injection graph topology.
Strictly structural. No execution logic.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Tuple

from .injection_descriptor import InjectionDescriptor
from .runtime_injection_binding import RuntimeInjectionBinding


@dataclass(frozen=True)
class RuntimeInjectionGraph:
    """
    Immutable representation of the graph topology.
    Owns bindings, adjacency, reverse adjacency, roots, leaves, and lookups.
    """
    bindings: Tuple[RuntimeInjectionBinding, ...]
    adjacency: Mapping[str, Tuple[InjectionDescriptor, ...]] = field(default_factory=lambda: MappingProxyType({}))
    reverse_adjacency: Mapping[str, Tuple[str, ...]] = field(default_factory=lambda: MappingProxyType({}))
    roots: Tuple[str, ...] = field(default_factory=tuple)
    leaves: Tuple[str, ...] = field(default_factory=tuple)
    
    # Immutable lookup structures
    binding_lookup: Mapping[str, RuntimeInjectionBinding] = field(default_factory=lambda: MappingProxyType({}))
    interface_lookup: Mapping[str, Tuple[RuntimeInjectionBinding, ...]] = field(default_factory=lambda: MappingProxyType({}))
    implementation_lookup: Mapping[str, Tuple[RuntimeInjectionBinding, ...]] = field(default_factory=lambda: MappingProxyType({}))
