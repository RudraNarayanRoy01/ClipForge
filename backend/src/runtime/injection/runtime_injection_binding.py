"""
Runtime Injection Binding.

Represents one immutable Runtime binding.
Describes the relationship between an interface and an implementation.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Tuple


@dataclass(frozen=True)
class RuntimeInjectionBinding:
    """
    Immutable representation of a service binding.
    Dictates what implementation satisfies what interface.
    """
    interface_id: str
    implementation_id: str
    service_id: str
    lifetime: str
    scope: str
    qualifiers: Tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
