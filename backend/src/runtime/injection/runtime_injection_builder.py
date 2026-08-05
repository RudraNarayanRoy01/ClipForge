"""
Runtime Injection Builder.

Thin orchestration pipeline for constructing the Runtime Injection Composition.
Delegates all logic to specialized factories and validators.
"""
from typing import Mapping, Tuple

from .injection_descriptor import InjectionDescriptor
from .injection_exceptions import InjectionValidationException
from .injection_graph_factory import InjectionGraphFactory
from .injection_id_factory import InjectionIdFactory
from .injection_metadata_factory import InjectionMetadataFactory
from .injection_result import InjectionResult
from .injection_snapshot_factory import InjectionSnapshotFactory
from .injection_statistics_builder import InjectionStatisticsBuilder
from .injection_validator import InjectionValidator
from .runtime_injection_binding import RuntimeInjectionBinding
from .runtime_injection_factory import RuntimeInjectionFactory


class RuntimeInjectionBuilder:
    """
    Thin orchestrator. Contains NO business logic.
    Pipeline: Validation -> Factories -> Graph Factory -> Metadata Factory -> Statistics Builder -> Snapshot Factory -> Composition -> Result
    """

    def __init__(self) -> None:
        self._validator = InjectionValidator()
        self._id_factory = InjectionIdFactory()
        self._metadata_factory = InjectionMetadataFactory()
        self._graph_factory = InjectionGraphFactory()
        self._statistics_builder = InjectionStatisticsBuilder()
        self._snapshot_factory = InjectionSnapshotFactory()
        self._composition_factory = RuntimeInjectionFactory()

    def build(
        self,
        bindings: Tuple[RuntimeInjectionBinding, ...],
        adjacency: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> InjectionResult:
        """
        Orchestrates the construction of the Runtime Injection Composition.
        """
        try:
            # 1. Validation
            self._validator.validate_bindings(bindings)
            self._validator.validate_graph(bindings, adjacency)

            # 2. Factories & Creation
            composition_id = self._id_factory.create()
            
            # 3. Graph Factory
            graph = self._graph_factory.create(bindings, adjacency)
            
            # 4. Metadata Factory
            metadata = self._metadata_factory.create()

            # 5. Statistics Builder
            statistics = self._statistics_builder.build(bindings, adjacency)

            # 6. Snapshot Factory
            snapshot = self._snapshot_factory.create(
                composition_id=composition_id,
                graph=graph,
                metadata=metadata,
                statistics=statistics
            )

            # 7. Composition
            composition = self._composition_factory.create(
                composition_id=composition_id,
                graph=graph,
                metadata=metadata,
                statistics=statistics,
                snapshot=snapshot
            )

            # 8. Result
            return InjectionResult(success=True, composition=composition)

        except InjectionValidationException as e:
            return InjectionResult(success=False, errors=(str(e),))
        except Exception as e:
            return InjectionResult(success=False, errors=(f"Unexpected error: {str(e)}",))
