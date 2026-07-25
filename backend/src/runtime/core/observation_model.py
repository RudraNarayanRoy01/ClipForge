from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from .retry_model import RetryIdentity


class ObservationCategory(str, Enum):
    """
    The category of an observation.
    
    A simple classification. It does NOT imply severity, trigger behavior, 
    recommend actions, or drive optimization.
    """
    EXECUTION = "EXECUTION"
    LIFECYCLE = "LIFECYCLE"
    RETRY = "RETRY"
    RESOURCE = "RESOURCE"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class ObservationSeverity(str, Enum):
    """
    The severity of an observation.
    
    A simple classification of impact. It does NOT contain behavior.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ObservationSummary:
    """
    Immutable observation summary information.
    
    Contains descriptive counts and a summary string. 
    It must NOT contain Learning behavior, Optimization behavior, 
    Recommendations, or Execution behavior.
    """
    summary: str
    observation_count: int
    warning_count: int
    error_count: int
    critical_count: int


@dataclass(frozen=True)
class ObservationRecord:
    """
    One immutable Runtime observation.
    
    Purely descriptive. It represents "What Runtime observed".
    It must NOT interpret observations, recommend actions, learn patterns, 
    calculate optimizations, generate scores, or assign priorities.
    """
    category: ObservationCategory
    severity: ObservationSeverity
    message: str
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObservationIdentity:
    """
    The permanent identity of a Runtime Observation.
    
    A pure identity value object.
    """
    observation_id: str
    created_at: float


@dataclass(frozen=True)
class ObservationResult:
    """
    The immutable outcome of Runtime observation.
    
    Represents "What Runtime observed".
    Produced by RuntimeObservation. Consumed by future Learning components.
    
    Must NEVER contain Execution logic, Scheduling information, 
    Retry behavior, Recovery behavior, Learning behavior, 
    Optimization behavior, Analytics, Recommendations, Telemetry, 
    Metrics, Monitoring, or Resource allocation.
    """
    observation_identity: ObservationIdentity
    retry_identity: RetryIdentity
    summary: ObservationSummary
    records: List[ObservationRecord] = field(default_factory=list)
    created_at: float = field(default_factory=float)
