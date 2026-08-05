from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class CompositionMetadata:
    """
    Metadata for a Runtime Composition.
    Observational only. No evaluation.
    """
    composition_version: str
    schema_version: str
    creation_timestamp: datetime
    builder_version: str
