"""
Runtime Service representation.
"""
from dataclasses import dataclass, field
from typing import Tuple, Mapping, Any
from types import MappingProxyType

@dataclass(frozen=True)
class RuntimeService:
    """Immutable representation of a Runtime Service."""
    service_id: str
    component_id: str
    service_name: str
    service_type: str
    lifetime: str
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    tags: Tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    
    def __post_init__(self):
        if not isinstance(self.dependencies, tuple):
            object.__setattr__(self, "dependencies", tuple(self.dependencies))
        if not isinstance(self.tags, tuple):
            object.__setattr__(self, "tags", tuple(self.tags))
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
