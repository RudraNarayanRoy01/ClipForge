from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class RecommendationDecision(Enum):
    """
    The final deterministic decision synthesized from all assessments.
    """
    RECOMMEND = auto()
    DO_NOT_RECOMMEND = auto()
    NEEDS_HUMAN_REVIEW = auto()


class RecommendationConfidence(Enum):
    """
    Overall confidence in the synthesized recommendation.
    """
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


@dataclass(frozen=True)
class RecommendationReason:
    """
    A structured reason explaining part of the recommendation decision.
    Provides a stable contract for UI, analytics, and localization.
    """
    code: str
    description: str


@dataclass(frozen=True)
class RecommendationRationale:
    """
    The structured rationale supporting the final recommendation.
    Avoids free-form text by aggregating typed reasons.
    """
    reasons: List[RecommendationReason] = field(default_factory=list)


@dataclass(frozen=True)
class Recommendation:
    """
    The final immutable recommendation output by the Recommendation Synthesis Engine.
    """
    decision: RecommendationDecision
    confidence: RecommendationConfidence
    rationale: RecommendationRationale
