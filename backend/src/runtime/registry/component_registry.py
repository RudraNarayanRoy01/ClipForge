from typing import Dict, List, Optional
import time
from types import MappingProxyType
from .runtime_component import RuntimeComponent
from .component_types import RuntimeComponentType
from .component_status import RuntimeComponentStatus
from .registration_result import ComponentRegistrationResult
from .registry_snapshot import RegistrySnapshot
from .registry_statistics import RegistryStatistics
from .registry_exceptions import (
    DuplicateComponentException,
    UnknownComponentException,
    RegistryFrozenException,
    InvalidComponentException,
    RegistryConsistencyException
)

class RuntimeComponentRegistry:
    """
    The canonical catalog of Runtime Components.
    
    Responsibilities:
    - Register Component
    - Remove Component
    - Lookup by ID/Name
    - Enumerate Components
    - Freeze Registry
    - Generate Snapshot
    - Generate Statistics
    
    Explicitly NOT responsible for:
    - Component instantiation
    - Dependency resolution
    - Execution
    - Provider discovery
    """
    
    def __init__(self):
        self._components_by_id: Dict[str, RuntimeComponent] = {}
        self._components_by_name: Dict[str, RuntimeComponent] = {}
        self._ordered_ids: List[str] = []
        self._is_frozen: bool = False

    def _verify_consistency(self) -> None:
        """
        Internal helper to verify Registry consistency.
        Must remain private.
        """
        if len(self._components_by_id) != len(self._components_by_name):
            raise RegistryConsistencyException("ID and Name collections are out of sync.")
        if len(self._components_by_id) != len(self._ordered_ids):
            raise RegistryConsistencyException("ID collection and ordering array are out of sync.")
        for cid in self._ordered_ids:
            if cid not in self._components_by_id:
                raise RegistryConsistencyException(f"Ordered ID {cid} missing from ID collection.")
            comp = self._components_by_id[cid]
            if comp.component_name not in self._components_by_name:
                raise RegistryConsistencyException(f"Component name {comp.component_name} missing from Name collection.")

    def register(self, component: RuntimeComponent) -> ComponentRegistrationResult:
        if self._is_frozen:
            raise RegistryFrozenException("Cannot register component: Registry is frozen.")
            
        if not component.component_id:
            raise InvalidComponentException("Component must have a valid ID.")
            
        if not component.component_name:
            raise InvalidComponentException("Component must have a valid Name.")

        if not component.component_type:
            raise InvalidComponentException("Component must have a valid Type.")

        if not component.version:
            raise InvalidComponentException("Component must have a valid Version.")
            
        if component.component_id in self._components_by_id:
            raise DuplicateComponentException(f"Component ID '{component.component_id}' already registered.")
            
        if component.component_name in self._components_by_name:
            raise DuplicateComponentException(f"Component Name '{component.component_name}' already registered.")
            
        self._components_by_id[component.component_id] = component
        self._components_by_name[component.component_name] = component
        self._ordered_ids.append(component.component_id)
        
        self._verify_consistency()
        
        return ComponentRegistrationResult(
            success=True,
            registered_component=component,
            reason="Component successfully registered."
        )

    def remove(self, component_id: str) -> None:
        if self._is_frozen:
            raise RegistryFrozenException("Cannot remove component: Registry is frozen.")
            
        if component_id not in self._components_by_id:
            raise UnknownComponentException(f"Component ID '{component_id}' not found in registry.")
            
        component = self._components_by_id[component_id]
        
        del self._components_by_id[component_id]
        del self._components_by_name[component.component_name]
        self._ordered_ids.remove(component_id)
        
        self._verify_consistency()

    def get_by_id(self, component_id: str) -> RuntimeComponent:
        if component_id not in self._components_by_id:
            raise UnknownComponentException(f"Component ID '{component_id}' not found.")
        return self._components_by_id[component_id]

    def get_by_name(self, component_name: str) -> RuntimeComponent:
        if component_name not in self._components_by_name:
            raise UnknownComponentException(f"Component Name '{component_name}' not found.")
        return self._components_by_name[component_name]

    def enumerate_components(self) -> List[RuntimeComponent]:
        """
        The canonical enumeration API for Runtime Components.
        Returns components in their registration order.
        """
        return [self._components_by_id[cid] for cid in self._ordered_ids]

    def list_components(self) -> List[RuntimeComponent]:
        """
        Convenience wrapper around enumerate_components.
        """
        return self.enumerate_components()

    def freeze(self) -> None:
        """
        Freezes the Registry. 
        Registry freezing is intentionally irreversible during Batch 6A.5.2.
        """
        self._is_frozen = True

    def is_frozen(self) -> bool:
        return self._is_frozen

    def get_snapshot(self) -> RegistrySnapshot:
        components_tuple = tuple(self.enumerate_components())
        return RegistrySnapshot(
            components=components_tuple,
            timestamp=time.time()
        )

    def get_statistics(self) -> RegistryStatistics:
        type_counts: Dict[RuntimeComponentType, int] = {}
        status_counts: Dict[RuntimeComponentStatus, int] = {}
        
        for cid in self._ordered_ids:
            comp = self._components_by_id[cid]
            type_counts[comp.component_type] = type_counts.get(comp.component_type, 0) + 1
            status_counts[comp.status] = status_counts.get(comp.status, 0) + 1
            
        return RegistryStatistics(
            total_components=len(self._ordered_ids),
            components_by_type=MappingProxyType(type_counts),
            components_by_status=MappingProxyType(status_counts),
            registration_order=tuple(self._ordered_ids)
        )
