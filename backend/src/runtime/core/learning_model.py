from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any

from .observation_model import ObservationIdentity


class LearningCategory(str, Enum):
    """
    The category of Runtime knowledge.
    
    A simple classification. It does NOT contain behavior.
    """
    EXECUTION = "EXECUTION"
    RETRY = "RETRY"
    RESOURCE = "RESOURCE"
    PERFORMANCE = "PERFORMANCE"
    STABILITY = "STABILITY"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class LearningConfidence(str, Enum):
    """
    Confidence in learned knowledge.
    
    It remains classification only. It does NOT trigger behavior,
    recommend actions, drive optimization, or perform scoring.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass(frozen=True)
class LearningPattern:
    """
    One immutable Runtime learning pattern.
    
    It must NOT contain behavior. It remains immutable.
    """
    category: LearningCategory
    confidence: LearningConfidence
    description: str
    supporting_observations: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningSummary:
    """
    Immutable Runtime knowledge summary.
    
    It must NOT contain Optimization behavior, Prediction, 
    Recommendations, or Execution behavior.
    """
    summary: str
    pattern_count: int
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int


@dataclass(frozen=True)
class LearningResult:
    """
    The immutable outcome of Runtime learning.
    
    Produced by RuntimeLearning. Consumed by future RuntimeOptimization.
    
    Must NEVER contain Execution logic, Scheduling information, Retry behavior, 
    Recovery behavior, Observation behavior, Optimization behavior, 
    Prediction, Analytics, Recommendations, Monitoring, Telemetry, Metrics, 
    or Resource allocation.
    """
    learning_identity: str
    observation_identity: ObservationIdentity
    summary: LearningSummary
    patterns: List[LearningPattern] = field(default_factory=list)
    created_at: float = field(default_factory=float)
