import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone

from src.domain.campaign_entities import Campaign
from src.knowledge.dtos import VideoKnowledge

class EvaluationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ERROR = "ERROR"

class RecommendationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RecommendationPriority(str, Enum):
    OPTIONAL = "OPTIONAL"
    RECOMMENDED = "RECOMMENDED"
    CRITICAL = "CRITICAL"

@dataclass(frozen=True)
class EvaluationId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class EvaluationMetadata:
    reasoning_version: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

@dataclass(frozen=True)
class EvaluationContext:
    campaign: Campaign
    video_knowledge: VideoKnowledge

@dataclass(frozen=True)
class RecommendationExplanation:
    reasoning: str
    key_factors: List[str] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class EvaluationSummary:
    overall_recommendation: str
    key_highlights: List[str] = field(default_factory=list)
    flagged_risks: List[str] = field(default_factory=list)

# Structural placeholders for future reasoning outputs
@dataclass(frozen=True)
class EligibilityResult:
    pass

@dataclass(frozen=True)
class CompatibilityResult:
    pass

@dataclass(frozen=True)
class SuitabilityResult:
    pass

@dataclass(frozen=True)
class RiskAssessment:
    pass

@dataclass(frozen=True)
class WorthItAssessment:
    pass

@dataclass(frozen=True)
class RecommendationResult:
    priority: RecommendationPriority
    confidence: RecommendationConfidence
    explanation: RecommendationExplanation

@dataclass(frozen=True)
class CampaignEvaluation:
    id: EvaluationId
    status: EvaluationStatus
    context: EvaluationContext
    metadata: EvaluationMetadata
    
    # Placeholders for future reasoning outputs
    eligibility: Optional[EligibilityResult] = None
    compatibility: Optional[CompatibilityResult] = None
    suitability: Optional[SuitabilityResult] = None
    risk: Optional[RiskAssessment] = None
    worth_it: Optional[WorthItAssessment] = None
    recommendation: Optional[RecommendationResult] = None
    summary: Optional[EvaluationSummary] = None
