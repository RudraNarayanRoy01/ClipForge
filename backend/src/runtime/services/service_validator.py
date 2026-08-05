"""
Validates service descriptors and properties.
"""
from typing import Sequence
from .service_descriptor import ServiceDescriptor
from .service_exceptions import (
    DuplicateServiceException,
    InvalidServiceDescriptorException,
    IncompleteServiceCompositionException
)
from .runtime_service_composition import ValidationResult

class ServiceValidator:
    """Structural validator for service descriptors."""
    
    @staticmethod
    def validate_descriptors(descriptors: Sequence[ServiceDescriptor]) -> ValidationResult:
        errors = []
        warnings = []
        
        if not descriptors:
            warnings.append("Empty service composition.")
            
        seen_ids = set()
        for desc in descriptors:
            if not desc.service_id:
                errors.append("Missing service identifier.")
            elif desc.service_id in seen_ids:
                errors.append(f"Duplicate service identifier: {desc.service_id}")
            seen_ids.add(desc.service_id)
            
            if not desc.component_id:
                errors.append(f"Service {desc.service_id or 'UNKNOWN'} is missing component_id.")
            if not desc.service_type:
                errors.append(f"Service {desc.service_id or 'UNKNOWN'} is missing service_type.")
                
            for dep in desc.dependencies:
                if not isinstance(dep, str):
                    errors.append(f"Service {desc.service_id} has invalid dependency: {dep}")
                    
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings)
        )
        
    @staticmethod
    def assert_valid(descriptors: Sequence[ServiceDescriptor]) -> None:
        result = ServiceValidator.validate_descriptors(descriptors)
        if not result.is_valid:
            if any("Duplicate" in err for err in result.errors):
                raise DuplicateServiceException(", ".join(result.errors))
            if any("Missing" in err for err in result.errors):
                raise InvalidServiceDescriptorException(", ".join(result.errors))
            raise IncompleteServiceCompositionException(", ".join(result.errors))
