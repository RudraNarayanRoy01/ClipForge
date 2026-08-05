from backend.src.runtime.composition.runtime_composition import RuntimeComposition
from .runtime_resolution import RuntimeResolution
from .resolution_result import ResolutionResult
from .resolution_validator import ResolutionValidator
from .resolution_algorithm import ResolutionAlgorithm
from .resolution_statistics_builder import ResolutionStatisticsBuilder
from .resolution_factories import ResolutionMetadataFactory, ResolutionIdFactory
from .resolution_exceptions import ResolutionCycleException

class RuntimeDependencyResolver:
    """
    Thin orchestration layer.
    
    Coordinates:
    ResolutionValidator -> ResolutionAlgorithm -> ResolutionStatisticsBuilder ->
    ResolutionMetadataFactory -> ResolutionIdFactory -> RuntimeResolution -> ResolutionResult
    
    Contains NO business logic.
    """
    
    @staticmethod
    def resolve(composition: RuntimeComposition) -> ResolutionResult:
        """
        Coordinates the resolution process and returns an immutable ResolutionResult.
        """
        # 1. Validate
        validation = ResolutionValidator.validate(composition)
        if not validation.is_valid:
            return ResolutionResult(
                success=False,
                errors=validation.errors,
                warnings=validation.warnings
            )
            
        try:
            # 2. Compute Ordering
            ordered_components, dependency_order = ResolutionAlgorithm.compute_ordering(composition)
            
            # 3. Build Statistics
            statistics = ResolutionStatisticsBuilder.build(composition, dependency_order)
            
            # 4. Generate Metadata
            metadata = ResolutionMetadataFactory.create()
            
            # 5. Generate ID
            res_id = ResolutionIdFactory.generate()
            
            # 6. Create Resolution
            resolution = RuntimeResolution(
                resolution_id=res_id,
                ordered_components=ordered_components,
                dependency_order=dependency_order,
                metadata=metadata,
                statistics=statistics,
                validation_result=validation
            )
            
            # 7. Create Result
            return ResolutionResult(
                success=True,
                resolution=resolution,
                errors=(),
                warnings=validation.warnings
            )
            
        except ResolutionCycleException as e:
            return ResolutionResult(
                success=False,
                errors=(str(e),),
                warnings=validation.warnings
            )
        except Exception as e:
            return ResolutionResult(
                success=False,
                errors=(f"Unexpected resolution error: {str(e)}",),
                warnings=validation.warnings
            )
