"""
Injection Statistics.

Immutable statistics for the Runtime Injection Foundation.
Reflects overall bindings and dependencies, delegating topology to GraphStatistics.
"""
from dataclasses import dataclass

from .runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics


@dataclass(frozen=True)
class InjectionStatistics:
    """
    Purely observational statistics for the injection composition.
    Never evaluates Runtime quality or executes logic.
    """
    binding_count: int
    interface_count: int
    implementation_count: int
    singleton_bindings: int
    transient_bindings: int
    scoped_bindings: int
    optional_dependency_count: int
    required_dependency_count: int
    graph_statistics: RuntimeInjectionGraphStatistics
