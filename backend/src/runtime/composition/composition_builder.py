from typing import Tuple, List

from backend.src.runtime.registry.component_registry import RuntimeComponentRegistry
from backend.src.runtime.dependency.dependency_graph import RuntimeDependencyGraph

from .runtime_composition import RuntimeComposition
from .composition_result import CompositionResult
from .composition_exceptions import (
    CompositionBuildException,
    CompositionValidationException,
    IncompleteCompositionException
)
from .composition_validator import CompositionValidator
from .composition_statistics_builder import CompositionStatisticsBuilder
from .composition_metadata_factory import CompositionMetadataFactory
from .composition_id_factory import CompositionIdFactory

class RuntimeCompositionBuilder:
    """
    Builds the Runtime Composition from the Registry and Dependency Graph.
    
    Responsibilities:
    - Receive Registry
    - Receive Dependency Graph
    - Call Validator
    - Call Metadata Factory
    - Call Statistics Builder
    - Call ID Factory
    - Assemble RuntimeComposition
    - Return CompositionResult
    
    Explicitly DOES NOT:
    - Instantiate Components
    - Execute Runtime
    - Perform Dependency Injection
    """
    
    def __init__(self, builder_version: str = "1.0.0"):
        self._builder_version = builder_version

    def build(
        self, 
        registry: RuntimeComponentRegistry, 
        graph: RuntimeDependencyGraph
    ) -> CompositionResult:
        warnings: List[str] = []
        errors: List[str] = []
        
        try:
            # 1. Validate
            validation_warnings = CompositionValidator.validate(registry, graph)
            warnings.extend(validation_warnings)
            
            # Snapshots for assembly
            registry_snapshot = registry.get_snapshot()
            graph_snapshot = graph.create_snapshot()
            
            # 2. Build Statistics
            stats = CompositionStatisticsBuilder.build(registry_snapshot, graph_snapshot)
            
            # 3. Create Metadata
            metadata = CompositionMetadataFactory.create(
                builder_version=self._builder_version,
                schema_version="1.0.0",
                composition_version="1.0.0"
            )
            
            # 4. Generate ID
            comp_id = CompositionIdFactory.generate_id()
            
            # 5. Assemble Composition
            composition = RuntimeComposition(
                composition_id=comp_id,
                components=registry_snapshot.components,
                dependencies=graph_snapshot.edges,
                metadata=metadata,
                statistics=stats
            )
            
            # 6. Return Result
            return CompositionResult(
                success=True,
                composition=composition,
                warnings=tuple(warnings),
                errors=tuple(errors)
            )
            
        except Exception as e:
            if not isinstance(e, (CompositionValidationException, IncompleteCompositionException)):
                errors.append(str(e))
                raise CompositionBuildException(f"Failed to build composition: {str(e)}") from e
            raise
