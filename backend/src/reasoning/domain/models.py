import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation

class EvaluationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ERROR = "ERROR"

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
    document: CampaignEntityDocument

@dataclass(frozen=True)
class CampaignEvaluation:
    id: EvaluationId
    status: EvaluationStatus
    context: EvaluationContext
    metadata: EvaluationMetadata
    
    eligibility: Optional[EligibilityAssessment] = None
    worth_it: Optional[WorthItAssessment] = None
    recommendation: Optional[Recommendation] = None
