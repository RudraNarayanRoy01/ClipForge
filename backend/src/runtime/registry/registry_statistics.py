from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Tuple
from .component_types import RuntimeComponentType
from .component_status import RuntimeComponentStatus

@dataclass(frozen=True)
class RegistryStatistics:
    """
    Immutable Registry metadata statistics.
    """
    total_components: int = 0
    components_by_type: Mapping[RuntimeComponentType, int] = field(default_factory=lambda: MappingProxyType({}))
    components_by_status: Mapping[RuntimeComponentStatus, int] = field(default_factory=lambda: MappingProxyType({}))
    registration_order: Tuple[str, ...] = field(default_factory=tuple)
