from datetime import datetime
from .composition_metadata import CompositionMetadata

class CompositionMetadataFactory:
    """
    Factory for constructing Runtime Composition metadata.
    
    Responsibilities:
    - Create CompositionMetadata
    - Populate timestamps
    - Populate builder version
    - Populate schema version
    - Populate composition version
    """
    
    @staticmethod
    def create(builder_version: str = "1.0.0", schema_version: str = "1.0.0", composition_version: str = "1.0.0") -> CompositionMetadata:
        """
        Creates an immutable CompositionMetadata instance.
        """
        return CompositionMetadata(
            composition_version=composition_version,
            schema_version=schema_version,
            creation_timestamp=datetime.utcnow(),
            builder_version=builder_version
        )
