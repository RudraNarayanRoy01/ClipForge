import uuid
import time
from .resolution_metadata import ResolutionMetadata

class ResolutionMetadataFactory:
    """Factory for creating immutable ResolutionMetadata."""
    
    @staticmethod
    def create() -> ResolutionMetadata:
        """Create current resolution metadata without provider/execution awareness."""
        return ResolutionMetadata(
            schema_version="1.0.0",
            resolver_version="1.0.0",
            runtime_version="1.0.0",  # Usually injected, but hardcoded here for pure foundation
            timestamp=time.time(),
            resolution_uuid=str(uuid.uuid4())
        )

class ResolutionIdFactory:
    """Factory for generating resolution IDs."""
    
    @staticmethod
    def generate() -> str:
        return f"res-{uuid.uuid4().hex[:8]}"
