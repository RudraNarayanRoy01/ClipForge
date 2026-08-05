"""
Runtime Dependency model.

Immutable representation of a single directed relationship in the graph.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .dependency_type import DependencyType

@dataclass(frozen=True)
class RuntimeDependency:
    """
    Immutable representation of a dependency edge.
    
    This class is purely descriptive and contains no execution logic.
    """
    dependency_id: str
    source_component_id: str
    target_component_id: str
    dependency_type: DependencyType
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
