"""
Factory for Runtime Service.
"""
from .runtime_service import RuntimeService
from .service_descriptor import ServiceDescriptor

class RuntimeServiceFactory:
    """Creates RuntimeService from ServiceDescriptor."""
    
    @staticmethod
    def create(descriptor: ServiceDescriptor) -> RuntimeService:
        return RuntimeService(
            service_id=descriptor.service_id,
            component_id=descriptor.component_id,
            service_name=descriptor.service_name,
            service_type=descriptor.service_type,
            lifetime=descriptor.lifetime,
            dependencies=descriptor.dependencies,
            tags=descriptor.tags,
            metadata=descriptor.metadata
        )
