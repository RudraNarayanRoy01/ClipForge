from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


class RuntimeRecommendationState(Enum):
    """
    Represents the immutable lifecycle of a Runtime Recommendation.
    Lifecycle categorization only. No behavior.
    """
    INITIALIZED = "INITIALIZED"
    GENERATED = "GENERATED"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class RuntimeRecommendationCategory(Enum):
    """
    Represents qualitative recommendation categories.
    Categories only. No logic.
    """
    EXECUTION = "EXECUTION"
    RESOURCE = "RESOURCE"
    PROVIDER_CAPABILITY = "PROVIDER_CAPABILITY"
    MODEL_CAPABILITY = "MODEL_CAPABILITY"
    RECOVERY = "RECOVERY"
    PERFORMANCE = "PERFORMANCE"
    RELIABILITY = "RELIABILITY"
    GENERAL = "GENERAL"


class RuntimeRecommendationPriority(Enum):
    """
    Represents qualitative recommendation priority.
    Qualitative only. Never numeric. Never scoring.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    OPTIONAL = "OPTIONAL"


@dataclass(frozen=True)
class RuntimeRecommendationAlternative:
    """
    Represents immutable alternative recommendations.
    
    Permanently owns only:
    - alternative identifiers
    - alternative metadata
    - alternative descriptions
    - alternative categories
    - alternative priorities
    - immutable references
    
    Must NEVER own:
    - execution plans
    - routing logic
    - provider selection
    - scheduling
    - retry plans
    - optimization strategies
    - orchestration logic
    
    Alternatives remain passive advisory artifacts only.
    """
    alternative_id: str
    title: str
    description: str
    category: RuntimeRecommendationCategory
    priority: RuntimeRecommendationPriority
    references: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuntimeRecommendationRationale:
    """
    Represents immutable advisory rationale.
    
    Permanently owns only:
    - rationale identifiers
    - rationale summaries
    - immutable references
    - metadata
    
    Must NEVER perform:
    - reasoning
    - confidence calculation
    - evidence evaluation
    - recommendation ranking
    - recommendation generation algorithms
    
    It explains a recommendation. It never creates one.
    No evaluation. No inference.
    """
    rationale_id: str
    summary: str
    reasoning_references: List[str] = field(default_factory=list)
    confidence_references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeRecommendation:
    """
    Canonical immutable Runtime Recommendation artifact.
    Answers "What should the Runtime recommend?" based upon the completed pipeline.
    
    It provides advice, NEVER commands. It does NOT represent execution, workflow, orchestration,
    provider routing, policy enforcement, scheduling, retry strategy, or optimization.
    
    Provider Agnostic Design: MUST NEVER recommend specific providers, models, hardware, or implementations.
    Instead, references required capabilities, execution characteristics, or resource characteristics.
    
    Contains only immutable identifiers and metadata.
    Must NEVER embed downstream artifacts or models.
    Depends only upon upstream observation_id, decision_id, reasoning_id, and confidence_id.
    """
    recommendation_id: str
    recommendation_state: RuntimeRecommendationState
    recommendation_category: RuntimeRecommendationCategory
    recommendation_priority: RuntimeRecommendationPriority
    rationale_id: str
    observation_id: Optional[str] = None
    decision_id: Optional[str] = None
    reasoning_id: Optional[str] = None
    confidence_id: Optional[str] = None
    alternative_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeRecommendationInfo:
    """
    Canonical immutable metadata.
    Contains identifiers only.
    """
    recommendation_id: str
    recommendation_state: RuntimeRecommendationState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeRecommendationResult:
    """
    Immutable transport artifact.
    Returned by future Runtime Recommendation producers.
    Contains Recommendation info, summary, and validation.
    Behavior remains outside this bounded context.
    """
    recommendation_info: RuntimeRecommendationInfo
    recommendation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
