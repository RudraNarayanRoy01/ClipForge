"""
Runtime Injection Factory.

SRP-compliant factory for assembling the final RuntimeInjectionComposition artifact.
"""
from .injection_metadata import InjectionMetadata
from .injection_snapshot import InjectionSnapshot
from .injection_statistics import InjectionStatistics
from .runtime_injection_composition import RuntimeInjectionComposition
from .runtime_injection_graph import RuntimeInjectionGraph


class RuntimeInjectionFactory:
    """Creates the canonical Runtime Injection Composition."""
    
    def create(
        self,
        composition_id: str,
        graph: RuntimeInjectionGraph,
        metadata: InjectionMetadata,
        statistics: InjectionStatistics,
        snapshot: InjectionSnapshot
    ) -> RuntimeInjectionComposition:
        """Constructs the final immutable composition representation."""
        return RuntimeInjectionComposition(
            composition_id=composition_id,
            graph=graph,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot
        )
