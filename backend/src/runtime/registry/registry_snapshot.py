from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from .runtime_component import RuntimeComponent

@dataclass(frozen=True)
class RegistrySnapshot:
    """
    Immutable representation of a point-in-time Registry view.
    """
    components: Tuple[RuntimeComponent, ...]
    timestamp: float
    
    @property
    def component_count(self) -> int:
        return len(self.components)
