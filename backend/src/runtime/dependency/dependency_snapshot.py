"""
Dependency Snapshot model.

Immutable, deterministic point-in-time capture of the Dependency Graph.
"""

from dataclasses import dataclass, field
from typing import Optional, FrozenSet, Tuple
from .runtime_dependency import RuntimeDependency
from .dependency_statistics import DependencyStatistics
from .dependency_validation_result import DependencyValidationResult

@dataclass(frozen=True)
class DependencySnapshot:
    """
    Immutable snapshot of the Dependency Graph.
    
    Contains graph metadata, nodes, edges, statistics, and validation results.
    """
    graph_identifier: str
    graph_version: int
    created_at: float
    frozen: bool
    nodes: FrozenSet[str] = field(default_factory=frozenset)
    edges: Tuple[RuntimeDependency, ...] = field(default_factory=tuple)
    root_nodes: FrozenSet[str] = field(default_factory=frozenset)
    leaf_nodes: FrozenSet[str] = field(default_factory=frozenset)
    statistics: Optional[DependencyStatistics] = None
    validation_summary: Optional[DependencyValidationResult] = None
