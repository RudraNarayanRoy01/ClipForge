from dataclasses import dataclass, field
from typing import Any, Mapping, Optional
from uuid import UUID

from src.editing.domain.enums.decisions import EditOperation, EditTarget
from src.editing.domain.value_objects.decision_metadata import DecisionMetadata
from src.editing.domain.value_objects.time import TimeRange

@dataclass(frozen=True)
class EditDecision:
    """
    Represents one editorial decision.
    Models editorial intent rather than implementation details.
    """
    id: UUID
    operation: EditOperation
    target: EditTarget
    metadata: DecisionMetadata
    
    # Optional context for the decision
    target_id: Optional[UUID] = None
    time_range: Optional[TimeRange] = None
    
    # Generic parameters for the specific operation (e.g., speed factor, zoom level)
    # Using Mapping to enforce immutability over dict
    parameters: Mapping[str, Any] = field(default_factory=dict)
