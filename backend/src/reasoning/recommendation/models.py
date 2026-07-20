import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional


class RecommendationConfidence(Enum):
    """
    Represents the confidence level of a generated recommendation.
    """
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


class RecommendationPriority(Enum):
    """
    Represents the priority or urgency of the recommendation.
    """
    CRITICAL = auto()
    HIGH = auto()
    NORMAL = auto()
    LOW = auto()


class SuggestedAction(Enum):
    """
    Represents standardized actions that can be suggested by the system.
    """
    PUBLISH = auto()
    REVIEW = auto()
    REJECT = auto()
    ARCHIVE = auto()
    ESCALATE = auto()


@dataclass(frozen=True)
class RecommendationRequest:
    """
    Represents an immutable application request to generate a recommendation.
    """
    target_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class RecommendationContext:
    """
    Represents the prepared, immutable context required to evaluate recommendations.
    Provides the environment in which the rules/engine will operate.
    """
    context_id: uuid.UUID = field(default_factory=uuid.uuid4)
    facts: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecommendationRuleMatch:
    """
    Represents the evaluation of a specific rule within the recommendation engine.
    """
    rule_id: uuid.UUID
    description: str
    is_matched: bool


@dataclass(frozen=True)
class RecommendationResult:
    """
    Represents the deterministic evaluation output of the recommendation engine.
    Focuses on what rules matched or what mathematical/logical outcomes were reached.
    """
    request_id: uuid.UUID
    is_successful: bool
    rule_matches: List[RecommendationRuleMatch] = field(default_factory=list)
    confidence: Optional[RecommendationConfidence] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class RecommendationReasoning:
    """
    Immutable representation of the explanation, risks, opportunities,
    assumptions, and supporting rationale behind a decision.
    """
    explanation: str
    opportunities: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    supporting_rationale: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecommendationDecision:
    """
    Represents the interpreted business outcome based on the result.
    It encapsulates the priority, whether the decision is actionable, and its reasoning.
    """
    primary_action: SuggestedAction
    priority: RecommendationPriority
    is_actionable: bool
    reasoning: RecommendationReasoning
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Recommendation:
    """
    The stable application-facing recommendation contract.
    Encapsulates the entire recommendation cycle, composing the request, context, result, and decision.
    """
    request: RecommendationRequest
    context: RecommendationContext
    result: RecommendationResult
    decision: RecommendationDecision
