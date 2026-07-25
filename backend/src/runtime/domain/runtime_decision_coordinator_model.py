from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

class RuntimeDecisionCoordinatorState(Enum):
    """
    Represents the immutable lifecycle of a Runtime Decision Coordinator.
    Lifecycle only. No behavior.
    """
    INITIALIZED = "INITIALIZED"
    COORDINATED = "COORDINATED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class RuntimeCoordinationStrategy(Enum):
    """
    Represents immutable coordination strategies.
    Strategies describe coordination only. Never execution.
    """
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    INDEPENDENT = "INDEPENDENT"
    GROUPED = "GROUPED"
    DEFERRED = "DEFERRED"


class RuntimeCoordinationPriority(Enum):
    """
    Represents qualitative coordination priority.
    Qualitative only. Never numeric. Never scoring.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    OPTIONAL = "OPTIONAL"


class RuntimeRecommendationRelationship(Enum):
    """
    Represents immutable relationships between recommendations.
    Relationship metadata only. No logic.
    """
    REQUIRES = "REQUIRES"
    SUPERSEDES = "SUPERSEDES"
    COMPLEMENTS = "COMPLEMENTS"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    OPTIONAL_WITH = "OPTIONAL_WITH"
    MUTUALLY_EXCLUSIVE = "MUTUALLY_EXCLUSIVE"


@dataclass(frozen=True)
class RuntimeRecommendationDependency:
    """
    Represents immutable dependency metadata.
    
    Permanently owns only:
    - dependency identifiers
    - recommendation identifiers
    - dependency metadata
    - relationship metadata
    
    Must NEVER perform:
    - dependency resolution
    - dependency validation
    - dependency scheduling
    - dependency execution
    - dependency graph traversal
    """
    dependency_id: str
    recommendation_id: str
    depends_on_recommendation_id: str
    relationship: RuntimeRecommendationRelationship
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeRecommendationConflict:
    """
    Represents immutable recommendation conflicts.
    
    Permanently owns only:
    - conflict identifiers
    - recommendation references
    - conflict descriptions
    - severity metadata
    
    Conflict artifacts NEVER perform:
    - conflict resolution
    - conflict prioritization
    - conflict arbitration
    - recommendation replacement
    - recommendation suppression
    """
    conflict_id: str
    recommendation_ids: List[str]
    description: str
    severity: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeDecisionCoordinator:
    """
    Canonical immutable coordination artifact.
    Answers "How should Runtime Recommendations be coordinated?"
    
    It performs coordination. It NEVER performs:
    - execution
    - provider selection
    - routing
    - retry
    - workflow execution
    - model loading
    - policy enforcement
    - hardware management
    - scheduling
    
    Provider Agnostic Design: MUST NEVER reference specific providers (e.g., Gemini, OpenAI, Ollama), 
    models, or hardware (e.g., CUDA, CPU, GPU).
    
    Contains only immutable identifiers. Never embeds Runtime domain objects like
    RuntimeObservation, RuntimeDecision, RuntimeReasoning, RuntimeConfidence, or RuntimeRecommendation.
    """
    coordinator_id: str
    state: RuntimeDecisionCoordinatorState
    coordination_strategy: RuntimeCoordinationStrategy
    coordination_priority: RuntimeCoordinationPriority
    recommendation_ids: List[str]
    relationship_ids: List[str] = field(default_factory=list)
    dependency_ids: List[str] = field(default_factory=list)
    conflict_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    observation_id: Optional[str] = None
    decision_id: Optional[str] = None
    reasoning_id: Optional[str] = None
    confidence_id: Optional[str] = None


@dataclass(frozen=True)
class RuntimeDecisionCoordinatorInfo:
    """
    Immutable metadata for Runtime Decision Coordinator.
    Contains identifiers only.
    """
    coordinator_id: str
    state: RuntimeDecisionCoordinatorState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeDecisionCoordinatorResult:
    """
    Immutable transport artifact.
    Returned by future Runtime Decision Coordinator producers.
    Contains Info, coordination summary, and validation.
    Behavior remains outside this bounded context.
    """
    coordinator_info: RuntimeDecisionCoordinatorInfo
    coordination_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
