"""
Runtime Bootstrap Builder.

Thin orchestration pipeline for assembling the canonical Runtime Bootstrap Foundation.
Contains ZERO business logic. Delegates everything to independent factories.
"""
from typing import Dict, Set, List, Optional

from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from .runtime_bootstrap_layer import RuntimeBootstrapLayer
from .runtime_bootstrap_composition import RuntimeBootstrapComposition
from .bootstrap_result import BootstrapResult
from .bootstrap_exceptions import BootstrapValidationException

from .runtime_bootstrap_validator import RuntimeBootstrapValidator
from .bootstrap_id_factory import BootstrapIdFactory
from .bootstrap_metadata_factory import BootstrapMetadataFactory
from .bootstrap_graph_factory import BootstrapGraphFactory
from .bootstrap_plan_factory import BootstrapPlanFactory
from .bootstrap_statistics_builder import BootstrapStatisticsBuilder
from .bootstrap_snapshot_factory import BootstrapSnapshotFactory
from .runtime_bootstrap_factory import RuntimeBootstrapFactory


class RuntimeBootstrapBuilder:
    """
    Builder orchestrating the assembly of the Runtime Bootstrap composition.
    
    Pipeline Stages:
    1. Validation
    2. Identifier Generation
    3. Metadata Generation
    4. Graph Construction
    5. Plan Construction
    6. Statistics Construction
    7. Snapshot Construction
    8. Composition Assembly
    9. RuntimeBootstrapFactory
    10. BootstrapResult
    """

    def __init__(self):
        self._validator = RuntimeBootstrapValidator()
        self._id_factory = BootstrapIdFactory()
        self._metadata_factory = BootstrapMetadataFactory()
        self._graph_factory = BootstrapGraphFactory()
        self._plan_factory = BootstrapPlanFactory()
        self._statistics_builder = BootstrapStatisticsBuilder()
        self._snapshot_factory = BootstrapSnapshotFactory()
        self._bootstrap_factory = RuntimeBootstrapFactory()

    def build(
        self,
        descriptor: RuntimeBootstrapDescriptor,
        descriptors: Dict[str, RuntimeBootstrapDescriptor],
        layers: List[RuntimeBootstrapLayer],
        adjacency: Dict[str, Set[str]],
        version: str = "1.0",
        schema_version: str = "1.0",
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ) -> BootstrapResult:
        """Executes the canonical Runtime Bootstrap."""
        warnings: List[str] = []
        errors: List[str] = []
        
        try:
            # 1. Validation
            self._validator.validate_inputs(descriptor, descriptors, layers, adjacency)

            # 2. Identifier Generation
            composition_id = self._id_factory.generate_composition_id()
            bootstrap_id = self._id_factory.generate_runtime_bootstrap_id()

            # 3. Metadata Generation
            metadata = self._metadata_factory.create_metadata(
                version=version,
                schema_version=schema_version,
                labels=labels,
                annotations=annotations,
                description=description
            )

            # 4. Graph Construction
            graph = self._graph_factory.build_graph(
                descriptors=descriptors,
                layers={layer.layer_identifier: layer for layer in layers},
                adjacency=adjacency
            )

            # 5. Plan Construction
            plan = self._plan_factory.build_plan(layers=layers)

            # 6. Statistics Construction
            graph_stats, plan_stats = self._statistics_builder.build_statistics(graph, plan)

            # 7. Snapshot Construction
            snapshot = self._snapshot_factory.build_snapshot(
                graph=graph,
                plan=plan,
                metadata=metadata,
                graph_statistics=graph_stats,
                statistics=plan_stats
            )

            # 8. Composition Assembly
            composition = RuntimeBootstrapComposition(
                composition_id=composition_id,
                graph=graph,
                plan=plan,
                metadata=metadata,
                graph_statistics=graph_stats,
                statistics=plan_stats,
                snapshot=snapshot
            )

            # 9. RuntimeBootstrapFactory
            bootstrap = self._bootstrap_factory.build_bootstrap(
                bootstrap_id=bootstrap_id,
                descriptor=descriptor,
                composition=composition
            )
            
            # 10. BootstrapResult
            return BootstrapResult(
                bootstrap=bootstrap,
                composition=composition,
                snapshot=snapshot,
                statistics=plan_stats,
                warnings=tuple(warnings),
                errors=tuple(errors)
            )
            
        except BootstrapValidationException as e:
            errors.append(str(e))
            return BootstrapResult(
                bootstrap=None, # type: ignore
                composition=None, # type: ignore
                snapshot=None, # type: ignore
                statistics=None, # type: ignore
                warnings=tuple(warnings),
                errors=tuple(errors)
            )
        except Exception as e:
            errors.append(f"Unexpected error during bootstrap build: {str(e)}")
            return BootstrapResult(
                bootstrap=None, # type: ignore
                composition=None, # type: ignore
                snapshot=None, # type: ignore
                statistics=None, # type: ignore
                warnings=tuple(warnings),
                errors=tuple(errors)
            )
