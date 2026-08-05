"""
Builder orchestration for Runtime Service Composition.
"""
from typing import Sequence
from .service_descriptor import ServiceDescriptor
from .runtime_service_composition import RuntimeServiceComposition
from .service_result import ServiceResult
from .service_validator import ServiceValidator
from .service_statistics_builder import ServiceStatisticsBuilder
from .service_snapshot_factory import ServiceSnapshotFactory
from .service_id_factory import ServiceIdFactory
from .service_metadata_factory import ServiceMetadataFactory
from .runtime_service_factory import RuntimeServiceFactory
from .service_exceptions import ServiceBuildException, ServiceValidationException

class RuntimeServiceBuilder:
    """Thin orchestration layer for Service Composition."""
    
    def __init__(self):
        self._validator = ServiceValidator()
        self._stats_builder = ServiceStatisticsBuilder()
        self._snapshot_factory = ServiceSnapshotFactory()
        self._id_factory = ServiceIdFactory()
        self._metadata_factory = ServiceMetadataFactory()
        self._service_factory = RuntimeServiceFactory()

    def build(self, descriptors: Sequence[ServiceDescriptor]) -> ServiceResult:
        try:
            # 1. Validation
            validation_result = self._validator.validate_descriptors(descriptors)
            if not validation_result.is_valid:
                return ServiceResult(
                    success=False,
                    errors=validation_result.errors,
                    warnings=validation_result.warnings
                )

            # 2. Factories (Convert descriptors to services)
            services = tuple(self._service_factory.create(d) for d in descriptors)
            
            # 3. Identifiers & Metadata
            composition_id = self._id_factory.create_id()
            metadata = self._metadata_factory.create()
            
            # 4. Statistics Builder
            statistics = self._stats_builder.build(services)
            
            # 5. Snapshot Factory
            snapshot = self._snapshot_factory.create(
                composition_id=composition_id,
                services=services,
                metadata=metadata,
                statistics=statistics
            )
            
            # 6. Result
            composition = RuntimeServiceComposition(
                composition_id=composition_id,
                services=services,
                metadata=metadata,
                statistics=statistics,
                validation_result=validation_result,
                snapshot=snapshot
            )
            
            return ServiceResult(
                success=True,
                service_composition=composition,
                errors=(),
                warnings=validation_result.warnings
            )
            
        except ServiceValidationException as e:
            return ServiceResult(
                success=False,
                errors=(str(e),),
            )
        except Exception as e:
            raise ServiceBuildException(f"Failed to build service composition: {str(e)}") from e
