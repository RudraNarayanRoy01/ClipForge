"""
Injection Snapshot.

Immutable Runtime Injection Snapshot.
Represents a specific deterministic point-in-time state of the injection composition.
Includes deterministic structural hashes.
"""
from dataclasses import dataclass

from .injection_metadata import InjectionMetadata
from .injection_statistics import InjectionStatistics
from .runtime_injection_graph import RuntimeInjectionGraph


@dataclass(frozen=True)
class InjectionSnapshot:
    """
    Immutable snapshot of the Runtime Dependency Injection Foundation.
    Contains deterministic hashes for observational tracking.
    """
    composition_id: str
    graph: RuntimeInjectionGraph
    metadata: InjectionMetadata
    statistics: InjectionStatistics
    
    # Deterministic Hashes
    binding_hash: str
    graph_hash: str
    metadata_hash: str
