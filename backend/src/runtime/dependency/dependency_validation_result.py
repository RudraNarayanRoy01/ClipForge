"""
Dependency Validation Result model.

Immutable representation of a validation pass over the graph.
"""

from dataclasses import dataclass, field
from typing import Tuple, FrozenSet

@dataclass(frozen=True)
class DependencyValidationResult:
    """
    Immutable result of graph validation.
    """
    success: bool
    cycles_detected: Tuple[Tuple[str, ...], ...] = field(default_factory=tuple)
    missing_components: FrozenSet[str] = field(default_factory=frozenset)
    orphan_nodes: FrozenSet[str] = field(default_factory=frozenset)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    validation_timestamp: float = 0.0
