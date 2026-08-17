from typing import Dict
from src.runtime.core.extension import IRuntimeExtensionPoint
from .workload_normalizer import WorkloadNormalizer, ExecutionWorkload

class NormalizerResolutionError(Exception):
    """Raised when no normalizer is registered for a capability."""
    pass

class WorkloadNormalizationExtensionPoint(IRuntimeExtensionPoint):
    """
    Extension point for capability domains to register their WorkloadNormalizers.
    Injected into RuntimeExecutionBoundary.
    """
    def __init__(self) -> None:
        self._normalizers: Dict[str, WorkloadNormalizer[ExecutionWorkload]] = {}
        
    def register_extension(self, extension: "IRuntimeExtension") -> None:
        """Required by IRuntimeExtensionPoint, though we might use a more specific method."""
        pass
        
    def register_normalizer(self, capability_id: str, normalizer: WorkloadNormalizer[ExecutionWorkload]) -> None:
        """Register a normalizer for a specific capability."""
        if capability_id in self._normalizers:
            raise ValueError(f"Normalizer already registered for capability '{capability_id}'")
        self._normalizers[capability_id] = normalizer
        
    def get_normalizer(self, capability_id: str) -> WorkloadNormalizer[ExecutionWorkload]:
        """Resolve a normalizer by capability identity."""
        if capability_id not in self._normalizers:
            raise NormalizerResolutionError(f"No normalizer registered for capability '{capability_id}'")
        return self._normalizers[capability_id]
