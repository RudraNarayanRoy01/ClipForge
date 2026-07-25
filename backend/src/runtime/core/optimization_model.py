from dataclasses import dataclass, field
from enum import Enum
from typing import List


class OptimizationCategory(str, Enum):
    """
    The category of Runtime optimization.
    
    A simple classification. It does NOT contain behavior.
    """
    EXECUTION = "EXECUTION"
    RETRY = "RETRY"
    RESOURCE = "RESOURCE"
    PERFORMANCE = "PERFORMANCE"
    STABILITY = "STABILITY"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class OptimizationPriority(str, Enum):
    """
    Priority of an optimization decision.
    
    It remains classification only. It does NOT trigger execution,
    apply optimization, allocate resources, or perform scheduling.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class OptimizationDecision:
    """
    One immutable Runtime optimization decision.
    
    Represents an optimization opportunity, NOT an executable instruction.
    (e.g., "Reduce GPU memory pressure", NOT "Set GPU memory limit to 4 GB").
    
    It must NOT contain behavior. It remains passive and immutable.
    """
    category: OptimizationCategory
    priority: OptimizationPriority
    description: str
    supporting_patterns: List[str] = field(default_factory=list)
    expected_benefit: str = "Unknown benefit"


@dataclass(frozen=True)
class OptimizationSummary:
    """
    Immutable Runtime optimization knowledge summary.
    
    It must remain immutable and must NOT contain Execution behavior,
    Learning behavior, Resource allocation, Prediction, or Recommendations.
    """
    summary: str
    decision_count: int
    critical_count: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int


@dataclass(frozen=True)
class OptimizationResult:
    """
    The immutable outcome of Runtime optimization.
    
    Stores Runtime optimization knowledge only.
    It must NEVER contain execution logic, scheduling information, retry behavior,
    observation behavior, learning behavior, resource allocation, applied optimizations,
    prediction, analytics, recommendations, monitoring, telemetry, or metrics.
    
    It remains a pure immutable artifact with no actions, commands, or callbacks.
    """
    optimization_identity: str
    learning_identity: str
    summary: OptimizationSummary
    decisions: List[OptimizationDecision] = field(default_factory=list)
    created_at: float = field(default_factory=float)
