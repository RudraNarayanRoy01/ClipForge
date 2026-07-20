from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Mapping, Optional, Tuple, Union
from uuid import UUID

from src.editing.domain.models.items import TimelineItem
from src.editing.domain.value_objects.time import Time, TimeRange


class TimelineOperationType(Enum):
    """
    Canonical operation types for timeline manipulation.
    """
    INSERT = auto()
    REMOVE = auto()
    MOVE = auto()
    TRIM = auto()
    SPLIT = auto()
    MERGE = auto()
    OVERLAY = auto()
    SUBTITLE = auto()
    TRANSITION = auto()


@dataclass(frozen=True)
class TimelineOperation:
    """
    An immutable representation of a timeline intent.
    Translates editorial decisions into backend-independent timeline operations.
    """
    id: UUID
    operation_type: TimelineOperationType
    
    # The affected timeline element, represented as a rich domain abstraction
    target: Optional[TimelineItem] = None
    
    # Explicit representation of position (insertion, destination, boundary)
    position: Optional[Union[Time, TimeRange]] = None
    
    # Flexible, implementation-independent parameters
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelineTransformationResult:
    """
    The canonical output of the transformation layer.
    Contains immutable timeline operations and can be extended with metadata
    (warnings, statistics, etc.) without changing the public API.
    """
    operations: Tuple[TimelineOperation, ...] = field(default_factory=tuple)
