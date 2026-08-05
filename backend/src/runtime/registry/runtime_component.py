from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .component_types import RuntimeComponentType
from .component_status import RuntimeComponentStatus

@dataclass(frozen=True)
class RuntimeComponent:
    """
    Immutable representation of Runtime Component metadata.
    
    This class represents only the metadata of a component. It has:
    - no execution logic
    - no provider awareness
    - no hardware awareness
    - no dependency resolution
    """
    component_id: str
    component_name: str
    component_type: RuntimeComponentType
    version: str
    description: str = ""
    lifecycle_state: str = "UNKNOWN"
    status: RuntimeComponentStatus = RuntimeComponentStatus.UNKNOWN
    capabilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
