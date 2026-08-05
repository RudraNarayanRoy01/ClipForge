"""
Injection Descriptor.

Immutable description of one injection dependency relationship.
Contains metadata only, with no execution logic.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class InjectionDescriptor:
    """
    Immutable representation of an injection target.
    Describes what dependency is needed and how it should be provided.
    """
    dependency_type: str
    optional: bool
    injection_kind: str
    scope: str
    target_service: str
    dependency_service: str
    qualifier: Optional[str] = None
