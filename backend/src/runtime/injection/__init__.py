"""
Runtime Injection Foundation Public API.

Exports ONLY the public boundary for the Runtime Injection subsystem.
Implementation details are intentionally hidden.
"""

from .injection_descriptor import InjectionDescriptor
from .injection_exceptions import (
    CircularInjectionException,
    DuplicateBindingException,
    InjectionCompositionException,
    InjectionException,
    InjectionValidationException,
    InvalidInjectionException,
    MissingImplementationException,
)
from .injection_metadata import InjectionMetadata
from .injection_result import InjectionResult
from .injection_snapshot import InjectionSnapshot
from .injection_statistics import InjectionStatistics
from .runtime_injection_binding import RuntimeInjectionBinding
from .runtime_injection_builder import RuntimeInjectionBuilder
from .runtime_injection_composition import RuntimeInjectionComposition
from .runtime_injection_graph import RuntimeInjectionGraph
from .runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics

__all__ = [
    "InjectionDescriptor",
    "RuntimeInjectionBinding",
    "RuntimeInjectionGraph",
    "RuntimeInjectionComposition",
    "InjectionResult",
    "RuntimeInjectionBuilder",
    "InjectionMetadata",
    "InjectionStatistics",
    "RuntimeInjectionGraphStatistics",
    "InjectionSnapshot",
    "InjectionException",
    "InjectionValidationException",
    "DuplicateBindingException",
    "CircularInjectionException",
    "InvalidInjectionException",
    "MissingImplementationException",
    "InjectionCompositionException",
]
